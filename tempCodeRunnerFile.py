import os

from flask import Flask, render_template, request, jsonify, send_file

from database.database import (
    init_db,
    insert_resume,
    get_resume,
    update_resume_parsed_data,
    save_analysis_result,
    get_latest_analysis,
    save_resume_version,
    get_resume_versions,
    get_version_by_id,
    save_job_description
)

from services.resume_parser import parse_resume

from services.ai_service import (
    analyze_resume_ai,
    generate_resume_doctor
)

from services.analyzer import (
    ROLE_PROFILES,
    parse_job_description_skills
)

from services.resume_generator import (
    generate_role_tailored_resume
)

from services.pdf_export import (
    generate_pdf_resume
)


app = Flask(__name__)

init_db()


# =========================================================
# HOME
# =========================================================

@app.route('/')
def home():
    return render_template(
        'index.html',
        roles=ROLE_PROFILES
    )


# =========================================================
# UPLOAD PAGE
# =========================================================

@app.route('/upload')
def upload_page():
    return render_template(
        'upload.html',
        roles=ROLE_PROFILES
    )


# =========================================================
# ANALYZER PAGE
# =========================================================

@app.route('/analyze')
def analyze_page():

    resume_id = request.args.get('resume_id')

    return render_template(
        'analyze.html',
        resume_id=resume_id,
        roles=ROLE_PROFILES
    )


# =========================================================
# BUILDER PAGE
# =========================================================

@app.route('/builder')
def builder_page():

    resume_id = request.args.get('resume_id')

    return render_template(
        'builder.html',
        resume_id=resume_id,
        roles=ROLE_PROFILES
    )


# =========================================================
# PREVIEW PAGE
# =========================================================

@app.route('/preview')
def preview_page():

    resume_id = request.args.get('resume_id')

    return render_template(
        'preview.html',
        resume_id=resume_id,
        roles=ROLE_PROFILES
    )


# =========================================================
# VERSIONS PAGE
# =========================================================

@app.route('/versions')
def versions_page():

    resume_id = request.args.get('resume_id')

    return render_template(
        'versions.html',
        resume_id=resume_id,
        roles=ROLE_PROFILES
    )


# =========================================================
# RESUME DOCTOR PAGE
# =========================================================

@app.route('/resume-doctor')
def resume_doctor_page():

    return render_template(
        'resume_doctor.html',
        roles=ROLE_PROFILES
    )


# =========================================================
# UPLOAD RESUME API
# ONLY ACTUAL RESUMES ARE ACCEPTED
# =========================================================

@app.route('/api/upload-resume', methods=['POST'])
def api_upload_resume():

    try:

        # -------------------------------------------------
        # CHECK FILE
        # -------------------------------------------------

        if 'resume' not in request.files:

            return jsonify({
                'success': False,
                'error': 'Please upload a resume.'
            }), 400


        file = request.files['resume']


        if not file.filename:

            return jsonify({
                'success': False,
                'error': 'Please select a resume file.'
            }), 400


        # -------------------------------------------------
        # CHECK FILE TYPE
        # -------------------------------------------------

        filename = file.filename.lower()

        if not filename.endswith(('.pdf', '.docx')):

            return jsonify({
                'success': False,
                'error': (
                    'Only PDF and DOCX resume files are supported.'
                )
            }), 400


        # -------------------------------------------------
        # CREATE UPLOAD FOLDER
        # -------------------------------------------------

        upload_dir = os.path.join(
            os.getcwd(),
            'uploads'
        )

        os.makedirs(
            upload_dir,
            exist_ok=True
        )


        # -------------------------------------------------
        # SAVE FILE
        # -------------------------------------------------

        filepath = os.path.join(
            upload_dir,
            file.filename
        )

        file.save(filepath)


        # -------------------------------------------------
        # PARSE RESUME
        # -------------------------------------------------

        try:

            parsed_data = parse_resume(
                filepath
            )

        except Exception:

            if os.path.exists(filepath):
                os.remove(filepath)

            return jsonify({
                'success': False,
                'error': (
                    'This document could not be read. '
                    'Please upload a valid resume.'
                )
            }), 400


        # -------------------------------------------------
        # CHECK PARSED DATA
        # -------------------------------------------------

        if not parsed_data:

            if os.path.exists(filepath):
                os.remove(filepath)

            return jsonify({
                'success': False,
                'error': (
                    'No readable resume information was found. '
                    'Please upload your actual resume.'
                )
            }), 400


        # -------------------------------------------------
        # EXTRACT TEXT
        # -------------------------------------------------

        resume_text_parts = []


        for key, value in parsed_data.items():

            if value is None:
                continue


            if isinstance(value, list):

                for item in value:

                    if isinstance(item, dict):

                        for item_value in item.values():

                            if item_value is not None:

                                resume_text_parts.append(
                                    str(item_value)
                                )

                    else:

                        resume_text_parts.append(
                            str(item)
                        )


            elif isinstance(value, dict):

                for item_value in value.values():

                    if item_value is not None:

                        resume_text_parts.append(
                            str(item_value)
                        )


            else:

                resume_text_parts.append(
                    str(value)
                )


        resume_text = ' '.join(
            resume_text_parts
        ).lower()


        # -------------------------------------------------
        # RESUME SECTION KEYWORDS
        # -------------------------------------------------

        resume_sections = {

            'contact': [
                'email',
                'phone',
                'mobile',
                'linkedin',
                'github'
            ],

            'education': [
                'education',
                'academic',
                'qualification',
                'degree',
                'university',
                'college',
                'school'
            ],

            'skills': [
                'skills',
                'technical skills',
                'technologies',
                'programming languages',
                'tools'
            ],

            'projects': [
                'projects',
                'project',
                'academic projects',
                'personal projects'
            ],

            'experience': [
                'experience',
                'work experience',
                'professional experience',
                'employment'
            ],

            'certifications': [
                'certification',
                'certifications',
                'courses'
            ],

            'achievements': [
                'achievement',
                'achievements',
                'awards'
            ],

            'profile': [
                'summary',
                'objective',
                'profile',
                'about me',
                'career objective'
            ]

        }


        # -------------------------------------------------
        # DETECT RESUME SECTIONS
        # -------------------------------------------------

        detected_sections = []


        for section, keywords in resume_sections.items():

            for keyword in keywords:

                if keyword in resume_text:

                    detected_sections.append(
                        section
                    )

                    break


        detected_sections = list(
            set(detected_sections)
        )


        # -------------------------------------------------
        # RESUME STRUCTURE
        # -------------------------------------------------

        has_contact = (
            'contact' in detected_sections
        )

        has_education = (
            'education' in detected_sections
        )

        has_skills = (
            'skills' in detected_sections
        )

        has_projects = (
            'projects' in detected_sections
        )

        has_experience = (
            'experience' in detected_sections
        )

        has_profile = (
            'profile' in detected_sections
        )


        # -------------------------------------------------
        # RESUME VALIDATION
        # -------------------------------------------------

        valid_resume = (

            has_contact

            and has_education

            and (
                has_skills
                or has_projects
                or has_experience
                or has_profile
            )

        )


        # -------------------------------------------------
        # REJECT NON-RESUME DOCUMENT
        # -------------------------------------------------

        if not valid_resume:

            if os.path.exists(filepath):
                os.remove(filepath)

            return jsonify({
                'success': False,
                'error': (
                    'This document is not recognized as a resume. '
                    'Please upload your actual resume containing '
                    'Contact Information, Education, Skills, '
                    'Projects, or Experience.'
                )
            }), 400


        # -------------------------------------------------
        # SAVE VALID RESUME
        # -------------------------------------------------

        resume_id = insert_resume(
            file.filename,
            parsed_data
        )


        # -------------------------------------------------
        # SUCCESS
        # -------------------------------------------------

        return jsonify({

            'success': True,

            'message': 'Resume uploaded successfully.',

            'resume_id': resume_id,

            'filename': file.filename,

            'parsed_data': parsed_data,

            'detected_sections': detected_sections

        })


    except Exception as e:

        return jsonify({

            'success': False,

            'error': (
                'Resume upload failed: '
                + str(e)
            )

        }), 500


# =========================================================
# ANALYZE RESUME API
# =========================================================

@app.route('/api/analyze-resume', methods=['POST'])
def api_analyze_resume():

    try:

        data = request.get_json() or {}

        resume_id = data.get('resume_id')

        target_role = data.get(
            'target_role',
            'Frontend Developer'
        )

        job_description = data.get(
            'job_description',
            ''
        ).strip()


        if not resume_id:

            return jsonify({
                'success': False,
                'error': 'Missing resume_id'
            }), 400


        resume = get_resume(
            resume_id
        )


        if not resume:

            return jsonify({
                'success': False,
                'error': 'Resume not found'
            }), 404


        parsed_data = resume.get(
            'parsed_data'
        ) or {}


        result = analyze_resume_ai(
            parsed_data,
            target_role,
            job_description
        )


        save_analysis_result(
            resume_id,
            result
        )


        return jsonify({

            'success': True,

            'resume_id': resume_id,

            'target_role': target_role,

            'analysis': result

        })


    except Exception as e:

        return jsonify({

            'success': False,

            'error': str(e)

        }), 500


# =========================================================
# JOB DESCRIPTION API
# =========================================================

@app.route('/api/analyze-job', methods=['POST'])
def api_analyze_job():

    try:

        data = request.get_json() or {}

        job_description = data.get(
            'job_description',
            ''
        ).strip()


        if not job_description:

            return jsonify({
                'success': False,
                'error': 'Job description is required'
            }), 400


        skills = parse_job_description_skills(
            job_description
        )


        return jsonify({

            'success': True,

            'skills': skills

        })


    except Exception as e:

        return jsonify({

            'success': False,

            'error': str(e)

        }), 500


# =========================================================
# AI RESUME DOCTOR
# =========================================================

@app.route('/api/resume-doctor', methods=['POST'])
def api_resume_doctor():

    try:

        data = request.get_json() or {}

        resume_id = data.get(
            'resume_id'
        )

        target_role = data.get(
            'target_role',
            'Frontend Developer'
        )

        job_description = data.get(
            'job_description',
            ''
        ).strip()


        if not resume_id:

            return jsonify({
                'success': False,
                'error': 'Missing resume_id'
            }), 400


        resume = get_resume(
            resume_id
        )


        if not resume:

            return jsonify({
                'success': False,
                'error': f'Resume {resume_id} not found'
            }), 404


        parsed_data = resume.get(
            'parsed_data'
        ) or {}


        result = generate_resume_doctor(
            parsed_data,
            target_role,
            job_description
        )


        if not result.get(
            'success',
            False
        ):

            return jsonify(result), 500


        return jsonify({

            'success': True,

            'resume_id': resume_id,

            'target_role': target_role,

            'analysis': result

        })


    except Exception as e:

        return jsonify({

            'success': False,

            'error': (
                f'Resume Doctor failed: {str(e)}'
            )

        }), 500


# =========================================================
# GENERATE RESUME
# =========================================================

@app.route('/api/generate-resume', methods=['POST'])
def api_generate_resume():

    try:

        data = request.get_json() or {}

        resume_id = data.get(
            'resume_id'
        )

        target_role = data.get(
            'target_role',
            'Frontend Developer'
        )


        if not resume_id:

            return jsonify({
                'success': False,
                'error': 'Missing resume_id'
            }), 400


        resume = get_resume(
            resume_id
        )


        if not resume:

            return jsonify({
                'success': False,
                'error': 'Resume not found'
            }), 404


        parsed_data = resume.get(
            'parsed_data'
        ) or {}


        generated = generate_role_tailored_resume(
            parsed_data,
            target_role
        )


        return jsonify({

            'success': True,

            'resume_id': resume_id,

            'target_role': target_role,

            'resume': generated

        })


    except Exception as e:

        return jsonify({

            'success': False,

            'error': str(e)

        }), 500


# =========================================================
# SAVE RESUME
# =========================================================

@app.route('/api/save-resume', methods=['POST'])
def api_save_resume():

    try:

        data = request.get_json() or {}

        resume_id = data.get(
            'resume_id'
        )

        resume_data = data.get(
            'resume_data'
        )


        if not resume_id:

            return jsonify({
                'success': False,
                'error': 'Missing resume_id'
            }), 400


        if not resume_data:

            return jsonify({
                'success': False,
                'error': 'Missing resume_data'
            }), 400


        update_resume_parsed_data(
            resume_id,
            resume_data
        )


        return jsonify({

            'success': True,

            'message': 'Resume saved successfully'

        })


    except Exception as e:

        return jsonify({

            'success': False,

            'error': str(e)

        }), 500


# =========================================================
# GET RESUME
# =========================================================

@app.route('/api/resume/<int:resume_id>')
def api_get_resume(resume_id):

    try:

        resume = get_resume(
            resume_id
        )


        if not resume:

            return jsonify({
                'success': False,
                'error': 'Resume not found'
            }), 404


        return jsonify({

            'success': True,

            'resume': resume

        })


    except Exception as e:

        return jsonify({

            'success': False,

            'error': str(e)

        }), 500


# =========================================================
# CREATE VERSION
# =========================================================

@app.route('/api/create-version', methods=['POST'])
def api_create_version():

    try:

        data = request.get_json() or {}

        resume_id = data.get(
            'resume_id'
        )

        version_name = data.get(
            'version_name',
            'Resume Version'
        )

        resume_data = data.get(
            'resume_data'
        )


        if not resume_id:

            return jsonify({
                'success': False,
                'error': 'Missing resume_id'
            }), 400


        version_id = save_resume_version(
            resume_id,
            version_name,
            resume_data
        )


        return jsonify({

            'success': True,

            'version_id': version_id

        })


    except Exception as e:

        return jsonify({

            'success': False,

            'error': str(e)

        }), 500


# =========================================================
# GET VERSIONS
# =========================================================

@app.route('/api/versions/<int:resume_id>')
def api_versions(resume_id):

    try:

        versions = get_resume_versions(
            resume_id
        )


        return jsonify({

            'success': True,

            'versions': versions

        })


    except Exception as e:

        return jsonify({

            'success': False,

            'error': str(e)

        }), 500


# =========================================================
# EXPORT PDF
# =========================================================

@app.route('/api/export/<int:resume_id>')
def api_export_resume(resume_id):

    try:

        resume = get_resume(
            resume_id
        )


        if not resume:

            return jsonify({
                'success': False,
                'error': 'Resume not found'
            }), 404


        parsed_data = resume.get(
            'parsed_data'
        ) or {}


        output_path = generate_pdf_resume(
            parsed_data
        )


        return send_file(
            output_path,
            as_attachment=True
        )


    except Exception as e:

        return jsonify({

            'success': False,

            'error': str(e)

        }), 500


# =========================================================
# LOAD SAMPLE
# =========================================================

@app.route('/api/load-sample')
def api_load_sample():

    try:

        sample_path = os.path.join(
            os.getcwd(),
            'sample_resume.pdf'
        )


        if not os.path.exists(
            sample_path
        ):

            return jsonify({
                'success': False,
                'error': 'Sample resume not found'
            }), 404


        parsed_data = parse_resume(
            sample_path
        )


        resume_id = insert_resume(
            'sample_resume.pdf',
            parsed_data
        )


        return jsonify({

            'success': True,

            'resume_id': resume_id,

            'parsed_data': parsed_data

        })


    except Exception as e:

        return jsonify({

            'success': False,

            'error': str(e)

        }), 500


# =========================================================
# SAMPLE DATA
# =========================================================

@app.route('/api/sample-data')
def api_sample_data():

    return jsonify({

        'success': True,

        'roles': ROLE_PROFILES

    })


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == '__main__':

    print()
    print('=======================================================')
    print(' AI Resume Analyzer & Skill-Based Resume Builder')
    print(' Running at: http://127.0.0.1:5000')
    print('=======================================================')
    print()

    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )