import re
from services.resume_parser import extract_skills_from_text, COMMON_SKILLS

# Curated role benchmarks for student & entry/mid-level job profiles
ROLE_PROFILES = {
    "Frontend Developer": {
        "core_skills": ["HTML", "HTML5", "CSS", "CSS3", "JavaScript", "React", "TypeScript", "Tailwind CSS", "Bootstrap", "Git"],
        "recommended_skills": ["Redux", "Next.js", "REST API", "Responsive Design", "Jest", "Webpack"],
        "description": "Builds user-facing web applications, responsive user interfaces, and client-side logic.",
        "skill_weights": {"HTML": 1.0, "CSS": 1.0, "JavaScript": 1.5, "React": 1.5, "Git": 0.8, "REST API": 1.0, "TypeScript": 1.0}
    },
    "Backend Developer": {
        "core_skills": ["Python", "Node.js", "Java", "SQL", "PostgreSQL", "MySQL", "REST API", "Git", "Docker"],
        "recommended_skills": ["FastAPI", "Flask", "Django", "Express.js", "Redis", "Microservices", "MongoDB", "Linux"],
        "description": "Architects server-side logic, databases, APIs, authentication, and backend services.",
        "skill_weights": {"SQL": 1.5, "REST API": 1.5, "Python": 1.2, "Node.js": 1.2, "Docker": 1.0, "Git": 0.8}
    },
    "Full Stack Developer": {
        "core_skills": ["JavaScript", "HTML", "CSS", "React", "Node.js", "Python", "SQL", "REST API", "Git"],
        "recommended_skills": ["TypeScript", "Docker", "MongoDB", "PostgreSQL", "Next.js", "Express.js", "AWS"],
        "description": "Develops both client and server software, database architectures, and end-to-end features.",
        "skill_weights": {"JavaScript": 1.2, "React": 1.2, "Node.js": 1.2, "SQL": 1.2, "REST API": 1.2, "Git": 0.8}
    },
    "Python Developer": {
        "core_skills": ["Python", "SQL", "Git", "REST API", "Flask", "Django", "FastAPI", "PostgreSQL", "Linux"],
        "recommended_skills": ["Docker", "Pandas", "PyTest", "Celery", "Redis", "AWS", "OOP"],
        "description": "Specializes in building robust Python software, web backends, automation, and data utilities.",
        "skill_weights": {"Python": 2.0, "SQL": 1.2, "REST API": 1.2, "Git": 0.8, "Flask": 1.0, "Django": 1.0}
    },
    "AI/ML Engineer": {
        "core_skills": ["Python", "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "Scikit-Learn", "Pandas", "NumPy", "SQL"],
        "recommended_skills": ["NLP", "Computer Vision", "OpenCV", "Matplotlib", "Docker", "Data Analysis", "LLM", "RAG"],
        "description": "Develops machine learning models, neural networks, data pipelines, and AI-driven applications.",
        "skill_weights": {"Python": 1.5, "Machine Learning": 1.5, "Scikit-Learn": 1.2, "TensorFlow": 1.2, "PyTorch": 1.2, "Pandas": 1.0}
    },
    "Data Analyst": {
        "core_skills": ["SQL", "Python", "Pandas", "NumPy", "Data Analysis", "Data Visualization", "Matplotlib", "Seaborn", "Excel"],
        "recommended_skills": ["PowerBI", "Tableau", "MySQL", "PostgreSQL", "Statistics", "Git"],
        "description": "Extracts actionable insights from structured data, creates dashboards, and performs statistical analysis.",
        "skill_weights": {"SQL": 1.8, "Python": 1.4, "Data Analysis": 1.5, "Data Visualization": 1.2, "Pandas": 1.2}
    }
}

# Role relevance explanations
SKILL_RELEVANCE_MAP = {
    "React": "Critical for building modular component-based user interfaces and single-page applications.",
    "JavaScript": "Foundational programming language for all client-side browser logic and dynamic interfaces.",
    "TypeScript": "Enforces type safety, preventing common runtime bugs in large-scale modern codebases.",
    "HTML": "Core structural backbone of every accessible, semantic web application.",
    "HTML5": "Modern web standard enabling multimedia, semantic structure, and native input features.",
    "CSS": "Essential for responsive layouts, styling, visual hierarchy, and cross-device display.",
    "CSS3": "Provides animations, transitions, grid, and flexbox for fluid user experiences.",
    "Tailwind CSS": "Industry standard utility-first CSS framework for rapid responsive UI engineering.",
    "REST API": "Standard protocol for communication between client frontends and backend services.",
    "Python": "Primary language for backend services, machine learning models, and automated data pipelines.",
    "Node.js": "Enables high-performance asynchronous, event-driven server backends and microservices.",
    "SQL": "Universal query language required to store, query, and manage relational database records.",
    "PostgreSQL": "Robust, ACID-compliant relational database standard in modern production architectures.",
    "Docker": "Standardizes containerized deployment, ensuring consistency across development and production.",
    "Git": "Essential version control system for collaborative team development, PRs, and code history.",
    "Machine Learning": "Core capability for developing predictive models, pattern recognition, and intelligence systems.",
    "Deep Learning": "Powers complex neural network architectures for computer vision, audio, and language tasks.",
    "TensorFlow": "Industry-grade framework for training and deploying scalable deep learning systems.",
    "PyTorch": "Leading research and production deep learning framework for computer vision and generative AI.",
    "Scikit-Learn": "Standard library for classical machine learning algorithms, preprocessing, and evaluation.",
    "Pandas": "Indispensable tool for high-performance data manipulation, cleaning, and tabular wrangling.",
    "NumPy": "Fundamental package for scientific computing, N-dimensional arrays, and vectorized math.",
    "FastAPI": "Modern, high-performance web framework for building asynchronous Python REST APIs.",
    "Flask": "Lightweight, flexible microframework for microservices and rapid backend development.",
    "Django": "Full-featured Python web framework with built-in ORM, admin panel, and security features.",
    "Data Analysis": "Vital for interpreting raw metrics into actionable technical and business decisions.",
    "Data Visualization": "Translates complex datasets into clear, communicative charts and visual summaries."
}

def get_role_explanation(skill, role):
    """Return why a skill matters for a role."""
    if skill in SKILL_RELEVANCE_MAP:
        return SKILL_RELEVANCE_MAP[skill]
    return f"Important competency for {role} roles to implement industry-standard workflows and requirements."

def parse_job_description_skills(jd_text):
    """Extract required and preferred skills from a raw job description."""
    if not jd_text or not jd_text.strip():
        return []
    skills = extract_skills_from_text(jd_text)
    return [s["name"] for s in skills]

def build_evidence_map(claimed_skills, projects, certifications, experiences):
    """
    Map each claimed skill to real evidence from projects, certifications, or experience.
    Strict rule: Never fabricate evidence. If not found, mark 'Not verified'.
    """
    evidence_map = []
    
    for skill_obj in claimed_skills:
        skill_name = skill_obj if isinstance(skill_obj, str) else skill_obj.get("name", "")
        if not skill_name:
            continue
            
        skill_lower = skill_name.lower()
        matched_evidence = []

        # Check projects
        for proj in projects:
            title = proj.get("title", "")
            desc = proj.get("description", "")
            tech = proj.get("technologies", "")
            combined_proj = f"{title} {tech} {desc}".lower()
            
            # Match whole word or exact skill
            pattern = r'\b' + re.escape(skill_lower) + r'\b'
            if skill_lower in ['c++', 'c#']:
                pattern = re.escape(skill_lower)
                
            if re.search(pattern, combined_proj):
                matched_evidence.append({
                    "type": "Project",
                    "source": title or "Technical Project",
                    "snippet": desc[:120] + "..." if len(desc) > 120 else desc
                })

        # Check certifications
        for cert in certifications:
            cert_name = cert if isinstance(cert, str) else cert.get("name", "")
            issuer = cert.get("issuer", "") if isinstance(cert, dict) else ""
            combined_cert = f"{cert_name} {issuer}".lower()
            if skill_lower in combined_cert:
                matched_evidence.append({
                    "type": "Certification",
                    "source": cert_name,
                    "snippet": f"Certified by {issuer}" if issuer else "Verified credential"
                })

        # Check experience
        for exp in experiences:
            role = exp.get("role", "")
            company = exp.get("company", "")
            desc = exp.get("description", "")
            combined_exp = f"{role} {company} {desc}".lower()
            pattern = r'\b' + re.escape(skill_lower) + r'\b'
            if skill_lower in ['c++', 'c#']:
                pattern = re.escape(skill_lower)
            if re.search(pattern, combined_exp):
                matched_evidence.append({
                    "type": "Experience",
                    "source": f"{role} at {company}".strip(" at"),
                    "snippet": desc[:120] + "..." if len(desc) > 120 else desc
                })

        if matched_evidence:
            primary_evidence = matched_evidence[0]
            evidence_label = f"{primary_evidence['source']} ({primary_evidence['type']})"
            evidence_map.append({
                "skill": skill_name,
                "verified": True,
                "status": "Verified",
                "evidence": evidence_label,
                "details": primary_evidence['snippet'],
                "evidence_count": len(matched_evidence)
            })
        else:
            evidence_map.append({
                "skill": skill_name,
                "verified": False,
                "status": "Not verified",
                "evidence": "Not verified",
                "details": "No project, certification, or work experience explicitly references this skill.",
                "evidence_count": 0
            })

    return evidence_map

def calculate_ats_structure_score(parsed_resume):
    """
    Evaluate structural ATS compliance:
    - Contact info completeness (name, email, phone)
    - Key sections present
    - Bullet point utilization
    - Format clarity
    """
    score = 0
    checks = []

    # 1. Contact Info (25 pts)
    contact_pts = 0
    if parsed_resume.get("name") and parsed_resume.get("name") != "Student Candidate":
        contact_pts += 10
    if parsed_resume.get("email"):
        contact_pts += 10
    if parsed_resume.get("phone"):
        contact_pts += 5
    score += contact_pts
    checks.append({"name": "Contact Information", "passed": contact_pts >= 20, "score": contact_pts, "max": 25})

    # 2. Key Sections Present (35 pts)
    section_pts = 0
    if parsed_resume.get("education"):
        section_pts += 10
    if parsed_resume.get("skills"):
        section_pts += 10
    if parsed_resume.get("projects"):
        section_pts += 10
    if parsed_resume.get("experience") or parsed_resume.get("certifications"):
        section_pts += 5
    score += section_pts
    checks.append({"name": "Core Sections Completeness", "passed": section_pts >= 25, "score": section_pts, "max": 35})

    # 3. Project Depth (25 pts)
    proj_pts = 0
    projects = parsed_resume.get("projects", [])
    if len(projects) >= 2:
        proj_pts += 15
    elif len(projects) == 1:
        proj_pts += 8

    # Check if project descriptions contain action-oriented content
    has_descriptions = any(len(p.get("description", "")) > 40 for p in projects)
    if has_descriptions:
        proj_pts += 10
    score += proj_pts
    checks.append({"name": "Project Documentation", "passed": proj_pts >= 15, "score": proj_pts, "max": 25})

    # 4. Professional Links & Profiles (15 pts)
    link_pts = 0
    if parsed_resume.get("github"):
        link_pts += 8
    if parsed_resume.get("linkedin"):
        link_pts += 7
    score += link_pts
    checks.append({"name": "Developer Profiles (GitHub/LinkedIn)", "passed": link_pts >= 8, "score": link_pts, "max": 15})

    return min(100, max(20, score)), checks

def generate_improvement_recommendations(parsed_resume, target_role, evidence_map, missing_skills):
    """
    Generate realistic, actionable resume improvement suggestions.
    Crucial: Never fabricate metrics or invent nonexistent work.
    """
    improvements = []

    # 1. ATS Recommendations
    if not parsed_resume.get("phone"):
        improvements.append({
            "category": "ATS",
            "title": "Include Phone Number",
            "recommendation": "Recruiters and automated ATS parsing filters require a contact phone number for candidate outreach.",
            "before": "Missing phone number in contact header",
            "suggested": "Add standard format phone: e.g. +1 (555) 000-0000 or +91 XXXXX XXXXX"
        })
    if not parsed_resume.get("github"):
        improvements.append({
            "category": "ATS",
            "title": "Add Developer Portfolio / GitHub Link",
            "recommendation": "Technical recruiters and hiring teams prioritize verifiable code repositories.",
            "before": "No code repository link provided",
            "suggested": "Include your GitHub profile link: github.com/your-username"
        })

    # 2. Skills Recommendations
    if missing_skills:
        top_missing = missing_skills[:3]
        improvements.append({
            "category": "Skills",
            "title": f"Target Role Skills Alignment for {target_role}",
            "recommendation": f"Add or demonstrate foundational experience in: {', '.join(top_missing)}.",
            "before": f"Resume currently does not highlight {', '.join(top_missing)}.",
            "suggested": f"Integrate {', '.join(top_missing)} into upcoming academic assignments, personal projects, or coursework."
        })

    # 3. Missing Evidence Recommendations
    unverified_skills = [e["skill"] for e in evidence_map if not e["verified"]]
    if unverified_skills:
        sample_unverified = unverified_skills[:3]
        improvements.append({
            "category": "Missing evidence",
            "title": "Unverified Skills Need Supporting Evidence",
            "recommendation": f"The following skills are claimed in your skills list without supporting project or experience context: {', '.join(sample_unverified)}.",
            "before": f"Listed skills: {', '.join(sample_unverified)} (no matching project description).",
            "suggested": f"Explicitly mention how you used {sample_unverified[0]} in a project description or coursework."
        })

    # 4. Project Improvement Recommendations
    projects = parsed_resume.get("projects", [])
    if projects:
        first_proj = projects[0]
        desc = first_proj.get("description", "").strip()
        title = first_proj.get("title", "Project")
        tech = first_proj.get("technologies", "")

        # Action verb enhancement suggestion based on user's actual text
        if desc:
            # Generate a cleaner, more impactful suggested version without fabricating false numbers
            cleaned_desc = desc
            for weak_prefix in ["worked on", "made a", "created a", "did a", "built a"]:
                if cleaned_desc.lower().startswith(weak_prefix):
                    cleaned_desc = cleaned_desc[len(weak_prefix):].strip()
            
            suggested_desc = f"Architected and implemented {title} leveraging {tech or 'modern engineering practices'}, focusing on clean modular design and robust execution."
            if "predict" in desc.lower() or "model" in desc.lower():
                suggested_desc = f"Engineered machine learning pipeline for {title} utilizing {tech or 'Python and Scikit-Learn'}, conducting feature engineering, model training, and performance evaluation."
            elif "web" in desc.lower() or "website" in desc.lower() or "app" in desc.lower():
                suggested_desc = f"Developed responsive, full-featured {title} utilizing {tech or 'modern web frameworks'}, implementing clean UI components and RESTful data flow."

            improvements.append({
                "category": "Projects",
                "title": f"Enhance Technical Impact for '{title}'",
                "recommendation": "Use strong action verbs and technical specifics. When quantifiable outcomes (latency reduction, user count, accuracy) exist from your tests, include them.",
                "before": desc[:140] + ("..." if len(desc) > 140 else ""),
                "suggested": suggested_desc
            })
    else:
        improvements.append({
            "category": "Projects",
            "title": "Add Verified Academic or Personal Projects",
            "recommendation": "Student resumes require at least 2 distinct technical projects demonstrating practical implementation.",
            "before": "Zero projects listed in resume.",
            "suggested": "Add at least two projects detailing title, technologies used, problem solved, and repository link."
        })

    # 5. Role Alignment
    improvements.append({
        "category": "Role alignment",
        "title": f"Tailor Technical Summary to {target_role}",
        "recommendation": f"Customize your professional summary to explicitly focus on {target_role} competencies.",
        "before": parsed_resume.get("summary") or "Generic student objective statement.",
        "suggested": f"Aspiring {target_role} with hands-on project experience in {', '.join([s['name'] for s in parsed_resume.get('skills', [])[:3]] or ['software development'])}, eager to contribute to robust software delivery."
    })

    return improvements

def analyze_resume_locally(parsed_resume, target_role="Frontend Developer", job_description_text=""):
    """
    Deterministic Local Fallback Analyzer.
    Provides complete, realistic scoring, evidence mapping, and improvement suggestions
    strictly based on extracted candidate information and target role benchmarks.
    """
    # 1. Determine target skills benchmark
    role_info = ROLE_PROFILES.get(target_role, ROLE_PROFILES["Frontend Developer"])
    core_target_skills = list(role_info["core_skills"])
    recommended_target_skills = list(role_info["recommended_skills"])

    # If job description is provided, extract additional skills
    jd_skills = []
    if job_description_text and job_description_text.strip():
        jd_skills = parse_job_description_skills(job_description_text)
        if jd_skills:
            # Prioritize skills mentioned in the job description
            core_target_skills = list(dict.fromkeys(jd_skills + core_target_skills))

    # Candidate claimed skills
    claimed_skill_names = [s["name"] if isinstance(s, dict) else s for s in parsed_resume.get("skills", [])]
    claimed_skill_names_lower = {s.lower(): s for s in claimed_skill_names}

    # 2. Skill Matching
    matched_skills = []
    missing_skills = []

    for target_skill in core_target_skills:
        t_lower = target_skill.lower()
        if t_lower in claimed_skill_names_lower:
            matched_skills.append({
                "name": claimed_skill_names_lower[t_lower],
                "category": COMMON_SKILLS.get(target_skill, "Technical"),
                "reason": get_role_explanation(target_skill, target_role),
                "importance": "High"
            })
        else:
            missing_skills.append({
                "name": target_skill,
                "category": COMMON_SKILLS.get(target_skill, "Technical"),
                "reason": get_role_explanation(target_skill, target_role),
                "importance": "High"
            })

    for rec_skill in recommended_target_skills:
        r_lower = rec_skill.lower()
        if r_lower in claimed_skill_names_lower:
            if not any(m["name"].lower() == r_lower for m in matched_skills):
                matched_skills.append({
                    "name": claimed_skill_names_lower[r_lower],
                    "category": COMMON_SKILLS.get(rec_skill, "Technical"),
                    "reason": get_role_explanation(rec_skill, target_role),
                    "importance": "Recommended"
                })
        else:
            if not any(m["name"].lower() == r_lower for m in missing_skills):
                missing_skills.append({
                    "name": rec_skill,
                    "category": COMMON_SKILLS.get(rec_skill, "Technical"),
                    "reason": get_role_explanation(rec_skill, target_role),
                    "importance": "Recommended"
                })

    # 3. Evidence Mapping: Claim -> Evidence or 'Not verified'
    evidence_map = build_evidence_map(
        parsed_resume.get("skills", []),
        parsed_resume.get("projects", []),
        parsed_resume.get("certifications", []),
        parsed_resume.get("experience", [])
    )

    # 4. Weak / Unverified Skills
    weak_skills = []
    for item in evidence_map:
        if not item["verified"]:
            weak_skills.append({
                "name": item["skill"],
                "reason": f"Skill '{item['skill']}' is listed in resume skills, but has no supporting projects, certifications, or work experience to substantiate it."
            })

    # 5. Scores Computation
    structure_score, checks = calculate_ats_structure_score(parsed_resume)

    # Skill Match Score (%)
    total_target_count = len(core_target_skills) + int(len(recommended_target_skills) * 0.5)
    matched_count = len([m for m in matched_skills if m["importance"] == "High"]) + int(len([m for m in matched_skills if m["importance"] == "Recommended"]) * 0.5)
    skill_match_pct = int(min(100, max(15, (matched_count / max(1, total_target_count)) * 100)))

    # Evidence Strength Score (%)
    verified_count = len([e for e in evidence_map if e["verified"]])
    total_claimed = max(1, len(evidence_map))
    evidence_strength_pct = int(min(100, max(10, (verified_count / total_claimed) * 100)))

    # Role Alignment Score (%)
    # Combines skill match with whether projects/experience relate to target domain
    domain_relevance_bonus = 0
    all_proj_text = " ".join([p.get("description", "") + " " + p.get("technologies", "") for p in parsed_resume.get("projects", [])]).lower()
    if target_role == "Frontend Developer" and any(k in all_proj_text for k in ["react", "web", "frontend", "ui", "css", "html", "javascript"]):
        domain_relevance_bonus += 15
    elif target_role in ["AI/ML Engineer", "Data Analyst"] and any(k in all_proj_text for k in ["model", "learning", "data", "prediction", "python", "scikit", "pandas"]):
        domain_relevance_bonus += 15
    elif target_role in ["Backend Developer", "Python Developer"] and any(k in all_proj_text for k in ["api", "backend", "database", "sql", "server", "flask", "django"]):
        domain_relevance_bonus += 15

    role_alignment_pct = int(min(98, max(20, (skill_match_pct * 0.7) + domain_relevance_bonus)))

    # ATS Score (%)
    # Weighted composite of structure (35%), skill match (30%), evidence strength (25%), contact/profiles (10%)
    ats_score = int((structure_score * 0.40) + (skill_match_pct * 0.35) + (evidence_strength_pct * 0.25))
    ats_score = min(98, max(25, ats_score))

    # 6. Improvements
    improvements = generate_improvement_recommendations(parsed_resume, target_role, evidence_map, [m["name"] for m in missing_skills])

    return {
        "target_role": target_role,
        "ats_score": ats_score,
        "skill_match": skill_match_pct,
        "role_alignment": role_alignment_pct,
        "structure_score": structure_score,
        "evidence_strength": evidence_strength_pct,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "weak_skills": weak_skills,
        "evidence_map": evidence_map,
        "improvements": improvements,
        "structure_checks": checks,
        "engine": "deterministic_fallback"
    }
