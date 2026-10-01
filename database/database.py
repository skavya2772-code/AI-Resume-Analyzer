import sqlite3
import json
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'resume_analyzer.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # Users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Resumes table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS resumes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        original_filename TEXT,
        file_type TEXT,
        raw_text TEXT,
        parsed_data TEXT, -- JSON
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    )
    ''')

    # Skills table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS skills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        resume_id INTEGER,
        skill_name TEXT NOT NULL,
        category TEXT,
        verified_status TEXT DEFAULT 'unverified', -- 'verified' or 'unverified'
        evidence_source TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (resume_id) REFERENCES resumes (id) ON DELETE CASCADE
    )
    ''')

    # Projects table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        resume_id INTEGER,
        title TEXT NOT NULL,
        description TEXT,
        technologies TEXT,
        github_url TEXT,
        live_url TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (resume_id) REFERENCES resumes (id) ON DELETE CASCADE
    )
    ''')

    # Certifications table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS certifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        resume_id INTEGER,
        name TEXT NOT NULL,
        issuer TEXT,
        issue_date TEXT,
        credential_id TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (resume_id) REFERENCES resumes (id) ON DELETE CASCADE
    )
    ''')

    # Resume Versions table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS resume_versions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        resume_id INTEGER,
        version_name TEXT NOT NULL,
        target_role TEXT NOT NULL,
        formatted_resume TEXT NOT NULL, -- JSON
        ats_score INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (resume_id) REFERENCES resumes (id) ON DELETE CASCADE
    )
    ''')

    # Job Descriptions table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS job_descriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        target_role TEXT NOT NULL,
        company TEXT,
        raw_text TEXT NOT NULL,
        required_skills TEXT, -- JSON
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Analysis Results table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS analysis_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        resume_id INTEGER,
        target_role TEXT NOT NULL,
        job_description_id INTEGER,
        ats_score INTEGER,
        skill_match_score INTEGER,
        role_alignment_score INTEGER,
        structure_score INTEGER,
        evidence_strength_score INTEGER,
        matched_skills TEXT, -- JSON
        missing_skills TEXT, -- JSON
        weak_skills TEXT, -- JSON
        evidence_map TEXT, -- JSON
        improvements TEXT, -- JSON
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (resume_id) REFERENCES resumes (id) ON DELETE CASCADE,
        FOREIGN KEY (job_description_id) REFERENCES job_descriptions (id) ON DELETE SET NULL
    )
    ''')

    # Interview Sessions table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS interview_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        resume_id INTEGER,
        target_role TEXT NOT NULL,
        interview_type TEXT DEFAULT 'HR Interview',
        total_questions INTEGER DEFAULT 10,
        current_question_index INTEGER DEFAULT 0,
        overall_score INTEGER DEFAULT 0,
        status TEXT DEFAULT 'in_progress', -- 'in_progress', 'completed'
        report_data TEXT, -- JSON
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (resume_id) REFERENCES resumes (id) ON DELETE SET NULL
    )
    ''')

    # Interview Messages table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS interview_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER NOT NULL,
        question_number INTEGER NOT NULL,
        question_text TEXT NOT NULL,
        user_answer TEXT,
        feedback_data TEXT, -- JSON
        score INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (session_id) REFERENCES interview_sessions (id) ON DELETE CASCADE
    )
    ''')

    # Career Roadmaps table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS career_roadmaps (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        resume_id INTEGER,
        target_role TEXT NOT NULL,
        timeline TEXT DEFAULT '6 Months',
        current_level TEXT DEFAULT 'Student / Fresher',
        roadmap_data TEXT NOT NULL, -- JSON
        progress_percent INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (resume_id) REFERENCES resumes (id) ON DELETE SET NULL
    )
    ''')

    conn.commit()
    conn.close()

# Helper DB Operations

def insert_resume(filename, file_type, raw_text, parsed_data, user_email=None, user_name=None):
    conn = get_db()
    cursor = conn.cursor()
    user_id = None

    if user_email:
        cursor.execute("SELECT id FROM users WHERE email = ?", (user_email,))
        row = cursor.fetchone()
        if row:
            user_id = row['id']
        else:
            cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)", (user_name or "Student", user_email))
            user_id = cursor.lastrowid

    cursor.execute('''
    INSERT INTO resumes (user_id, original_filename, file_type, raw_text, parsed_data)
    VALUES (?, ?, ?, ?, ?)
    ''', (user_id, filename, file_type, raw_text, json.dumps(parsed_data)))
    resume_id = cursor.lastrowid

    # Populate normalized sub-tables if parsed_data has them
    if parsed_data:
        # Skills
        for sk in parsed_data.get('skills', []):
            name = sk if isinstance(sk, str) else sk.get('name', '')
            cat = sk.get('category', 'Technical') if isinstance(sk, dict) else 'Technical'
            cursor.execute('''
            INSERT INTO skills (resume_id, skill_name, category)
            VALUES (?, ?, ?)
            ''', (resume_id, name, cat))

        # Projects
        for proj in parsed_data.get('projects', []):
            if isinstance(proj, dict):
                cursor.execute('''
                INSERT INTO projects (resume_id, title, description, technologies, github_url)
                VALUES (?, ?, ?, ?, ?)
                ''', (
                    resume_id,
                    proj.get('title', 'Untitled Project'),
                    proj.get('description', ''),
                    proj.get('technologies', ''),
                    proj.get('github_url', '')
                ))

        # Certifications
        for cert in parsed_data.get('certifications', []):
            if isinstance(cert, dict):
                cursor.execute('''
                INSERT INTO certifications (resume_id, name, issuer, issue_date)
                VALUES (?, ?, ?, ?)
                ''', (
                    resume_id,
                    cert.get('name', 'Certification'),
                    cert.get('issuer', ''),
                    cert.get('issue_date', '')
                ))
            elif isinstance(cert, str):
                cursor.execute('''
                INSERT INTO certifications (resume_id, name)
                VALUES (?, ?)
                ''', (resume_id, cert))

    conn.commit()
    conn.close()
    return resume_id

def get_resume(resume_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM resumes WHERE id = ?", (resume_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None

    resume = dict(row)
    if resume.get('parsed_data'):
        try:
            resume['parsed_data'] = json.loads(resume['parsed_data'])
        except Exception:
            pass

    # Fetch skills
    cursor.execute("SELECT * FROM skills WHERE resume_id = ?", (resume_id,))
    resume['skills_list'] = [dict(r) for r in cursor.fetchall()]

    # Fetch projects
    cursor.execute("SELECT * FROM projects WHERE resume_id = ?", (resume_id,))
    resume['projects_list'] = [dict(r) for r in cursor.fetchall()]

    # Fetch certifications
    cursor.execute("SELECT * FROM certifications WHERE resume_id = ?", (resume_id,))
    resume['certifications_list'] = [dict(r) for r in cursor.fetchall()]

    conn.close()
    return resume

def update_resume_parsed_data(resume_id, parsed_data):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
    UPDATE resumes 
    SET parsed_data = ?, updated_at = CURRENT_TIMESTAMP
    WHERE id = ?
    ''', (json.dumps(parsed_data), resume_id))
    conn.commit()
    conn.close()

def save_analysis_result(resume_id, target_role, analysis, job_desc_id=None):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO analysis_results (
        resume_id, target_role, job_description_id,
        ats_score, skill_match_score, role_alignment_score,
        structure_score, evidence_strength_score,
        matched_skills, missing_skills, weak_skills,
        evidence_map, improvements
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        resume_id,
        target_role,
        job_desc_id,
        analysis.get('ats_score', 0),
        analysis.get('skill_match', 0),
        analysis.get('role_alignment', 0),
        analysis.get('structure_score', 0),
        analysis.get('evidence_strength', 0),
        json.dumps(analysis.get('matched_skills', [])),
        json.dumps(analysis.get('missing_skills', [])),
        json.dumps(analysis.get('weak_skills', [])),
        json.dumps(analysis.get('evidence_map', [])),
        json.dumps(analysis.get('improvements', []))
    ))
    analysis_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return analysis_id

def get_latest_analysis(resume_id, target_role=None):
    conn = get_db()
    cursor = conn.cursor()
    if target_role:
        cursor.execute('''
        SELECT * FROM analysis_results 
        WHERE resume_id = ? AND target_role = ? 
        ORDER BY created_at DESC LIMIT 1
        ''', (resume_id, target_role))
    else:
        cursor.execute('''
        SELECT * FROM analysis_results 
        WHERE resume_id = ? 
        ORDER BY created_at DESC LIMIT 1
        ''', (resume_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    res = dict(row)
    for field in ['matched_skills', 'missing_skills', 'weak_skills', 'evidence_map', 'improvements']:
        if res.get(field):
            try:
                res[field] = json.loads(res[field])
            except Exception:
                pass
    return res

def save_resume_version(resume_id, version_name, target_role, formatted_resume, ats_score=None):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO resume_versions (resume_id, version_name, target_role, formatted_resume, ats_score)
    VALUES (?, ?, ?, ?, ?)
    ''', (resume_id, version_name, target_role, json.dumps(formatted_resume), ats_score))
    version_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return version_id

def get_resume_versions(resume_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT * FROM resume_versions WHERE resume_id = ? ORDER BY created_at DESC
    ''', (resume_id,))
    rows = cursor.fetchall()
    conn.close()
    results = []
    for r in rows:
        v = dict(r)
        if v.get('formatted_resume'):
            try:
                v['formatted_resume'] = json.loads(v['formatted_resume'])
            except Exception:
                pass
        results.append(v)
    return results

def get_version_by_id(version_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM resume_versions WHERE id = ?', (version_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    v = dict(row)
    if v.get('formatted_resume'):
        try:
            v['formatted_resume'] = json.loads(v['formatted_resume'])
        except Exception:
            pass
    return v

def save_job_description(target_role, raw_text, required_skills=None, company=None):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO job_descriptions (target_role, company, raw_text, required_skills)
    VALUES (?, ?, ?, ?)
    ''', (target_role, company, raw_text, json.dumps(required_skills or [])))
    job_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return job_id

# -------------------------------------------------------------
# Interview Sessions DB Helpers
# -------------------------------------------------------------

def create_interview_session(resume_id, target_role, interview_type='HR Interview', total_questions=10):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO interview_sessions (resume_id, target_role, interview_type, total_questions, current_question_index, status)
    VALUES (?, ?, ?, ?, 0, 'in_progress')
    ''', (resume_id, target_role, interview_type, total_questions))
    session_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return session_id

def get_interview_session(session_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM interview_sessions WHERE id = ?', (session_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    sess = dict(row)
    if sess.get('report_data'):
        try:
            sess['report_data'] = json.loads(sess['report_data'])
        except Exception:
            pass
    return sess

def add_interview_message(session_id, question_number, question_text, user_answer=None, feedback=None, score=None):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO interview_messages (session_id, question_number, question_text, user_answer, feedback_data, score)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        session_id,
        question_number,
        question_text,
        user_answer,
        json.dumps(feedback) if feedback else None,
        score
    ))
    message_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return message_id

def update_interview_message_answer(message_id, user_answer, feedback_data, score):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
    UPDATE interview_messages
    SET user_answer = ?, feedback_data = ?, score = ?
    WHERE id = ?
    ''', (user_answer, json.dumps(feedback_data), score, message_id))
    conn.commit()
    conn.close()

def get_interview_messages(session_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM interview_messages WHERE session_id = ? ORDER BY question_number ASC', (session_id,))
    rows = cursor.fetchall()
    conn.close()
    messages = []
    for r in rows:
        m = dict(r)
        if m.get('feedback_data'):
            try:
                m['feedback_data'] = json.loads(m['feedback_data'])
            except Exception:
                pass
        messages.append(m)
    return messages

def complete_interview_session(session_id, overall_score, report_data):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
    UPDATE interview_sessions
    SET status = 'completed', overall_score = ?, report_data = ?, current_question_index = total_questions
    WHERE id = ?
    ''', (overall_score, json.dumps(report_data), session_id))
    conn.commit()
    conn.close()

def get_user_interviews(resume_id=None):
    conn = get_db()
    cursor = conn.cursor()
    if resume_id:
        cursor.execute('SELECT * FROM interview_sessions WHERE resume_id = ? ORDER BY created_at DESC', (resume_id,))
    else:
        cursor.execute('SELECT * FROM interview_sessions ORDER BY created_at DESC')
    rows = cursor.fetchall()
    conn.close()
    res = []
    for r in rows:
        d = dict(r)
        if d.get('report_data'):
            try:
                d['report_data'] = json.loads(d['report_data'])
            except Exception:
                pass
        res.append(d)
    return res

# -------------------------------------------------------------
# Career Roadmaps DB Helpers
# -------------------------------------------------------------

def save_career_roadmap(resume_id, target_role, timeline, roadmap_data, current_level='Student / Fresher'):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO career_roadmaps (resume_id, target_role, timeline, current_level, roadmap_data, progress_percent)
    VALUES (?, ?, ?, ?, ?, 0)
    ''', (resume_id, target_role, timeline, current_level, json.dumps(roadmap_data)))
    roadmap_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return roadmap_id

def get_career_roadmap(roadmap_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM career_roadmaps WHERE id = ?', (roadmap_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    rm = dict(row)
    if rm.get('roadmap_data'):
        try:
            rm['roadmap_data'] = json.loads(rm['roadmap_data'])
        except Exception:
            pass
    return rm

def get_latest_career_roadmap(resume_id=None, target_role=None):
    conn = get_db()
    cursor = conn.cursor()
    query = 'SELECT * FROM career_roadmaps WHERE 1=1'
    params = []
    if resume_id:
        query += ' AND resume_id = ?'
        params.append(resume_id)
    if target_role:
        query += ' AND target_role = ?'
        params.append(target_role)
    query += ' ORDER BY created_at DESC LIMIT 1'
    cursor.execute(query, tuple(params))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    rm = dict(row)
    if rm.get('roadmap_data'):
        try:
            rm['roadmap_data'] = json.loads(rm['roadmap_data'])
        except Exception:
            pass
    return rm

def update_roadmap_progress(roadmap_id, progress_percent, roadmap_data=None):
    conn = get_db()
    cursor = conn.cursor()
    if roadmap_data is not None:
        cursor.execute('''
        UPDATE career_roadmaps
        SET progress_percent = ?, roadmap_data = ?
        WHERE id = ?
        ''', (progress_percent, json.dumps(roadmap_data), roadmap_id))
    else:
        cursor.execute('''
        UPDATE career_roadmaps
        SET progress_percent = ?
        WHERE id = ?
        ''', (progress_percent, roadmap_id))
    conn.commit()
    conn.close()

def get_user_roadmaps(resume_id=None):
    conn = get_db()
    cursor = conn.cursor()
    if resume_id:
        cursor.execute('SELECT * FROM career_roadmaps WHERE resume_id = ? ORDER BY created_at DESC', (resume_id,))
    else:
        cursor.execute('SELECT * FROM career_roadmaps ORDER BY created_at DESC')
    rows = cursor.fetchall()
    conn.close()
    results = []
    for r in rows:
        d = dict(r)
        if d.get('roadmap_data'):
            try:
                d['roadmap_data'] = json.loads(d['roadmap_data'])
            except Exception:
                pass
        results.append(d)
    return results
