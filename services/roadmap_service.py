import os
import json
from services.ai_service import get_gemini_client
from services.analyzer import ROLE_PROFILES, COMMON_SKILLS

ROADMAP_BLUEPRINTS = {
    "Frontend Developer": {
        "readiness_base": 65,
        "phases": [
            {
                "phase_number": 1,
                "title": "Phase 1: Advanced JavaScript, DOM & TypeScript",
                "duration": "Weeks 1 - 4",
                "description": "Master modern ECMAScript standards (ES2024+), asynchronous JavaScript (Promises, async/await), DOM performance, and TypeScript type safety.",
                "skills_to_learn": ["TypeScript", "ES6+", "Asynchronous JS", "Web APIs"],
                "milestones": [
                    {"id": "fe_p1_1", "task": "Refactor a vanilla JavaScript utility to TypeScript with strict type checking", "completed": False},
                    {"id": "fe_p1_2", "task": "Implement asynchronous data fetching with comprehensive error boundaries", "completed": False},
                    {"id": "fe_p1_3", "task": "Master CSS Grid, Flexbox, and responsive layout without external frameworks", "completed": False}
                ],
                "recommended_resources": [
                    {"name": "TypeScript Handbook (Official)", "type": "Documentation", "link": "https://www.typescriptlang.org/docs/"},
                    {"name": "javascript.info - Modern Tutorial", "type": "Course", "link": "https://javascript.info/"}
                ]
            },
            {
                "phase_number": 2,
                "title": "Phase 2: React Ecosystem & Modern State Management",
                "duration": "Weeks 5 - 8",
                "description": "Deep dive into component lifecycle, custom hooks, context API, state managers (Zustand / Redux Toolkit), and Tailwind CSS.",
                "skills_to_learn": ["React", "Custom Hooks", "Zustand / Redux", "Tailwind CSS"],
                "milestones": [
                    {"id": "fe_p2_1", "task": "Build multi-view Single Page Application using React Router v6", "completed": False},
                    {"id": "fe_p2_2", "task": "Implement global client-side caching with TanStack React Query", "completed": False},
                    {"id": "fe_p2_3", "task": "Construct a reusable component design system using Tailwind CSS", "completed": False}
                ],
                "recommended_resources": [
                    {"name": "React Documentation (Official)", "type": "Documentation", "link": "https://react.dev/"},
                    {"name": "Tailwind CSS Component Guide", "type": "Docs", "link": "https://tailwindcss.com/docs"}
                ]
            },
            {
                "phase_number": 3,
                "title": "Phase 3: Production Web Project & Evidence Building",
                "duration": "Weeks 9 - 14",
                "description": "Build an industry-grade portfolio project that provides verifiable evidence for claimed frontend skills.",
                "skills_to_learn": ["Next.js", "Performance Optimization", "Lighthouse", "REST APIs"],
                "milestones": [
                    {"id": "fe_p3_1", "task": "Engineer an interactive SaaS Dashboard featuring real-time data visual charts", "completed": False},
                    {"id": "fe_p3_2", "task": "Audit and achieve 95+ score on Google Lighthouse (LCP, CLS, FID)", "completed": False},
                    {"id": "fe_p3_3", "task": "Deploy live production app on Vercel with automated CI/CD GitHub Actions", "completed": False}
                ],
                "recommended_resources": [
                    {"name": "Next.js Learn Course", "type": "Interactive Guide", "link": "https://nextjs.org/learn"},
                    {"name": "Web.dev Performance Auditing", "type": "Articles", "link": "https://web.dev/explore/fast"}
                ]
            },
            {
                "phase_number": 4,
                "title": "Phase 4: Frontend Testing, Interview Drills & Applications",
                "duration": "Weeks 15 - 18",
                "description": "Component unit testing with Vitest/Jest, mock interviews, and tailoring role resumes.",
                "skills_to_learn": ["Jest / Vitest", "React Testing Library", "System Design (Frontend)", "Behavioral STAR"],
                "milestones": [
                    {"id": "fe_p4_1", "task": "Write component tests covering user interactions and API mocks", "completed": False},
                    {"id": "fe_p4_2", "task": "Practice 5 mock HR & Technical frontend interviews on SkillAlign AI", "completed": False},
                    {"id": "fe_p4_3", "task": "Tailor resume version specifically for Frontend Developer positions and export PDF", "completed": False}
                ],
                "recommended_resources": [
                    {"name": "Testing Library Cheatsheet", "type": "Guide", "link": "https://testing-library.com/"},
                    {"name": "Frontend Interview Handbook", "type": "Repository", "link": "https://www.frontendinterviewhandbook.com/"}
                ]
            }
        ],
        "recommended_projects": [
            {
                "title": "Collaborative Real-Time Workspace Canvas",
                "focus_areas": "React, TypeScript, Tailwind CSS, WebSockets, REST API",
                "description": "Build an interactive multi-user whiteboard or task board with real-time state synchronization, drag-and-drop mechanics, and role permissions.",
                "resume_bullet_suggestion": "Architected responsive collaborative workspace using React, TypeScript, and WebSockets, supporting real-time multi-user synchronization."
            },
            {
                "title": "E-Commerce Analytics & Inventory Management Portal",
                "focus_areas": "Next.js, Tailwind CSS, Chart.js / Recharts, TanStack Query",
                "description": "Develop full-featured admin portal with interactive sales charts, paginated orders table with multi-column filtering, and dark mode toggle.",
                "resume_bullet_suggestion": "Engineered enterprise analytics dashboard utilizing Next.js and Tailwind CSS, reducing page load times by 40% through server components."
            }
        ]
    },
    "AI/ML Engineer": {
        "readiness_base": 60,
        "phases": [
            {
                "phase_number": 1,
                "title": "Phase 1: Mathematics, Feature Engineering & Classical ML",
                "duration": "Weeks 1 - 4",
                "description": "Linear algebra, multivariable calculus, probability, vectorized math with NumPy/Pandas, and feature engineering pipelines with Scikit-Learn.",
                "skills_to_learn": ["NumPy", "Pandas", "Scikit-Learn", "Feature Engineering", "Statistical Analysis"],
                "milestones": [
                    {"id": "ml_p1_1", "task": "Implement linear regression and gradient descent from scratch in pure NumPy", "completed": False},
                    {"id": "ml_p1_2", "task": "Construct reproducible data cleaning and categorical encoding pipelines using Scikit-Learn", "completed": False},
                    {"id": "ml_p1_3", "task": "Evaluate classification models using Precision-Recall, ROC-AUC, and Cross-Validation", "completed": False}
                ],
                "recommended_resources": [
                    {"name": "Scikit-Learn User Guide", "type": "Documentation", "link": "https://scikit-learn.org/stable/user_guide.html"},
                    {"name": "Kaggle Feature Engineering Micro-Course", "type": "Hands-on", "link": "https://www.kaggle.com/learn"}
                ]
            },
            {
                "phase_number": 2,
                "title": "Phase 2: Deep Learning Architectures & PyTorch",
                "duration": "Weeks 5 - 8",
                "description": "Feedforward neural networks, Convolutional Neural Networks (CNNs), Recurrent / Transformers concepts, and model training in PyTorch.",
                "skills_to_learn": ["PyTorch", "Deep Learning", "Neural Networks", "TensorFlow", "Computer Vision / NLP"],
                "milestones": [
                    {"id": "ml_p2_1", "task": "Train a custom image classification CNN using PyTorch with data augmentation", "completed": False},
                    {"id": "ml_p2_2", "task": "Implement learning rate schedulers and early stopping to prevent model overfitting", "completed": False},
                    {"id": "ml_p2_3", "task": "Fine-tune a pretrained Hugging Face transformer model for sentiment classification", "completed": False}
                ],
                "recommended_resources": [
                    {"name": "PyTorch Deep Learning Tutorials", "type": "Interactive", "link": "https://pytorch.org/tutorials/"},
                    {"name": "Hugging Face NLP Course", "type": "Course", "link": "https://huggingface.co/learn/nlp-course"}
                ]
            },
            {
                "phase_number": 3,
                "title": "Phase 3: MLOps, Containerization & API Deployment",
                "duration": "Weeks 9 - 14",
                "description": "Package trained models into high-performance REST inference services using FastAPI and Docker containers.",
                "skills_to_learn": ["FastAPI", "Docker", "Model Serving", "MLflow", "REST API"],
                "milestones": [
                    {"id": "ml_p3_1", "task": "Wrap model inference pipeline into asynchronous FastAPI endpoint with input schema validation", "completed": False},
                    {"id": "ml_p3_2", "task": "Containerize the inference service with Docker and multi-stage builds", "completed": False},
                    {"id": "ml_p3_3", "task": "Deploy Dockerized model to Cloud Run or AWS ECS with monitoring", "completed": False}
                ],
                "recommended_resources": [
                    {"name": "FastAPI Documentation", "type": "Docs", "link": "https://fastapi.tiangolo.com/"},
                    {"name": "Full Stack Deep Learning MLOps", "type": "Guide", "link": "https://fullstackdeeplearning.com/"}
                ]
            },
            {
                "phase_number": 4,
                "title": "Phase 4: ML System Design, Interview Prep & Portfolio",
                "duration": "Weeks 15 - 18",
                "description": "Machine learning system design questions, data pipeline trade-offs, and behavioral HR readiness.",
                "skills_to_learn": ["ML System Design", "Data Pipelines", "Model Drift", "Interview STAR"],
                "milestones": [
                    {"id": "ml_p4_1", "task": "Design end-to-end recommendation or fraud detection architecture on paper", "completed": False},
                    {"id": "ml_p4_2", "task": "Complete 3 AI/ML mock interviews on SkillAlign AI simulator", "completed": False},
                    {"id": "ml_p4_3", "task": "Generate and save AI/ML Engineer resume version with verified project evidence", "completed": False}
                ],
                "recommended_resources": [
                    {"name": "ML System Design Interview Guide", "type": "Repository", "link": "https://github.com/chiphuyen/machine-learning-systems-design"},
                    {"name": "Google Machine Learning Crash Course", "type": "Course", "link": "https://developers.google.com/machine-learning/crash-course"}
                ]
            }
        ],
        "recommended_projects": [
            {
                "title": "End-to-End Predictive Maintenance & Anomaly Detection System",
                "focus_areas": "Python, Scikit-Learn, PyTorch, FastAPI, Docker",
                "description": "Train temporal anomaly detection pipeline on sensor data, serve real-time predictions over REST API, and visualize anomalies on a web dashboard.",
                "resume_bullet_suggestion": "Engineered real-time anomaly detection pipeline with PyTorch and FastAPI; containerized with Docker for sub-50ms inference latency."
            },
            {
                "title": "Intelligent Document Q&A with RAG & Vector Embeddings",
                "focus_areas": "Python, Gemini API / HuggingFace, ChromaDB / FAISS, LangChain",
                "description": "Build Retrieval-Augmented Generation (RAG) system allowing users to upload PDFs and ask natural language questions grounded in document text.",
                "resume_bullet_suggestion": "Developed semantic document search and Q&A pipeline with FAISS vector database and Gemini API, achieving high precision grounding."
            }
        ]
    }
}

def generate_career_roadmap_service(resume_data, target_role="Software Developer", timeline="6 Months"):
    """
    Generate a tailored career roadmap analyzing candidate's current evidence vs target role.
    Uses Gemini API if available, falls back to deterministic blueprint.
    """
    skills_raw = resume_data.get("skills", []) if resume_data else []
    claimed_skills = [s["name"] if isinstance(s, dict) else s for s in skills_raw]
    projects = resume_data.get("projects", []) if resume_data else []
    
    role_info = ROLE_PROFILES.get(target_role, ROLE_PROFILES["Frontend Developer"])
    core_target_skills = role_info.get("core_skills", ["Programming", "Git", "Problem Solving"])
    
    # Identify verified skills vs missing
    matched = [s for s in claimed_skills if s.lower() in [c.lower() for c in core_target_skills]]
    missing = [c for c in core_target_skills if c.lower() not in [s.lower() for s in claimed_skills]]

    client = get_gemini_client()
    if client:
        try:
            prompt = f"""
You are an expert Career Coach and Technical Engineering Mentor.
Create a detailed, highly actionable, step-by-step Career Roadmap for a student/fresher aspiring to become a: "{target_role}".
Pacing Timeline: {timeline}

CANDIDATE CONTEXT:
- Name: {resume_data.get('name', 'Candidate') if resume_data else 'Candidate'}
- Current Claimed Skills: {', '.join(claimed_skills) if claimed_skills else 'Basic programming'}
- Current Projects: {json.dumps([p.get('title') for p in projects[:3]])}
- Skills Already Matched: {', '.join(matched) if matched else 'Foundational concepts'}
- Critical Skill Gaps: {', '.join(missing) if missing else 'Advanced tooling and deployment'}

CRITICAL INSTRUCTIONS:
1. Divide the roadmap into 4 sequential progressive phases with realistic week/month timeframes for a {timeline} timeline.
2. In Phase 3, recommend 2 specific, realistic portfolio project blueprints that will provide verifiable evidence for their missing skills without inventing fake past experience.
3. Provide actionable milestone tasks with clear objectives.
4. Keep resources realistic, free or standard industry documentation.
5. Return ONLY a valid JSON object matching the exact structure below.

JSON SCHEMA:
{{
  "target_role": "{target_role}",
  "timeline": "{timeline}",
  "current_readiness_score": 65,
  "readiness_label": "High Potential - Solid Foundation",
  "verified_strengths": {json.dumps(matched[:5] or ["Foundational Programming"])},
  "critical_skill_gaps": {json.dumps(missing[:5] or ["Framework Specialization"])},
  "summary": "Tailored career trajectory focusing on practical implementation...",
  "phases": [
    {{
      "phase_number": 1,
      "title": "Phase 1: Title",
      "duration": "Weeks 1 - 4",
      "description": "Detailed explanation of what to learn",
      "skills_to_learn": ["Skill1", "Skill2"],
      "milestones": [
        {{"id": "p1_1", "task": "Specific actionable milestone", "completed": false}}
      ],
      "recommended_resources": [
        {{"name": "Resource Name", "type": "Documentation", "link": "https://..."}}
      ]
    }}
  ],
  "recommended_projects": [
    {{
      "title": "Project Concept Title",
      "focus_areas": "Tech1, Tech2, Tech3",
      "description": "What to build and how it demonstrates competencies",
      "resume_bullet_suggestion": "Suggested action-verb bullet point for candidate resume"
    }}
  ]
}}
"""
            resp = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            raw = resp.text.strip()
            if raw.startswith("```json"):
                raw = raw[7:]
            elif raw.startswith("```"):
                raw = raw[3:]
            if raw.endswith("```"):
                raw = raw[:-3]
            data = json.loads(raw.strip())
            data["engine"] = "gemini-2.5-flash"
            return data
        except Exception as e:
            print(f"Gemini roadmap generation error: {e}. Using deterministic fallback.")

    # Deterministic Local Fallback
    template_key = target_role if target_role in ROADMAP_BLUEPRINTS else ("AI/ML Engineer" if "AI" in target_role or "ML" in target_role or "Data" in target_role else "Frontend Developer")
    blueprint = ROADMAP_BLUEPRINTS[template_key]

    readiness = int(min(90, max(35, len(matched) * 15 + len(projects) * 10 + 20)))
    readiness_label = "Strong Foundation" if readiness >= 75 else ("Good Starting Point" if readiness >= 55 else "Beginner Level")

    return {
        "target_role": target_role,
        "timeline": timeline,
        "current_readiness_score": readiness,
        "readiness_label": f"{readiness_label} for {target_role}",
        "verified_strengths": matched if matched else (claimed_skills[:4] if claimed_skills else ["Core Programming"]),
        "critical_skill_gaps": missing if missing else ["Advanced Architecture", "Testing & Deployment"],
        "summary": f"Personalized {timeline} career roadmap structured to bridge key engineering skill gaps and build verifiable portfolio evidence for {target_role} hiring standards.",
        "phases": blueprint["phases"],
        "recommended_projects": blueprint["recommended_projects"],
        "engine": "deterministic_local"
    }
