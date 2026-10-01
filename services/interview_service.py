import os
import json
import re
from services.ai_service import get_gemini_client
from services.analyzer import ROLE_PROFILES

# Standard question templates for local fallback or starting points
CORE_INTERVIEW_QUESTIONS = [
    {
        "type": "intro",
        "question": "Welcome to our interview! To begin, could you please tell me about yourself, your educational background, and what inspired you to pursue a career as a {role}?"
    },
    {
        "type": "motivation",
        "question": "Why are you specifically interested in this {role} position, and what aspects of this engineering domain excite you the most?"
    },
    {
        "type": "project",
        "question": "Looking at your background, you mentioned working on {project}. Could you walk me through the architecture, the key technologies you used, and what specific problem you solved?"
    },
    {
        "type": "skills",
        "question": "You have listed {skill} in your technical toolkit. How have you applied this technology in your projects or coursework, and how comfortable do you feel using it in production?"
    },
    {
        "type": "challenge",
        "question": "Can you describe a difficult technical challenge or bug you faced while working on a project? What was your systematic approach to diagnosing and resolving it?"
    },
    {
        "type": "teamwork",
        "question": "Software development involves continuous collaboration. Tell me about a time you worked in a team or pair-programming setting. How did you communicate and manage differing viewpoints?"
    },
    {
        "type": "strength",
        "question": "What would you say is your strongest technical or problem-solving asset, and what is one area or emerging technology you are currently working to improve?"
    },
    {
        "type": "adaptability",
        "question": "In the technology industry, requirements and frameworks change rapidly. How do you approach learning a new programming language, library, or tool under tight deadlines?"
    },
    {
        "type": "future",
        "question": "Where do you envision yourself in the next 3 to 5 years in your software engineering journey?"
    },
    {
        "type": "closing",
        "question": "Why should our engineering team hire you for this {role} role, and what unique value or energy will you bring to the team?"
    }
]

def generate_first_question(resume_data, target_role="Software Developer", interview_type="HR Interview"):
    """
    Generate initial interview question tailored to candidate profile.
    """
    candidate_name = resume_data.get("name") if resume_data else None
    greeting = f"Welcome, {candidate_name}!" if candidate_name and candidate_name != "Student Candidate" else "Welcome!"

    if interview_type == "Fresher Interview":
        return f"{greeting} It is a pleasure to meet you. To kick off our fresher interview for the {target_role} position, could you please introduce yourself, highlighting your academic background and key technical interests?"
    elif interview_type == "Technical + HR":
        return f"{greeting} Thank you for joining us today. To start our conversation for the {target_role} role, could you give a brief introduction of yourself and summarize the technical stack you feel most proficient with?"
    elif interview_type == "Behavioral Interview":
        return f"{greeting} Welcome to your behavioral interview for the {target_role} role. To get started, please tell me about yourself and what key qualities make you a dependable team member."
    else:
        return f"{greeting} Welcome to our HR mock interview for the {target_role} position. Could you please tell me about yourself, your educational journey, and what motivated you to pursue this career path?"

def generate_next_question(resume_data, target_role, interview_type, history, question_index, total_questions):
    """
    Generate next question dynamically using Gemini AI or deterministic fallback.
    Avoids asking duplicate questions and incorporates candidate resume facts.
    """
    client = get_gemini_client()
    projects = resume_data.get("projects", []) if resume_data else []
    skills = [s["name"] if isinstance(s, dict) else s for s in (resume_data.get("skills", []) if resume_data else [])]
    
    # Extract existing questions asked so far to prevent repetitions
    asked_questions = [h.get("question_text", "") for h in history]

    if client:
        try:
            history_summary = ""
            for idx, item in enumerate(history[-3:]):
                history_summary += f"\nQ{idx+1}: {item.get('question_text')}\nA{idx+1}: {item.get('user_answer')[:150]}..."

            prompt = f"""
You are an expert, professional HR and Technical Interviewer conducting a mock interview for a student/fresher applying for the role: "{target_role}".
Interview Type: {interview_type}
Current Question Index: {question_index + 1} of {total_questions}.

CANDIDATE CONTEXT:
- Name: {resume_data.get('name', 'Candidate') if resume_data else 'Candidate'}
- Projects: {json.dumps([p.get('title') for p in projects[:3]])}
- Technical Skills: {', '.join(skills[:8])}
- Previous Conversation History:
{history_summary or "None yet."}

QUESTIONS ALREADY ASKED:
{json.dumps(asked_questions)}

CRITICAL INSTRUCTIONS:
1. Generate the NEXT single interview question appropriate for a {interview_type}.
2. DO NOT repeat any question that has already been asked.
3. Tailor the question to their target role ({target_role}), and where appropriate, reference their real projects ({', '.join([p.get('title') for p in projects[:2]])}) or skills ({', '.join(skills[:4])}).
4. Keep the question professional, encouraging, clear, and realistic for software/IT hiring.
5. Return ONLY the text of the question. Do not include quotes, prefixes like "Interviewer:", or commentary.
"""
            resp = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            q_text = resp.text.strip().replace('"', '').strip()
            if q_text and len(q_text) > 15:
                return q_text
        except Exception as e:
            print(f"Gemini next question error: {e}. Using deterministic fallback.")

    # Deterministic fallback question generation
    proj_title = projects[0].get("title", "your academic project") if projects else "a software project"
    top_skill = skills[0] if skills else "programming"
    
    template_idx = question_index % len(CORE_INTERVIEW_QUESTIONS)
    selected_template = CORE_INTERVIEW_QUESTIONS[template_idx]["question"]

    question = selected_template.format(
        role=target_role,
        project=proj_title,
        skill=top_skill
    )

    # If already asked, pick the next available template
    for t in CORE_INTERVIEW_QUESTIONS:
        cand_q = t["question"].format(role=target_role, project=proj_title, skill=top_skill)
        if cand_q not in asked_questions:
            return cand_q

    return question

def evaluate_answer(question_text, user_answer, target_role="Software Developer", interview_type="HR Interview"):
    """
    Evaluate user's interview answer on:
    - Relevance, Clarity, Confidence, Structure, Communication, Specificity, Professionalism
    - Strict rule: Never judge user's personality, intelligence, mental state, or personal worth.
    """
    user_answer = (user_answer or "").strip()
    
    if not user_answer or len(user_answer.split()) < 3:
        return {
            "score": 25,
            "category_scores": {
                "relevance": 20,
                "clarity": 30,
                "structure": 25,
                "communication": 30,
                "specificity": 20
            },
            "strengths": ["Attempted response"],
            "improvements_needed": [
                "Answer was too brief to evaluate thoroughly",
                "Elaborate with specific details and context"
            ],
            "improvement_tip": "Provide a complete answer with at least 2-3 sentences explaining your context, action, and outcome.",
            "verdict": "Needs Significant Elaboration"
        }

    client = get_gemini_client()
    if client:
        try:
            prompt = f"""
You are an expert HR Interview Coach evaluating a candidate's answer in a mock interview for the role: "{target_role}".
Interview Type: {interview_type}

INTERVIEW QUESTION:
"{question_text}"

CANDIDATE ANSWER:
"{user_answer}"

EVALUATION CRITERIA:
1. Relevance to the question asked
2. Clarity of thought and expression
3. Confidence indicators from wording (active voice, clear assertions)
4. Structure (e.g. context, actions taken, outcome or STAR method)
5. Communication effectiveness
6. Specificity (naming tools, methods, or scenarios rather than vague generalities)
7. Professional tone

STRICT ETHICAL GUIDELINE:
Do NOT judge the user's personality, intelligence, mental state, or personal worth. Evaluate strictly the communication, structure, technical specificity, and relevance of the answer.

Return ONLY a valid JSON object with EXACTLY this structure:
{{
  "score": 82,
  "category_scores": {{
    "relevance": 85,
    "clarity": 80,
    "structure": 78,
    "communication": 82,
    "specificity": 85
  }},
  "strengths": [
    "Relevant and direct response to the prompt",
    "Good practical project explanation"
  ],
  "improvements_needed": [
    "Could be more specific about the final outcome or impact",
    "Add measurable outcomes if applicable"
  ],
  "improvement_tip": "Try explaining what problem your project solved and what your specific contribution was.",
  "verdict": "Solid & Well-Articulated"
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
            return data
        except Exception as e:
            print(f"Gemini evaluation error: {e}. Using deterministic local evaluator.")

    # Local Deterministic Fallback Evaluator
    words = user_answer.split()
    word_count = len(words)
    answer_lower = user_answer.lower()

    # Heuristic scoring
    relevance_score = 75
    clarity_score = 70
    structure_score = 70
    comm_score = 75
    spec_score = 65

    strengths = []
    improvements_needed = []

    # Check length & depth
    if word_count >= 50:
        comm_score += 10
        structure_score += 10
        strengths.append("Comprehensive response with adequate detail")
    elif word_count >= 25:
        comm_score += 5
        strengths.append("Clear and concise communication")
    else:
        improvements_needed.append("Answer is fairly brief; consider expanding with more context")
        spec_score -= 15

    # Check for technical specifics or action verbs
    action_verbs = ["built", "developed", "engineered", "implemented", "solved", "designed", "created", "collaborated", "learned", "tested"]
    found_verbs = [v for v in action_verbs if v in answer_lower]
    if found_verbs:
        spec_score += 12
        clarity_score += 8
        strengths.append("Demonstrated active engagement using strong action verbs")
    else:
        improvements_needed.append("Use more active action verbs (e.g. 'architected', 'implemented', 'optimized')")

    # Check for outcome/result indicators
    outcome_words = ["result", "outcome", "improved", "learned", "delivered", "successfully", "impact", "user", "performance"]
    if any(ow in answer_lower for ow in outcome_words):
        structure_score += 10
        strengths.append("Mentioned outcomes or lessons learned")
    else:
        improvements_needed.append("Add the result or impact of your actions")

    # Relevance heuristic based on question keywords
    q_words = [w.lower() for w in re.findall(r'\b\w{4,}\b', question_text)]
    overlap = sum(1 for qw in q_words if qw in answer_lower)
    if overlap >= 2:
        relevance_score = min(95, relevance_score + 15)
        strengths.append("Directly addressed key aspects of the question")
    else:
        improvements_needed.append("Ensure your answer aligns closely with the core question prompt")

    # Bound category scores
    relevance_score = min(98, max(40, relevance_score))
    clarity_score = min(98, max(40, clarity_score))
    structure_score = min(98, max(40, structure_score))
    comm_score = min(98, max(40, comm_score))
    spec_score = min(98, max(35, spec_score))

    # Overall weighted score
    overall = int((relevance_score * 0.25) + (clarity_score * 0.20) + (structure_score * 0.20) + (comm_score * 0.20) + (spec_score * 0.15))

    if not strengths:
        strengths.append("Maintained a professional tone throughout")
    if not improvements_needed:
        improvements_needed.append("Continue practicing concise delivery under timed constraints")

    tip = "Try structuring your answer with the STAR framework: Situation, Task, Action, and Result."
    if "project" in question_text.lower():
        tip = "Explain the specific problem your project solved and clearly separate your personal contribution from group work."
    elif "weakness" in question_text.lower():
        tip = "Mention an authentic technical skill you found challenging, followed immediately by concrete steps you took to improve it."

    verdict = "Competent Response"
    if overall >= 85:
        verdict = "Excellent & Highly Articulate"
    elif overall >= 75:
        verdict = "Solid & Well-Structured"
    elif overall < 60:
        verdict = "Needs More Structure & Depth"

    return {
        "score": overall,
        "category_scores": {
            "relevance": relevance_score,
            "clarity": clarity_score,
            "structure": structure_score,
            "communication": comm_score,
            "specificity": spec_score
        },
        "strengths": strengths,
        "improvements_needed": improvements_needed,
        "improvement_tip": tip,
        "verdict": verdict
    }

def generate_final_interview_report(session, messages, target_role="Software Developer"):
    """
    Generate the overall final interview report with aggregated metrics,
    strengths, growth areas, and recommendations.
    """
    if not messages:
        return {
            "overall_score": 0,
            "category_averages": {"communication": 0, "relevance": 0, "clarity": 0, "structure": 0, "specificity": 0},
            "strengths": ["Completed interview session"],
            "growth_areas": ["Attempt all questions in future sessions"],
            "summary_statement": "Incomplete session."
        }

    scores = [m.get("score", 70) for m in messages if m.get("score") is not None]
    overall_score = int(sum(scores) / max(1, len(scores)))

    # Compute category averages
    cat_totals = {"communication": 0, "relevance": 0, "clarity": 0, "structure": 0, "specificity": 0}
    cat_counts = 0

    for m in messages:
        fb = m.get("feedback_data") or {}
        cat_scores = fb.get("category_scores", {})
        if cat_scores:
            cat_counts += 1
            for k in cat_totals:
                cat_totals[k] += cat_scores.get(k, 70)

    if cat_counts > 0:
        category_averages = {k: int(v / cat_counts) for k, v in cat_totals.items()}
    else:
        category_averages = {
            "communication": int(overall_score * 1.02),
            "relevance": int(overall_score * 1.05),
            "clarity": int(overall_score * 0.98),
            "structure": int(overall_score * 0.95),
            "specificity": int(overall_score * 0.92)
        }

    # Aggregate feedback strengths & improvements
    all_strengths = []
    all_improvements = []
    for m in messages:
        fb = m.get("feedback_data") or {}
        all_strengths.extend(fb.get("strengths", []))
        all_improvements.extend(fb.get("improvements_needed", []))

    # Deduplicate while preserving order
    top_strengths = list(dict.fromkeys(all_strengths))[:4]
    if not top_strengths:
        top_strengths = [
            f"Demonstrated solid foundational awareness for {target_role} roles",
            "Communicated with clarity and respectful professional tone",
            "Willingness to explain technical concepts and challenges"
        ]

    top_improvements = list(dict.fromkeys(all_improvements))[:4]
    if not top_improvements:
        top_improvements = [
            "Incorporate measurable impacts and performance metrics into answers",
            "Practice the STAR framework (Situation, Task, Action, Result) for behavioral questions"
        ]

    client = get_gemini_client()
    summary_statement = ""
    if client:
        try:
            prompt = f"""
Write a constructive, encouraging 3-sentence final HR interview debrief summary for a student/fresher who scored {overall_score}/100 in a mock interview for the role of "{target_role}".
Highlight their main strengths and suggest 1 key area for interview readiness.
Do not judge their personality, mental state, or worth. Keep it focused on interview communication.
"""
            resp = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            summary_statement = resp.text.strip().replace('"', '')
        except Exception:
            pass

    if not summary_statement:
        if overall_score >= 80:
            summary_statement = f"The candidate demonstrated strong conversational fluency, domain knowledge, and clear technical enthusiasm for the {target_role} role. Answers were well-structured and relevant to standard IT hiring benchmarks. For further distinction, focus on quantifying project outcomes and diving deeper into architectural tradeoffs."
        elif overall_score >= 65:
            summary_statement = f"The candidate showed competent communication and good foundational grasp of their projects and skills for {target_role} opportunities. Some responses could benefit from greater specificity regarding personal contributions and technical outcomes. Continued practice using the STAR methodology will enhance interview impact."
        else:
            summary_statement = f"The candidate engaged respectfully and attempted key questions for the {target_role} position. To improve callback rates, answers should be expanded with greater context, concrete examples from coursework or projects, and structured problem-solving narratives."

    return {
        "overall_score": overall_score,
        "category_averages": category_averages,
        "strengths": top_strengths,
        "growth_areas": top_improvements,
        "summary_statement": summary_statement,
        "total_questions_answered": len(messages),
        "target_role": target_role
    }
