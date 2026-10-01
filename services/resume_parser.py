import re
import os
import pypdf
import docx

# Comprehensive skill taxonomy for skill matching and categorization
COMMON_SKILLS = {
    # Languages
    "Python": "Programming Languages",
    "JavaScript": "Programming Languages",
    "TypeScript": "Programming Languages",
    "Java": "Programming Languages",
    "C++": "Programming Languages",
    "C": "Programming Languages",
    "C#": "Programming Languages",
    "Go": "Programming Languages",
    "Rust": "Programming Languages",
    "Ruby": "Programming Languages",
    "PHP": "Programming Languages",
    "SQL": "Databases & Query",
    "HTML": "Frontend",
    "HTML5": "Frontend",
    "CSS": "Frontend",
    "CSS3": "Frontend",
    # Frontend
    "React": "Frontend",
    "React.js": "Frontend",
    "Next.js": "Frontend",
    "Vue.js": "Frontend",
    "Vue": "Frontend",
    "Angular": "Frontend",
    "Redux": "Frontend",
    "Tailwind CSS": "Frontend",
    "Tailwind": "Frontend",
    "Bootstrap": "Frontend",
    "Sass": "Frontend",
    "jQuery": "Frontend",
    # Backend
    "Node.js": "Backend",
    "Express.js": "Backend",
    "Express": "Backend",
    "Django": "Backend",
    "Flask": "Backend",
    "FastAPI": "Backend",
    "Spring Boot": "Backend",
    "Ruby on Rails": "Backend",
    "REST API": "Backend",
    "GraphQL": "Backend",
    "gRPC": "Backend",
    "Microservices": "Backend",
    # AI/ML & Data
    "Machine Learning": "AI & Machine Learning",
    "Deep Learning": "AI & Machine Learning",
    "Artificial Intelligence": "AI & Machine Learning",
    "TensorFlow": "AI & Machine Learning",
    "PyTorch": "AI & Machine Learning",
    "Scikit-Learn": "AI & Machine Learning",
    "Keras": "AI & Machine Learning",
    "Pandas": "Data Science & Analytics",
    "NumPy": "Data Science & Analytics",
    "Matplotlib": "Data Science & Analytics",
    "Seaborn": "Data Science & Analytics",
    "Data Analysis": "Data Science & Analytics",
    "Data Visualization": "Data Science & Analytics",
    "NLP": "AI & Machine Learning",
    "Natural Language Processing": "AI & Machine Learning",
    "Computer Vision": "AI & Machine Learning",
    "OpenCV": "AI & Machine Learning",
    "Gemini API": "AI & Machine Learning",
    "OpenAI": "AI & Machine Learning",
    "LLM": "AI & Machine Learning",
    "RAG": "AI & Machine Learning",
    # Databases
    "PostgreSQL": "Databases & Query",
    "MySQL": "Databases & Query",
    "SQLite": "Databases & Query",
    "MongoDB": "Databases & Query",
    "Redis": "Databases & Query",
    "Firebase": "Cloud & DevOps",
    # Cloud & Tools
    "Git": "Tools & Version Control",
    "GitHub": "Tools & Version Control",
    "Docker": "DevOps & Cloud",
    "Kubernetes": "DevOps & Cloud",
    "AWS": "DevOps & Cloud",
    "GCP": "DevOps & Cloud",
    "Azure": "DevOps & Cloud",
    "Linux": "Systems & OS",
    "CI/CD": "DevOps & Cloud"
}

def extract_text_from_pdf(pdf_path):
    """Extract raw text from PDF using pypdf."""
    text = ""
    try:
        reader = pypdf.PdfReader(pdf_path)
        for page in reader.pages:
            t = page.extract_text()
            if t:
                text += t + "\n"
    except Exception as e:
        print(f"Error reading PDF {pdf_path}: {e}")
    return text.strip()

def extract_text_from_docx(docx_path):
    """Extract raw text from DOCX using python-docx."""
    text = ""
    try:
        doc = docx.Document(docx_path)
        for para in doc.paragraphs:
            if para.text:
                text += para.text + "\n"
        for table in doc.tables:
            for row in table.rows:
                row_text = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                if row_text:
                    text += " | ".join(row_text) + "\n"
    except Exception as e:
        print(f"Error reading DOCX {docx_path}: {e}")
    return text.strip()

def extract_contact_info(text):
    """Extract name, email, phone, github, linkedin from resume text."""
    # Email regex
    email_match = re.search(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text)
    email = email_match.group(0) if email_match else ""

    # Phone regex
    phone_match = re.search(r'(?:(?:\+?1\s*(?:[.-]\s*)?)?(?:\(\s*([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9])\s*\)|([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9]))\s*(?:[.-]\s*)?)?([2-9]1[02-9]|[2-9][02-9]1|[2-9][02-9]{2})\s*(?:[.-]\s*)?([0-9]{4})(?:\s*(?:#|x\.?|ext\.?|extension)\s*(\d+))?|(?:\+91[\-\s]?)?[6789]\d{9}', text)
    phone = phone_match.group(0).strip() if phone_match else ""

    # GitHub regex
    github_match = re.search(r'(?:https?:\/\/)?(?:www\.)?github\.com\/([a-zA-Z0-9_-]+)', text, re.IGNORECASE)
    github = f"github.com/{github_match.group(1)}" if github_match else ""

    # LinkedIn regex
    linkedin_match = re.search(r'(?:https?:\/\/)?(?:www\.)?linkedin\.com\/in\/([a-zA-Z0-9_-]+)', text, re.IGNORECASE)
    linkedin = f"linkedin.com/in/{linkedin_match.group(1)}" if linkedin_match else ""

    # Name heuristic: First non-empty line without special characters or keywords
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    name = "Student Candidate"
    for line in lines[:5]:
        if "@" in line or "http" in line or "github" in line or "resume" in line.lower() or "curriculum" in line.lower():
            continue
        cleaned = re.sub(r'[^a-zA-Z\s]', '', line).strip()
        words = cleaned.split()
        if 2 <= len(words) <= 4 and all(w[0].isupper() for w in words if w):
            name = cleaned
            break

    return {
        "name": name,
        "email": email,
        "phone": phone,
        "github": github,
        "linkedin": linkedin
    }

def split_into_sections(text):
    """Segment resume text into standard sections based on common headings."""
    heading_patterns = {
        "education": r'\b(education|academic background|qualifications|academic details)\b',
        "skills": r'\b(technical skills|skills|technologies|core competencies|tools & technologies|skill set)\b',
        "projects": r'\b(projects|academic projects|key projects|personal projects|technical projects)\b',
        "experience": r'\b(experience|work experience|professional experience|employment history|internships)\b',
        "certifications": r'\b(certifications|certificates|licenses & certifications|training & certifications)\b',
        "achievements": r'\b(achievements|honors & awards|awards|extracurricular activities|coding profiles)\b',
        "summary": r'\b(summary|professional summary|career objective|about me|profile)\b'
    }

    lines = text.split("\n")
    sections = {k: [] for k in heading_patterns}
    current_section = "summary"

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        matched_section = None
        # Check if line looks like a header (short, matches section keyword)
        if len(stripped.split()) <= 5:
            for sec_key, pattern in heading_patterns.items():
                if re.fullmatch(pattern, stripped, flags=re.IGNORECASE) or re.search(r'^[#*_\-\s]*' + pattern + r'[:\s*_\-]*$', stripped, flags=re.IGNORECASE):
                    matched_section = sec_key
                    break

        if matched_section:
            current_section = matched_section
        else:
            sections[current_section].append(stripped)

    # Convert line lists to text blocks
    return {k: "\n".join(v) for k, v in sections.items()}

def extract_skills_from_text(text):
    """Detect skills from text using taxonomy and regex matching."""
    detected = []
    text_lower = f" {text.lower()} "
    # Replace punctuation with spaces for whole-word search, preserving special characters like c++, c#, .net
    normalized = re.sub(r'[,|/()\[\]•\-]', ' ', text_lower)

    for skill, category in COMMON_SKILLS.items():
        pattern = r'\b' + re.escape(skill.lower()) + r'\b'
        # Special cases for C++, C#, .NET
        if skill.lower() in ['c++', 'c#']:
            pattern = re.escape(skill.lower())

        if re.search(pattern, normalized) or re.search(pattern, text_lower):
            detected.append({"name": skill, "category": category})

    # Deduplicate by name
    seen = set()
    unique_skills = []
    for s in detected:
        if s["name"].lower() not in seen:
            seen.add(s["name"].lower())
            unique_skills.append(s)

    return unique_skills

def parse_projects_section(text):
    """Extract project items from projects section text."""
    projects = []
    if not text.strip():
        return projects

    lines = [l.strip() for l in text.split("\n") if l.strip()]
    current_proj = None

    for line in lines:
        is_bullet = bool(re.match(r'^[•\-\*\u2022\u25cf\u2013]\s*', line))
        cleaned = re.sub(r'^[•\-\*\u2022\u25cf\u2013]\s*', '', line).strip()

        # Check if line looks like a new project title
        is_new_title = False
        if not is_bullet:
            if "|" in line or " - " in line or ":" in line:
                is_new_title = True
            elif current_proj is None:
                is_new_title = True
            elif len(line.split()) <= 7 and not line.endswith('.'):
                is_new_title = True

        if is_new_title:
            if current_proj:
                projects.append(current_proj)
            
            title = cleaned
            technologies = ""
            if "|" in cleaned:
                parts = cleaned.split("|", 1)
                title = parts[0].strip()
                technologies = parts[1].strip()
            elif " - " in cleaned:
                parts = cleaned.split(" - ", 1)
                title = parts[0].strip()
                technologies = parts[1].strip()
            elif ":" in cleaned and len(cleaned.split(":")[0].split()) <= 4:
                parts = cleaned.split(":", 1)
                title = parts[0].strip()
                technologies = parts[1].strip()

            current_proj = {
                "title": title.strip("#* "),
                "technologies": technologies,
                "description": "",
                "github_url": ""
            }
        else:
            if current_proj is not None:
                gh_match = re.search(r'(?:https?:\/\/)?(?:www\.)?github\.com\/[^\s\)]+', cleaned)
                if gh_match and not current_proj["github_url"]:
                    url = gh_match.group(0)
                    current_proj["github_url"] = url if url.startswith("http") else f"https://{url}"

                if current_proj["description"]:
                    current_proj["description"] += " " + cleaned
                else:
                    current_proj["description"] = cleaned
            else:
                current_proj = {
                    "title": cleaned[:40],
                    "technologies": "",
                    "description": cleaned,
                    "github_url": ""
                }

    if current_proj:
        projects.append(current_proj)

    # Secondary cleanup: extract tech from description if technologies is empty
    for p in projects:
        if not p["technologies"] and p["description"]:
            tech_found = [s["name"] for s in extract_skills_from_text(p["description"])]
            p["technologies"] = ", ".join(tech_found[:6])

    return projects

def parse_education_section(text):
    """Extract education entries."""
    educations = []
    if not text.strip():
        return educations

    lines = [l.strip() for l in text.split("\n") if l.strip()]
    current_edu = {}

    degree_patterns = r'\b(B\.?Tech|B\.?E\.?|B\.?S\.?|Bachelor|M\.?Tech|M\.?S\.?|Master|Diploma|High School|Secondary)\b'

    for line in lines:
        cleaned_line = re.sub(r'^[•\-\*]\s*', '', line)
        if re.search(degree_patterns, cleaned_line, flags=re.IGNORECASE):
            if current_edu:
                educations.append(current_edu)
                current_edu = {}
            current_edu["degree"] = cleaned_line
        elif any(kw in cleaned_line.lower() for kw in ["university", "college", "institute", "school", "academy"]):
            if "institution" not in current_edu:
                current_edu["institution"] = cleaned_line
            else:
                if current_edu:
                    educations.append(current_edu)
                current_edu = {"institution": cleaned_line}
        elif re.search(r'\b(20\d\d|19\d\d)\b', cleaned_line):
            year_match = re.search(r'\b(20\d\d|19\d\d)\b', cleaned_line)
            current_edu["year"] = year_match.group(0) if year_match else ""
        elif "gpa" in cleaned_line.lower() or "cgpa" in cleaned_line.lower() or "%" in cleaned_line:
            current_edu["gpa"] = cleaned_line

    if current_edu:
        educations.append(current_edu)

    if not educations and lines:
        educations.append({
            "institution": lines[0],
            "degree": lines[1] if len(lines) > 1 else "Degree",
            "year": "2024",
            "gpa": ""
        })

    return educations

def parse_certifications_section(text):
    """Extract certifications."""
    certs = []
    if not text.strip():
        return certs

    for line in text.split("\n"):
        cleaned = re.sub(r'^[•\-\*]\s*', '', line).strip()
        if len(cleaned) > 3:
            issuer = ""
            name = cleaned
            if " - " in cleaned:
                parts = cleaned.split(" - ")
                name = parts[0].strip()
                issuer = parts[1].strip()
            elif " by " in cleaned.lower():
                parts = re.split(r'\s+by\s+', cleaned, flags=re.IGNORECASE)
                name = parts[0].strip()
                issuer = parts[1].strip()
            elif " from " in cleaned.lower():
                parts = re.split(r'\s+from\s+', cleaned, flags=re.IGNORECASE)
                name = parts[0].strip()
                issuer = parts[1].strip()

            certs.append({
                "name": name,
                "issuer": issuer,
                "issue_date": ""
            })
    return certs

def parse_experience_section(text):
    """Extract internships or work experience."""
    experiences = []
    if not text.strip():
        return experiences

    blocks = re.split(r'\n\s*\n', text)
    for b in blocks:
        lines = [l.strip() for l in b.split("\n") if l.strip()]
        if not lines:
            continue
        role_company = lines[0]
        role = role_company
        company = ""
        duration = ""
        if " at " in role_company.lower():
            parts = re.split(r'\s+at\s+', role_company, flags=re.IGNORECASE)
            role = parts[0].strip()
            company = parts[1].strip()
        elif " - " in role_company:
            parts = role_company.split(" - ")
            role = parts[0].strip()
            company = parts[1].strip()

        # Find duration
        desc_lines = []
        for l in lines[1:]:
            if re.search(r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|20\d\d)\b', l) and not duration:
                duration = l
            else:
                desc_lines.append(re.sub(r'^[•\-\*]\s*', '', l))

        experiences.append({
            "role": role,
            "company": company,
            "duration": duration,
            "description": " ".join(desc_lines)
        })
    return experiences

def parse_achievements_section(text):
    """Extract achievement bullet points."""
    achievements = []
    if not text.strip():
        return achievements
    for line in text.split("\n"):
        cleaned = re.sub(r'^[•\-\*]\s*', '', line).strip()
        if len(cleaned) > 5:
            achievements.append(cleaned)
    return achievements

def parse_resume(file_path_or_text, is_raw_text=False):
    """Main parsing orchestrator. Extracts text and parses into structured dictionary."""
    raw_text = ""
    file_type = "text"

    if is_raw_text:
        raw_text = file_path_or_text
    else:
        ext = os.path.splitext(file_path_or_text)[1].lower()
        if ext == '.pdf':
            file_type = "pdf"
            raw_text = extract_text_from_pdf(file_path_or_text)
        elif ext in ['.docx', '.doc']:
            file_type = "docx"
            raw_text = extract_text_from_docx(file_path_or_text)
        else:
            file_type = "txt"
            with open(file_path_or_text, 'r', encoding='utf-8', errors='ignore') as f:
                raw_text = f.read()

    contact = extract_contact_info(raw_text)
    sections = split_into_sections(raw_text)

    # Extract skills from both the skills section and the entire resume
    skills_from_section = extract_skills_from_text(sections.get("skills", ""))
    skills_from_all = extract_skills_from_text(raw_text)
    
    # Merge skills
    seen_skills = set()
    merged_skills = []
    for s in skills_from_section + skills_from_all:
        if s["name"].lower() not in seen_skills:
            seen_skills.add(s["name"].lower())
            merged_skills.append(s)

    projects = parse_projects_section(sections.get("projects", ""))
    education = parse_education_section(sections.get("education", ""))
    experience = parse_experience_section(sections.get("experience", ""))
    certifications = parse_certifications_section(sections.get("certifications", ""))
    achievements = parse_achievements_section(sections.get("achievements", ""))

    summary = sections.get("summary", "").strip()
    if not summary and len(raw_text.split("\n")) > 0:
        # Heuristic: grab first 2-3 lines if they are not headers or contact
        first_lines = [l.strip() for l in raw_text.split("\n")[:6] if l.strip() and "@" not in l and not any(kw in l.lower() for kw in ["github", "linkedin", "phone"])]
        if len(first_lines) > 1:
            summary = " ".join(first_lines[1:3])

    parsed_result = {
        "name": contact["name"],
        "email": contact["email"],
        "phone": contact["phone"],
        "github": contact["github"],
        "linkedin": contact["linkedin"],
        "summary": summary,
        "skills": merged_skills,
        "education": education,
        "projects": projects,
        "experience": experience,
        "certifications": certifications,
        "achievements": achievements,
        "raw_text": raw_text,
        "file_type": file_type
    }

    return parsed_result
