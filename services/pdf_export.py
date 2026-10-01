import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, ListFlowable, ListItem
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT

def generate_pdf_resume(resume_data, output_path):
    """
    Generate an ATS-compliant, professionally formatted PDF resume using ReportLab.
    """
    # 0.5 in (36 points) margins for ATS standards
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom ATS Typography Styles
    name_style = ParagraphStyle(
        'ResumeName',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#111827')
    )

    contact_style = ParagraphStyle(
        'ResumeContact',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#4B5563')
    )

    section_heading_style = ParagraphStyle(
        'ResumeSectionHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        alignment=TA_LEFT,
        textColor=colors.HexColor('#1F2937'),
        spaceBefore=8,
        spaceAfter=3
    )

    item_title_style = ParagraphStyle(
        'ResumeItemTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor('#111827')
    )

    item_subtitle_style = ParagraphStyle(
        'ResumeItemSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9.5,
        leading=12,
        textColor=colors.HexColor('#4B5563')
    )

    body_style = ParagraphStyle(
        'ResumeBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor('#374151')
    )

    bullet_style = ParagraphStyle(
        'ResumeBullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12.5,
        textColor=colors.HexColor('#374151')
    )

    story = []

    contact = resume_data.get('contact', {})
    name = contact.get('name') or resume_data.get('name') or "Candidate Name"
    story.append(Paragraph(name.upper(), name_style))
    story.append(Spacer(1, 4))

    # Contact Info Bar
    contact_parts = []
    if contact.get('email'):
        contact_parts.append(contact.get('email'))
    if contact.get('phone'):
        contact_parts.append(contact.get('phone'))
    if contact.get('linkedin'):
        contact_parts.append(contact.get('linkedin'))
    if contact.get('github'):
        contact_parts.append(contact.get('github'))
    
    if contact_parts:
        contact_text = "  |  ".join(contact_parts)
        story.append(Paragraph(contact_text, contact_style))
    story.append(Spacer(1, 6))

    def add_section_header(title):
        story.append(Paragraph(title.upper(), section_heading_style))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#9CA3AF'), spaceAfter=5, spaceBefore=1))

    # 1. Professional Summary
    summary = resume_data.get('summary')
    if summary:
        add_section_header("Professional Summary")
        story.append(Paragraph(summary, body_style))
        story.append(Spacer(1, 6))

    # 2. Technical Skills
    skills_data = resume_data.get('skills', {})
    if skills_data:
        add_section_header("Technical Skills")
        if isinstance(skills_data, dict):
            for cat, s_list in skills_data.items():
                if s_list:
                    skill_str = f"<b>{cat}:</b> {', '.join(s_list)}"
                    story.append(Paragraph(skill_str, body_style))
                    story.append(Spacer(1, 2))
        elif isinstance(skills_data, list):
            names = [s if isinstance(s, str) else s.get('name', '') for s in skills_data]
            story.append(Paragraph(f"<b>Skills:</b> {', '.join(names)}", body_style))
        story.append(Spacer(1, 4))

    # 3. Technical Projects
    projects = resume_data.get('projects', [])
    if projects:
        add_section_header("Technical Projects")
        for proj in projects:
            p_title = proj.get('title', 'Project')
            p_tech = proj.get('technologies', '')
            p_desc = proj.get('description', '')
            p_gh = proj.get('github_url', '')

            header_text = f"<b>{p_title}</b>"
            if p_tech:
                header_text += f" | <i>{p_tech}</i>"
            if p_gh:
                header_text += f" | <font color='#2563EB'>{p_gh}</font>"

            story.append(Paragraph(header_text, item_title_style))
            if p_desc:
                story.append(Paragraph(f"• {p_desc}", bullet_style))
            story.append(Spacer(1, 4))

    # 4. Experience / Internships
    experience = resume_data.get('experience', [])
    if experience:
        add_section_header("Experience & Internships")
        for exp in experience:
            role = exp.get('role', 'Role')
            company = exp.get('company', '')
            duration = exp.get('duration', '')
            desc = exp.get('description', '')

            exp_line = f"<b>{role}</b>"
            if company:
                exp_line += f" – {company}"
            if duration:
                exp_line += f" ({duration})"

            story.append(Paragraph(exp_line, item_title_style))
            if desc:
                story.append(Paragraph(f"• {desc}", bullet_style))
            story.append(Spacer(1, 4))

    # 5. Education
    education = resume_data.get('education', [])
    if education:
        add_section_header("Education")
        for edu in education:
            degree = edu.get('degree', 'Degree')
            inst = edu.get('institution', 'University')
            year = edu.get('year', '')
            gpa = edu.get('gpa', '')

            edu_line = f"<b>{degree}</b> – {inst}"
            extra = []
            if year:
                extra.append(year)
            if gpa:
                extra.append(f"GPA: {gpa}")
            if extra:
                edu_line += f" ({', '.join(extra)})"

            story.append(Paragraph(edu_line, item_title_style))
            story.append(Spacer(1, 2))
        story.append(Spacer(1, 4))

    # 6. Certifications
    certifications = resume_data.get('certifications', [])
    if certifications:
        add_section_header("Certifications")
        for cert in certifications:
            c_name = cert if isinstance(cert, str) else cert.get('name', '')
            issuer = cert.get('issuer', '') if isinstance(cert, dict) else ''
            c_text = f"• <b>{c_name}</b>"
            if issuer:
                c_text += f" – {issuer}"
            story.append(Paragraph(c_text, body_style))
            story.append(Spacer(1, 2))
        story.append(Spacer(1, 4))

    # 7. Key Achievements & Coding Evidence
    achievements = resume_data.get('achievements', [])
    if achievements:
        add_section_header("Achievements & Coding Performance")
        for ach in achievements:
            story.append(Paragraph(f"• {ach}", bullet_style))
            story.append(Spacer(1, 2))

    doc.build(story)
    return output_path
