import os
import io
import json
import unittest
import sys

# Ensure root directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from database.database import init_db, get_db, insert_resume, get_resume
from services.resume_parser import parse_resume, extract_contact_info, extract_skills_from_text
from services.analyzer import analyze_resume_locally, build_evidence_map
from services.ai_service import analyze_resume_ai
from services.resume_generator import generate_role_tailored_resume
from services.pdf_export import generate_pdf_resume

class TestResumeAnalyzer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        init_db()

    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_database_initialization(self):
        """Verify all required SQLite tables are created."""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row['name'] for row in cursor.fetchall()]
        conn.close()

        required = ['users', 'resumes', 'skills', 'projects', 'certifications', 'resume_versions', 'job_descriptions', 'analysis_results']
        for tbl in required:
            self.assertIn(tbl, tables, f"Missing table: {tbl}")

    def test_contact_extraction(self):
        """Test extraction of candidate email, phone, links, and name."""
        text = "Alex Kumar\nalex@example.com | +1 (555) 234-5678 | github.com/alexkumar-dev | linkedin.com/in/alexkumar-dev"
        contact = extract_contact_info(text)
        self.assertEqual(contact['name'], 'Alex Kumar')
        self.assertEqual(contact['email'], 'alex@example.com')
        self.assertIn('555', contact['phone'])
        self.assertIn('github.com/alexkumar-dev', contact['github'])
        self.assertIn('linkedin.com/in/alexkumar-dev', contact['linkedin'])

    def test_resume_parser_with_sample_text(self):
        """Test resume parsing from text string."""
        sample_text = """Alex Kumar
alex.kumar@example.com | +1 (555) 234-5678 | github.com/alexkumar-dev

SUMMARY
Motivated Computer Science student specializing in frontend web engineering.

EDUCATION
Bachelor of Technology in Computer Science
Apex Institute of Technology 2024 GPA: 3.8

SKILLS
HTML, CSS, JavaScript, React, Python, Machine Learning, Git, Node.js

PROJECTS
Movie Success Prediction System | Python, Machine Learning
Engineered predictive model using Python and Scikit-Learn to forecast film revenue.

Student Portfolio Portal | HTML, CSS, JavaScript
Built responsive student portal for tracking campus events.

CERTIFICATIONS
Meta Front-End Developer Certificate - Coursera
"""
        parsed = parse_resume(sample_text, is_raw_text=True)
        self.assertEqual(parsed['name'], 'Alex Kumar')
        self.assertEqual(parsed['email'], 'alex.kumar@example.com')
        self.assertTrue(len(parsed['skills']) >= 5)
        self.assertTrue(len(parsed['projects']) >= 2)

    def test_parse_sample_pdf_and_docx(self):
        """Verify parser can ingest real sample PDF and DOCX files."""
        pdf_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sample_data', 'sample_resume_alex_kumar.pdf')
        docx_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sample_data', 'sample_resume_alex_kumar.docx')

        if os.path.exists(pdf_path):
            parsed_pdf = parse_resume(pdf_path)
            self.assertTrue(len(parsed_pdf['skills']) > 0)
            self.assertTrue(len(parsed_pdf['projects']) > 0)

        if os.path.exists(docx_path):
            parsed_docx = parse_resume(docx_path)
            self.assertTrue(len(parsed_docx['skills']) > 0)
            self.assertTrue(len(parsed_docx['projects']) > 0)

    def test_evidence_mapping_strict_rules(self):
        """
        Verify Claim -> Evidence mapping:
        - Python maps to 'Movie Success Prediction System'
        - HTML/CSS maps to 'Student Portfolio'
        - Node.js (not used in projects) maps to 'Not verified'
        """
        candidate = {
            "skills": [{"name": "Python"}, {"name": "HTML"}, {"name": "Node.js"}],
            "projects": [
                {"title": "Movie Success Prediction System", "technologies": "Python", "description": "Built regression model using Python."},
                {"title": "Student Portfolio", "technologies": "HTML, CSS", "description": "Created accessible website."}
            ],
            "certifications": [],
            "experience": []
        }
        evidence_map = build_evidence_map(candidate["skills"], candidate["projects"], candidate["certifications"], candidate["experience"])
        
        py_evidence = next(e for e in evidence_map if e["skill"] == "Python")
        html_evidence = next(e for e in evidence_map if e["skill"] == "HTML")
        node_evidence = next(e for e in evidence_map if e["skill"] == "Node.js")

        self.assertTrue(py_evidence["verified"])
        self.assertIn("Movie Success Prediction", py_evidence["evidence"])

        self.assertTrue(html_evidence["verified"])
        self.assertIn("Student Portfolio", html_evidence["evidence"])

        # Node.js MUST be unverified!
        self.assertFalse(node_evidence["verified"])
        self.assertEqual(node_evidence["evidence"], "Not verified")

    def test_deterministic_analyzer_scores(self):
        """Verify scores, matched skills, missing skills, and improvement generation."""
        candidate = {
            "name": "Alex Kumar",
            "email": "alex@example.com",
            "phone": "+1 (555) 234-5678",
            "github": "github.com/alexkumar",
            "skills": [{"name": "HTML"}, {"name": "CSS"}, {"name": "JavaScript"}, {"name": "Python"}, {"name": "Node.js"}],
            "projects": [
                {"title": "Student Portfolio Website", "technologies": "HTML, CSS, JavaScript", "description": "Built responsive portfolio site."}
            ],
            "education": [{"degree": "BS Computer Science", "institution": "Apex Tech", "year": "2024"}],
            "certifications": [],
            "experience": []
        }

        # Analyze for Frontend Developer
        analysis = analyze_resume_locally(candidate, "Frontend Developer")
        self.assertIn('ats_score', analysis)
        self.assertIn('skill_match', analysis)
        self.assertIn('role_alignment', analysis)
        self.assertIn('evidence_strength', analysis)
        self.assertTrue(0 <= analysis['ats_score'] <= 100)
        self.assertTrue(len(analysis['matched_skills']) > 0)
        self.assertTrue(len(analysis['missing_skills']) > 0)
        self.assertTrue(len(analysis['improvements']) > 0)

    def test_ai_service_fallback(self):
        """Verify AI service falls back to local analyzer gracefully when key is missing."""
        candidate = {
            "name": "Jane Candidate",
            "email": "jane@example.com",
            "phone": "555-0100",
            "skills": [{"name": "Python"}]
        }
        result = analyze_resume_ai(candidate, "AI/ML Engineer")
        self.assertIn('ats_score', result)
        self.assertIn('matched_skills', result)
        self.assertIn('evidence_map', result)

    def test_pdf_generation(self):
        """Test reportlab PDF export produces non-empty file."""
        test_payload = {
            "contact": {"name": "Test Candidate", "email": "test@example.com", "phone": "555-1234"},
            "summary": "Software engineer with solid background in testing.",
            "skills": {"Languages": ["Python", "SQL"]},
            "projects": [{"title": "Test Project", "technologies": "Python", "description": "Built test automation system."}],
            "education": [{"degree": "BS CS", "institution": "State Univ", "year": "2025"}]
        }
        output_file = os.path.join(os.path.dirname(__file__), 'test_out.pdf')
        generate_pdf_resume(test_payload, output_file)
        self.assertTrue(os.path.exists(output_file))
        self.assertTrue(os.path.getsize(output_file) > 500)
        if os.path.exists(output_file):
            os.remove(output_file)

    # ---------------- API Endpoint Tests ----------------

    def test_api_pages(self):
        """Test that all front-end HTML pages return 200 OK."""
        pages = ['/', '/upload', '/analyze', '/builder', '/preview', '/versions']
        for p in pages:
            res = self.client.get(p)
            self.assertEqual(res.status_code, 200, f"Page {p} returned status {res.status_code}")

    def test_api_load_sample(self):
        """Test 1-click demo resume loading endpoint."""
        res = self.client.post('/api/load-sample')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertIn('resume_id', data)
        self.assertIn('parsed_data', data)

    def test_api_upload_resume_text(self):
        """Test upload API with raw text."""
        res = self.client.post('/api/upload-resume', data={'raw_text': 'John Doe\njohn@example.com\n555-1111\nSKILLS: Python, SQL'})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertIn('resume_id', data)

    def test_api_upload_pdf_file(self):
        """Test upload API with physical PDF file."""
        pdf_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sample_data', 'sample_resume_alex_kumar.pdf')
        with open(pdf_path, 'rb') as f:
            res = self.client.post('/api/upload-resume', data={
                'file': (io.BytesIO(f.read()), 'test_upload.pdf')
            }, content_type='multipart/form-data')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['parsed_data']['name'], 'ALEX KUMAR')

    def test_api_upload_docx_file(self):
        """Test upload API with physical DOCX file."""
        docx_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sample_data', 'sample_resume_alex_kumar.docx')
        with open(docx_path, 'rb') as f:
            res = self.client.post('/api/upload-resume', data={
                'file': (io.BytesIO(f.read()), 'test_upload.docx')
            }, content_type='multipart/form-data')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['parsed_data']['name'], 'Alex Kumar')

    def test_api_analyze_resume(self):
        """Test analysis API for both Frontend Developer and AI/ML Engineer."""
        # First load sample
        load_res = self.client.post('/api/load-sample')
        resume_id = load_res.get_json()['resume_id']

        # 1. Analyze for Frontend Developer
        fe_res = self.client.post('/api/analyze-resume', json={
            'resume_id': resume_id,
            'target_role': 'Frontend Developer'
        })
        self.assertEqual(fe_res.status_code, 200)
        fe_data = fe_res.get_json()
        self.assertTrue(fe_data['success'])
        self.assertIn('ats_score', fe_data['analysis'])
        self.assertIn('evidence_map', fe_data['analysis'])

        # 2. Analyze for AI/ML Engineer
        aiml_res = self.client.post('/api/analyze-resume', json={
            'resume_id': resume_id,
            'target_role': 'AI/ML Engineer'
        })
        self.assertEqual(aiml_res.status_code, 200)
        aiml_data = aiml_res.get_json()
        self.assertTrue(aiml_data['success'])

    def test_api_generate_and_save_versions(self):
        """Test role-specific generation, version creation, and export."""
        load_res = self.client.post('/api/load-sample')
        resume_id = load_res.get_json()['resume_id']

        # Generate role resume
        gen_res = self.client.post('/api/generate-resume', json={
            'resume_id': resume_id,
            'target_role': 'Frontend Developer'
        })
        self.assertEqual(gen_res.status_code, 200)
        role_resume = gen_res.get_json()['role_resume']

        # Save Version 1: Frontend Developer
        v1_res = self.client.post('/api/create-version', json={
            'resume_id': resume_id,
            'version_name': 'Version 1: Frontend Developer',
            'target_role': 'Frontend Developer',
            'formatted_resume': role_resume,
            'ats_score': 82
        })
        self.assertEqual(v1_res.status_code, 200)

        # Save Version 2: AI/ML Developer
        v2_res = self.client.post('/api/create-version', json={
            'resume_id': resume_id,
            'version_name': 'Version 2: AI/ML Developer',
            'target_role': 'AI/ML Engineer',
            'formatted_resume': role_resume,
            'ats_score': 79
        })
        self.assertEqual(v2_res.status_code, 200)

        # Retrieve versions
        list_res = self.client.get(f'/api/versions/{resume_id}')
        self.assertEqual(list_res.status_code, 200)
        versions = list_res.get_json()['versions']
        self.assertTrue(len(versions) >= 2)

        # Export PDF
        export_res = self.client.get(f'/api/export/{resume_id}?role=Frontend+Developer')
        self.assertEqual(export_res.status_code, 200)
        self.assertEqual(export_res.mimetype, 'application/pdf')
        export_res.close()

if __name__ == '__main__':
    unittest.main()
