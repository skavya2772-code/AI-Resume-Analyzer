from services.analyzer import ROLE_PROFILES
from services.ai_service import generate_role_summary_ai

def generate_role_tailored_resume(parsed_data, target_role="Frontend Developer"):
    """
    Generate an ATS-optimized, role-tailored resume data structure based strictly
    on verified candidate information.
    """
    role_benchmarks = ROLE_PROFILES.get(target_role, ROLE_PROFILES["Frontend Developer"])
    core_skills = [s.lower() for s in role_benchmarks.get("core_skills", [])]

    # 1. Contact Info
    contact = {
        "name": parsed_data.get("name") or "Candidate Name",
        "email": parsed_data.get("email") or "",
        "phone": parsed_data.get("phone") or "",
        "github": parsed_data.get("github") or "",
        "linkedin": parsed_data.get("linkedin") or ""
    }

    # 2. Targeted Summary
    summary = generate_role_summary_ai(parsed_data, target_role)

    # 3. Prioritized Skills
    raw_skills = parsed_data.get("skills", [])
    prioritized_skills = []
    other_skills = []

    for sk in raw_skills:
        name = sk if isinstance(sk, str) else sk.get("name", "")
        cat = sk.get("category", "Technical") if isinstance(sk, dict) else "Technical"
        if not name:
            continue
        if name.lower() in core_skills:
            prioritized_skills.append({"name": name, "category": cat, "priority": True})
        else:
            other_skills.append({"name": name, "category": cat, "priority": False})

    # Group skills by category
    categorized_skills = {}
    for sk in prioritized_skills + other_skills:
        cat = sk["category"]
        if cat not in categorized_skills:
            categorized_skills[cat] = []
        if sk["name"] not in categorized_skills[cat]:
            categorized_skills[cat].append(sk["name"])

    # 4. Prioritized Projects
    projects = list(parsed_data.get("projects", []))
    
    def project_relevance_score(proj):
        score = 0
        desc = (proj.get("description", "") + " " + proj.get("technologies", "") + " " + proj.get("title", "")).lower()
        for sk in core_skills:
            if sk in desc:
                score += 2
        return score

    # Sort projects by relevance to target role
    sorted_projects = sorted(projects, key=project_relevance_score, reverse=True)

    # 5. Experience
    experience = parsed_data.get("experience", [])

    # 6. Education
    education = parsed_data.get("education", [])

    # 7. Certifications
    certifications = parsed_data.get("certifications", [])

    # 8. Achievements
    achievements = parsed_data.get("achievements", [])

    return {
        "target_role": target_role,
        "contact": contact,
        "summary": summary,
        "skills": categorized_skills,
        "raw_skills": [s["name"] if isinstance(s, dict) else s for s in raw_skills],
        "projects": sorted_projects,
        "experience": experience,
        "education": education,
        "certifications": certifications,
        "achievements": achievements
    }
