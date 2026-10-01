import os
import json
import re
from dotenv import load_dotenv
from services.analyzer import analyze_resume_locally, ROLE_PROFILES

load_dotenv()

def get_gemini_client():
    """Retrieve Gemini client if API key is configured."""
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key or api_key == "your_gemini_api_key_here":
        return None
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        return client
    except Exception as e:
        print(f"Warning: Could not initialize Gemini client: {e}")
        return None

def analyze_resume_ai(parsed_resume, target_role="Frontend Developer", job_description=""):
    """
    Orchestrate resume analysis. Uses Gemini API if configured;
    falls back cleanly to deterministic local analyzer if key is missing or on error.
    """
    client = get_gemini_client()
    if not client:
        # Graceful fallback to deterministic local analyzer
        result = analyze_resume_locally(parsed_resume, target_role, job_description)
        result["engine"] = "deterministic_local"
        result["ai_status"] = "API key not provided. Deterministic local engine active."
        return result

    # Prepare prompt for Gemini
    role_benchmarks = ROLE_PROFILES.get(target_role, ROLE_PROFILES["Frontend Developer"])
    
    prompt = f"""
You are an expert ATS and Technical Resume Evaluator.
Analyze the following candidate resume for the target role: "{target_role}".

TARGET ROLE CONTEXT:
- Core required skills: {', '.join(role_benchmarks['core_skills'])}
- Recommended skills: {', '.join(role_benchmarks['recommended_skills'])}
- Role description: {role_benchmarks['description']}

OPTIONAL JOB DESCRIPTION PROVIDED BY USER:
{job_description or "None provided. Use standard role benchmarks."}

CANDIDATE EXTRACTED RESUME DATA:
- Name: {parsed_resume.get('name')}
- Email: {parsed_resume.get('email')}
- Phone: {parsed_resume.get('phone')}
- GitHub: {parsed_resume.get('github')}
- LinkedIn: {parsed_resume.get('linkedin')}
- Summary: {parsed_resume.get('summary')}
- Claimed Skills: {json.dumps([s['name'] if isinstance(s, dict) else s for s in parsed_resume.get('skills', [])])}
- Projects: {json.dumps(parsed_resume.get('projects', []))}
- Education: {json.dumps(parsed_resume.get('education', []))}
- Experience: {json.dumps(parsed_resume.get('experience', []))}
- Certifications: {json.dumps(parsed_resume.get('certifications', []))}
- Achievements: {json.dumps(parsed_resume.get('achievements', []))}

CRITICAL RULES:
1. NEVER fabricate or invent fake evidence, projects, certifications, metrics, or work experience.
2. For EVIDENCE MAPPING: Examine every claimed skill. If it appears in a candidate project, certification, or experience, state the exact project/cert name as Evidence. If NOT found in any project, cert, or experience, strictly mark evidence as "Not verified" with status "Not verified".
3. For IMPROVEMENTS: Suggest real, actionable improvements. Only suggest measurable metrics when candidate provides numbers; do not invent fake stats (e.g. do not invent "improved latency by 45%").
4. Scores MUST be realistic integers between 0 and 100 based strictly on actual candidate qualifications.

Return ONLY a valid JSON object with EXACTLY this structure:
{{
  "ats_score": 75,
  "skill_match": 70,
  "role_alignment": 75,
  "structure_score": 80,
  "evidence_strength": 65,
  "matched_skills": [
    {{"name": "SkillName", "category": "Category", "reason": "Why it matters for this role"}}
  ],
  "missing_skills": [
    {{"name": "SkillName", "category": "Category", "reason": "Why it is needed for this role"}}
  ],
  "weak_skills": [
    {{"name": "SkillName", "reason": "Why it is unverified or lacks evidence"}}
  ],
  "evidence_map": [
    {{"skill": "SkillName", "verified": true, "status": "Verified", "evidence": "Project Name (Project)", "details": "Snippet from project"}}
  ],
  "improvements": [
    {{"category": "Category (ATS/Skills/Projects/Education/Role alignment/Missing evidence)", "title": "Headline", "recommendation": "Detailed advice", "before": "Exact text or state from resume", "suggested": "Improved wording"}}
  ]
}}
"""

    try:
        # Call Gemini model
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        text_resp = response.text.strip()
        
        # Clean potential markdown backticks
        if text_resp.startswith("```json"):
            text_resp = text_resp[7:]
        elif text_resp.startswith("```"):
            text_resp = text_resp[3:]
        if text_resp.endswith("```"):
            text_resp = text_resp[:-3]
        text_resp = text_resp.strip()

        data = json.loads(text_resp)
        data["engine"] = "gemini-2.5-flash"
        data["ai_status"] = "Evaluated with Gemini AI API"
        data["target_role"] = target_role
        return data
    except Exception as e:
        print(f"Gemini API analysis encountered an issue: {e}. Falling back to deterministic local analyzer.")
        local_result = analyze_resume_locally(parsed_resume, target_role, job_description)
        local_result["engine"] = "deterministic_local"
        local_result["ai_status"] = f"Local engine used (Gemini fallback: {str(e)[:60]})"
        return local_result

def generate_role_summary_ai(candidate_data, target_role):
    """
    Generate an ATS-friendly, role-aligned professional summary based on verified facts.
    """
    client = get_gemini_client()
    skills_list = [s['name'] if isinstance(s, dict) else s for s in candidate_data.get('skills', [])]
    projects_list = [p.get('title', '') for p in candidate_data.get('projects', [])]
    
    if client:
        try:
            prompt = f"""
Write a concise, professional 3-sentence ATS resume summary for candidate '{candidate_data.get('name', 'Candidate')}' targeting the role: '{target_role}'.
Base the summary ONLY on their verified skills ({', '.join(skills_list[:6])}) and projects ({', '.join(projects_list[:3])}).
DO NOT invent companies, metrics, or unmentioned skills.
Return ONLY the text of the summary.
"""
            resp = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            summary = resp.text.strip().replace('"', '')
            if summary:
                return summary
        except Exception as e:
            print(f"Gemini summary generation error: {e}")

    # Deterministic fallback summary
    top_skills = ", ".join(skills_list[:4]) if skills_list else "modern software technologies"
    top_proj = projects_list[0] if projects_list else "technical projects"
    return f"Motivated software candidate with hands-on technical foundation in {top_skills}. Proven experience delivering practical applications including {top_proj}, with a strong commitment to clean code, continuous learning, and scalable solutions for {target_role} opportunities."
def generate_resume_doctor(parsed_resume, target_role="Frontend Developer", job_description=""):
    """
    AI Resume Doctor.
    Analyzes the candidate's actual resume and provides personalized
    weaknesses, strengths, and improvement suggestions.
    """

    client = get_gemini_client()

    if not client:
        return {
            "success": False,
            "error": "Gemini API key is not configured.",
            "engine": "none"
        }

    skills = [
        s["name"] if isinstance(s, dict) else s
        for s in parsed_resume.get("skills", [])
    ]

    resume_data = {
        "name": parsed_resume.get("name"),
        "summary": parsed_resume.get("summary"),
        "skills": skills,
        "projects": parsed_resume.get("projects", []),
        "experience": parsed_resume.get("experience", []),
        "education": parsed_resume.get("education", []),
        "certifications": parsed_resume.get("certifications", []),
        "achievements": parsed_resume.get("achievements", [])
    }

    prompt = f"""
You are an expert AI Resume Doctor and professional resume reviewer.

Analyze the candidate's ACTUAL resume for the target role:
{target_role}

OPTIONAL JOB DESCRIPTION:
{job_description or "No job description provided."}

CANDIDATE RESUME:
{json.dumps(resume_data, indent=2)}

Your task is to deeply analyze THIS candidate's resume.

IMPORTANT RULES:

1. Do NOT give generic advice.
2. Every weakness must be based on something actually present or missing in this resume.
3. Do NOT invent experience, skills, achievements, projects, companies, certifications, numbers or metrics.
4. If a section is missing, explicitly identify that section as missing.
5. Improved examples must use ONLY information already present in the resume.
6. Do not invent measurable achievements.
7. Distinguish between:
   - Existing evidence
   - Missing information
   - Recommended improvement
8. Analyze the entire resume, not only the skills section.
9. Consider the target role when identifying gaps.
10. Return ONLY valid JSON.

Evaluate:

- Professional summary
- Skills
- Projects
- Experience
- Education
- Certifications
- Achievements
- ATS keyword alignment
- Evidence of technical skills
- Overall clarity
- Role alignment

Return EXACTLY this JSON structure:

{{
    "health_score": 0,

    "overall_summary": "Personalized explanation of the current resume condition.",

    "strengths": [
        {{
            "section": "Projects",
            "point": "Specific strength found in this resume",
            "evidence": "Actual evidence from the resume"
        }}
    ],

    "issues": [
        {{
            "section": "Summary",
            "severity": "High",
            "problem": "Specific problem found",
            "why_it_matters": "Why this matters for the target role",
            "recommendation": "Specific improvement",
            "before": "Existing resume content or Missing",
            "suggested": "Improved version using only verified information"
        }}
    ],

    "missing_information": [
        {{
            "section": "Projects",
            "item": "Specific missing information",
            "reason": "Why this would improve the resume"
        }}
    ],

    "priority_improvements": [
        "Most important improvement",
        "Second important improvement",
        "Third important improvement"
    ],

    "role_alignment": {{
        "target_role": "{target_role}",
        "alignment_score": 0,
        "matched_areas": [],
        "gap_areas": []
    }}
}}
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        text_resp = response.text.strip()

        if text_resp.startswith("```json"):
            text_resp = text_resp[7:]

        elif text_resp.startswith("```"):
            text_resp = text_resp[3:]

        if text_resp.endswith("```"):
            text_resp = text_resp[:-3]

        text_resp = text_resp.strip()

        result = json.loads(text_resp)

        result["success"] = True
        result["engine"] = "gemini-2.5-flash"
        result["ai_status"] = "Resume analyzed using Gemini AI"
        result["target_role"] = target_role

        return result

    except Exception as e:
        print(f"Resume Doctor AI error: {e}")

        return {
            "success": False,
            "error": f"AI Resume Doctor failed: {str(e)}",
            "engine": "gemini-2.5-flash"
        }