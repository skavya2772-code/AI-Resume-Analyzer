# SkillAlign AI: AI Resume Analyzer & Skill-Based Resume Builder

> **A Complete Working Hackathon Prototype** built for students and early-career software engineers.
> Evaluates resumes with strict **Claim &rarr; Evidence** auditing, prevents hallucinated metrics, tailors ATS resumes for specific engineering roles, and exports standardized PDFs.

---

## Table of Contents
1. [Problem Statement](#problem-statement)
2. [The Solution](#the-solution)
3. [Key Features](#key-features)
4. [Architecture & Workflow](#architecture--workflow)
5. [Tech Stack](#tech-stack)
6. [Database Schema (SQLite)](#database-schema-sqlite)
7. [AI & Fallback Engine Strategy](#ai--fallback-engine-strategy)
8. [Installation & Setup](#installation--setup)
9. [Environment Variables](#environment-variables)
10. [Running the Application](#running-the-application)
11. [Hackathon Demo Flow (Step-by-Step)](#hackathon-demo-flow-step-by-step)
12. [API Documentation](#api-documentation)
13. [Security & Robustness](#security--robustness)
14. [Future Improvements](#future-improvements)

---

## Problem Statement

College students and early-career candidates often circulate **generic resumes** packed with lists of buzzword technologies. This creates major hurdles:
- **Disconnect from Evidence:** Students claim skills (e.g. *Machine Learning*, *React*, *Node.js*) without substantiating them through projects, certifications, or coursework.
- **ATS Filtering Failures:** Automated Applicant Tracking Systems (ATS) reject resumes lacking standardized formatting, clear contact hierarchies, or role-relevant keywords.
- **Role Misalignment:** A single resume is submitted to wildly different positions (e.g., *Frontend Developer* vs. *AI/ML Engineer*), causing low callback rates.
- **AI Hallucinations in Existing Tools:** Many AI builders invent fake metrics (e.g., *"increased revenue by 48%"*) or fabricate nonexistent corporate experience, creating reputational risk for students.

---

## The Solution

**SkillAlign AI** is an end-to-end, evidence-grounded web application:
1. **Parses Real Resumes:** Ingests PDF, DOCX, or text without executing untrusted binaries.
2. **Performs Strict Evidence Auditing:** Maps every claimed skill to verifiable project descriptions, certifications, or internships. If no evidence exists, it is explicitly flagged as **`Not verified`**.
3. **Dual Analysis Engine:** Leverages the official **Google Gemini API** (`gemini-2.5-flash`) with a deterministic, local offline engine that ensures zero downtime during judging or live demos.
4. **Calculates Multi-Dimensional Scores:** Computes ATS Score, Skill Match %, Role Alignment %, Resume Structure Score, and Evidence Strength %.
5. **Generates Role-Specific Resumes:** Re-prioritizes skills, highlights matching projects, generates role summaries, and produces ATS-compliant PDFs via ReportLab.
6. **Multi-Role Versioning:** Persists tailored resume versions (e.g., *Version 1: Frontend Developer*, *Version 2: AI/ML Engineer*) in SQLite.

---

## Key Features

- **Multi-Format Ingestion:** Drag-and-drop support for **PDF** and **DOCX** files with robust text and section segmentation.
- **Visual Score Dashboard:** Five real-time progress indicators:
  - **ATS Score (0–100%):** Parsability, contact completeness, bullet formatting.
  - **Skill Match (0–100%):** Direct alignment with target role benchmarks.
  - **Role Alignment (0–100%):** Relevance of candidate projects to the target engineering domain.
  - **Resume Structure Score (0–100%):** Coverage of core sections (Education, Skills, Projects, Experience).
  - **Evidence Strength (0–100%):** Ratio of claimed skills supported by actual project/cert evidence.
- **Skills Gap Analysis:**
  - **Matched Skills:** Identified proficiencies with role relevance explanations.
  - **Missing Skills:** Critical role competencies needed for the target job.
  - **Weak / Unverified Skills:** Skills listed without supporting evidence.
- **CLAIM &rarr; EVIDENCE Mapping Table:** Clear transparency showing what project proves which skill (e.g. `Python` &rarr; `Movie Success Prediction System`). Unsubstantiated skills show `Not verified`.
- **Actionable Resume Improvement Report:** Specific `Before` vs. `Suggested` diffs based exclusively on candidate-provided details without fabricating metrics.
- **Manual Resume Builder:** Step-by-step form for candidates building their first resume.
- **Interactive Live Preview & Editor:** Modify candidate summary, skills, and project bullets with immediate visual feedback on an ATS paper sheet.
- **Role-Based Version Management:** Switch between and persist versions for distinct roles in SQLite.
- **ATS-Compliant PDF Export:** Pure-Python PDF generation utilizing standard ATS fonts (Helvetica), standard 0.5-inch margins, and clean section flow.

---

## Architecture & Workflow

```
[ User Browser ]
   │  ├── Landing Page (/)
   │  ├── Upload (/upload)
   │  ├── Analyzer (/analyze)
   │  ├── Builder (/builder)
   │  ├── Preview & Live Editor (/preview)
   │  └── Versions (/versions)
   ▼
[ Flask Application (app.py) ]
   ├── REST API Endpoints (/api/*)
   ├── Secure File Storage (/uploads)
   ├── SQLite Database (resume_analyzer.db)
   │
   ├── [ services/resume_parser.py ] ─── PDF (pypdf) & DOCX (python-docx) Text Extraction
   ├── [ services/analyzer.py ] ──────── Deterministic Taxonomy, Evidence Mapping & ATS Scoring
   ├── [ services/ai_service.py ] ────── Google Gemini API (gemini-2.5-flash) + Local Fallback
   ├── [ services/resume_generator.py ]  Role Re-weighting & Fact-Grounded Summary
   └── [ services/pdf_export.py ] ────── ReportLab ATS-Compliant PDF Generator
```

---

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Frontend** | HTML5, CSS3, Vanilla JavaScript | Responsive modern dashboard, animated scorebars, live preview sheet |
| **Backend** | Python 3.14+, Flask 3.1 | REST API routes, session management, file handling |
| **Database** | SQLite3 | Relational tables for resumes, versions, skills, projects, analyses |
| **AI Engine** | Google Gemini API (`google-genai` SDK) | Deep semantic role alignment & summary generation |
| **Fallback Engine** | Custom Deterministic Python Analyzer | Keyword taxonomy, regex boundary analysis, evidence mapping |
| **PDF Parsing** | `pypdf` 6.10+ | Extracting text blocks from uploaded PDF resumes |
| **DOCX Parsing** | `python-docx` 1.2+ | Parsing paragraphs and tables from Word documents |
| **PDF Generation** | `reportlab` 5.0+ | Generating clean, single/multi-page ATS-standard PDF resumes |

---

## Database Schema (SQLite)

The application uses `resume_analyzer.db` with 8 normalized tables:

1. `users`: Stores candidate identity (`id`, `name`, `email`, `created_at`).
2. `resumes`: Master table storing uploaded resumes, file metadata, raw text, and parsed JSON structures.
3. `skills`: Extracted candidate skills with `verified_status` (`verified` vs `unverified`) and `evidence_source`.
4. `projects`: Candidate project entries (`title`, `description`, `technologies`, `github_url`).
5. `certifications`: Candidate credential records (`name`, `issuer`, `issue_date`).
6. `resume_versions`: Role-tailored snapshots (`version_name`, `target_role`, `formatted_resume` JSON, `ats_score`).
7. `job_descriptions`: Uploaded/pasted job descriptions and extracted skill requirements.
8. `analysis_results`: Stored historical analyses including ATS score, matched skills, missing skills, evidence map, and improvements.

---

## AI & Fallback Engine Strategy

### 1. Gemini Integration
SkillAlign AI integrates Google's official `google-genai` SDK using `gemini-2.5-flash`:
- Reads `GEMINI_API_KEY` securely from `.env`.
- Prompts enforce strict grounding: **Never hallucinate projects, certifications, or metrics**.
- Returns structured JSON containing scores, matched skills, unverified skills, and before/after suggestions.

### 2. Deterministic Local Fallback Analyzer
If `GEMINI_API_KEY` is missing, expired, or offline:
- The system automatically engages `services/analyzer.py`.
- **Zero failure rate:** The application continues running smoothly with 100% of features functioning.
- Employs a comprehensive tech taxonomy (Languages, Web, Backend, AI/ML, Cloud, Databases).
- Checks whole-word regex occurrences of claimed skills across project descriptions and credentials.
- Evaluates ATS structural completeness (contact points, section presence, project depth).

---

## Installation & Setup

### Prerequisites
- Python 3.10+ (tested on Python 3.14)
- Git (optional)

### Steps
1. **Navigate to the project directory:**
   ```bash
   cd "rampex hackerthon"
   ```

2. **Install required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**
   Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
   *(Optional)* Add your Gemini API key in `.env`:
   ```env
   GEMINI_API_KEY=your_actual_key_here
   ```
   *Note: If left empty, the application will automatically run using the built-in deterministic local engine.*

4. **Initialize database & generate sample data:**
   ```bash
   python sample_data/create_samples.py
   ```

5. **Run test suite:**
   ```bash
   python -m unittest tests/test_app.py
   ```

---

## Running the Application

Start the Flask development server:
```bash
python app.py
```

Open your browser at:
```
http://127.0.0.1:5000
```

---

## Hackathon Demo Flow (Step-by-Step)

The application includes an end-to-end demo flow designed for hackathon judges:

1. **Visit Landing Page (`/`):**
   - View role benchmark examples (Frontend Developer, AI/ML Engineer, etc.).
   - Click **"1-Click Demo Resume"** in the top navigation bar, OR click **"Analyze Existing Resume"**.

2. **Upload or 1-Click Demo (`/upload`):**
   - Click **"Load Sample Student Resume (Alex Kumar)"** or drag-and-drop `sample_data/sample_resume_alex_kumar.pdf`.
   - Observe instant structural extraction (Contact info, 17 detected skills, 3 projects, education).
   - Select **Target Role:** `Frontend Developer`.
   - Click **"Proceed to Evidence Audit & Scores"**.

3. **Review Analysis Dashboard (`/analyze`):**
   - Observe the 5 visual scorecards (**ATS Score**, **Skill Match**, **Role Alignment**, **Structure Score**, **Evidence Strength**).
   - View **Skills Gap Analysis:**
     - Matched skills: HTML, CSS, JavaScript, React.
     - Missing skills: REST API, TypeScript, Tailwind.
     - Weak/Unverified skills: e.g. Node.js (listed but absent in projects).
   - Inspect the **CLAIM &rarr; EVIDENCE** Table:
     - `Python` &rarr; `Movie Success Prediction System (Project)` &rarr; **Verified**
     - `HTML/CSS` &rarr; `Student Portfolio Portal (Project)` &rarr; **Verified**
     - `Node.js` &rarr; **Not verified**
   - Review the **Resume Improvement Report** showing `Before` vs. `Suggested` improvements.

4. **Test Target Role Switch:**
   - Change target role dropdown to **AI/ML Engineer**.
   - Click **"Re-Analyze Role"**.
   - Watch the scores update dynamically: Python, Machine Learning, Scikit-Learn become matched core skills, while Deep Learning and PyTorch become recommended additions.

5. **Generate Role-Specific Resume (`/preview`):**
   - Click **"Generate Role-Specific Resume Version"**.
   - The system re-weights projects (puts Movie Prediction on top for AI/ML or Portfolio for Frontend).
   - Review live ATS paper sheet preview.
   - Edit summary or project descriptions on the left; watch the sheet update live.

6. **Save Role Versions (`/versions`):**
   - Save "Version 1: Frontend Developer".
   - Switch role to "AI/ML Engineer" and save "Version 2: AI/ML Developer".
   - View both stored versions in the SQLite database on `/versions`.

7. **Export ATS PDF:**
   - Click **"Download PDF"**; immediately downloads an ATS-formatted PDF generated by ReportLab.

---

## API Documentation

| Method | Endpoint | Description | Payload / Params |
|---|---|---|---|
| `POST` | `/api/upload-resume` | Upload PDF/DOCX or paste raw text | Multipart form (`file`) or `raw_text` |
| `POST` | `/api/analyze-resume` | Run ATS and evidence analysis | `{"resume_id": 1, "target_role": "Frontend Developer", "job_description": "..."}` |
| `POST` | `/api/analyze-job` | Extract required skills from raw JD | `{"job_description": "...", "target_role": "..."}` |
| `POST` | `/api/generate-resume` | Generate role-tailored resume | `{"resume_id": 1, "target_role": "AI/ML Engineer"}` |
| `POST` | `/api/save-resume` | Save or update candidate profile | `{"resume_id": 1, "parsed_data": {...}}` |
| `GET` | `/api/resume/<id>` | Fetch candidate resume record | None |
| `POST` | `/api/create-version` | Save role version to SQLite | `{"resume_id": 1, "version_name": "...", "formatted_resume": {...}}` |
| `GET` | `/api/versions/<id>` | Fetch all saved role versions | None |
| `GET` | `/api/export/<id>` | Download ATS-compliant PDF | Query params: `?role=...` or `?version_id=...` |
| `POST` | `/api/load-sample` | 1-click load of demo resume | None |
| `GET` | `/api/sample-data` | Retrieve sample JDs and roles | None |

---

## Security & Robustness

- **File Validation:** Allowed extensions strictly restricted to `.pdf`, `.docx`, `.doc`, `.txt`.
- **Path Sanitization:** Filenames sanitized via Werkzeug `secure_filename`.
- **Upload Size Ceiling:** Hard cap of 16MB via `MAX_CONTENT_LENGTH`.
- **Non-Executable Storage:** Uploaded files stored as raw data without execution permissions.
- **Environment Isolation:** API keys loaded strictly via `os.getenv` without hardcoded secrets.
- **Defensive Parsing:** Malformed PDFs/DOCX files handled gracefully with structured error reporting.

---

## Future Improvements

1. **GitHub Repository Deep Scan:** Automatically parse commits and README files from candidate's GitHub profile to discover unmentioned project evidence.
2. **Coding Platform Connectors:** Direct OAuth integration with LeetCode, Codeforces, and HackerRank to verify contest ratings and problem-solving badges.
3. **LinkedIn Skill Endorsement Verification:** Cross-check claimed skills against verified certifications from LinkedIn Learning.
4. **LaTeX Resume Export:** Provide downloadable `.tex` templates alongside ReportLab PDFs.

---

## License

Built for the Hackathon 2026. Distributed under the MIT License.
