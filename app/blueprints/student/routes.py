import os
from werkzeug.utils import secure_filename
from flask import current_app
import json
from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify
from app import db
from app.models import User, Career, QuizQuestion, QuizOption, QuizResult, StudentSkill, LearningProgress, Project, Portfolio, Certificate, Notification, Roadmap
from app.blueprints.auth.routes import login_required
from app.services.recommender import calculate_career_compatibility
from app.services.readiness import calculate_job_readiness
from app.services.chatbot import generate_chatbot_response
from flask import render_template
from sqlalchemy import func

student_bp = Blueprint('student', __name__)

# 1. Student Dashboard
@student_bp.route('/dashboard')
@login_required
def dashboard():
    user = db.session.get(User, session['user_id'])
    
    # Fetch quiz results
    latest_result = QuizResult.query.filter_by(user_id=user.id).order_by(QuizResult.created_at.desc()).first()
    
    recommended_careers = []
    top_career = None
    top_match_pct = 0
    personality_type = "Not Analyzed"
    
    if latest_result:
        matches = latest_result.get_matches()
        # Fetch actual career objects and pair with their percentage match
        for career_id, pct in matches.items():
            career = db.session.get(Career, int(career_id))
            if career:
                recommended_careers.append({
                    'career': career,
                    'match_pct': pct
                })
        
        # Sort recommendations by match percentage
        recommended_careers = sorted(recommended_careers, key=lambda x: x['match_pct'], reverse=True)
        if recommended_careers:
            top_career = recommended_careers[0]['career']
            top_match_pct = recommended_careers[0]['match_pct']
            
        # Determine personality strengths
        strong_categories = []
        scores = {
            'Technical': latest_result.technical_score,
            'Logical': latest_result.logical_score,
            'Communication': latest_result.communication_score,
            'Interest': latest_result.interest_score,
            'Personality': latest_result.personality_score
        }
        for name, score in scores.items():
            if score >= 70:
                strong_categories.append(name)
        if strong_categories:
            personality_type = ", ".join(strong_categories) + " Oriented"
        else:
            # Fallback based on max score
            max_cat = max(scores, key=scores.get)
            personality_type = f"{max_cat} Driven"
            
    # Skill statistics
    skills = StudentSkill.query.filter_by(user_id=user.id).all()
    skills_count = len(skills)
    strength_count = sum(1 for s in skills if s.proficiency >= 70)
    
    # Progress trackers
    certificates_completed = Certificate.query.filter_by(user_id=user.id, status='completed').count()
    projects_count = Project.query.filter_by(user_id=user.id).count()
    
    # Roadmap overall progress (for their top matched career)
    completed_steps = 0
    total_steps = 0
    if top_career:
        total_steps = Roadmap.query.filter_by(career_id=top_career.id).count()
        completed_steps = LearningProgress.query.filter_by(
            user_id=user.id, 
            career_id=top_career.id, 
            status='completed'
        ).count()
        
    roadmap_pct = int((completed_steps / total_steps * 100)) if total_steps > 0 else 0

    return render_template(
        'student/dashboard.html',
        user=user,
        latest_result=latest_result,
        recommended_careers=recommended_careers[:6],  # limit to top 6
        top_career=top_career,
        top_match_pct=top_match_pct,
        personality_type=personality_type,
        skills_count=skills_count,
        strength_count=strength_count,
        certs_count=certificates_completed,
        projects_count=projects_count,
        roadmap_pct=roadmap_pct
    )


# 2. Career Assessment Quiz Wizard
@student_bp.route('/assessment', methods=['GET', 'POST'])
@login_required
def assessment():
    user = db.session.get(User, session['user_id'])
    
    if request.method == 'POST':
        # Retrieve form data
        answers = {}
        for key, value in request.form.items():
            if key.startswith('question_'):
                q_id = key.split('_')[1]
                answers[q_id] = value
                
        # Basic validation: ensure they answered questions
        if not answers:
            flash("Please complete the quiz to generate recommendations.", "danger")
            return redirect(url_for('student.assessment'))
            
        # Calculate compatibility
        matches, cat_scores = calculate_career_compatibility(user, answers, db.session)
        print("Matches =", matches)
        print("Category Scores =", cat_scores)
        
        # Save to database
        new_result = QuizResult(
            user_id=user.id,
            career_match_pct=json.dumps(matches),
            interest_score=cat_scores.get('technical_interest', 50),
            personality_score=cat_scores.get('personality', 50),
            technical_score=cat_scores.get('technical_interest', 50),
            communication_score=cat_scores.get('communication', 50),
            logical_score=cat_scores.get('logical_thinking', 50)
        )
        db.session.add(new_result)
        
        # Create user notification
        notif = Notification(
            user_id=user.id,
            title="Career Compatibility Scores Updated!",
            message="You have successfully completed the Career Assessment. Check your dashboard to view matches!"
        )
        db.session.add(notif)
        db.session.commit()
        
        flash("Career Assessment completed successfully! Your recommendations are ready.", "success")
        return redirect(url_for('student.dashboard'))
        
    # Get all questions
    questions = QuizQuestion.query.all()
    return render_template('student/assessment.html', questions=questions)


# 3. Learning Roadmap
@student_bp.route('/roadmap/<int:career_id>')
@login_required
def roadmap(career_id):
    user = db.session.get(User, session['user_id'])
    career = db.session.get(Career, career_id)
    if not career:
        flash("Career not found.", "warning")
        return redirect(url_for('student.dashboard'))
        
    stages = Roadmap.query.filter_by(career_id=career_id).order_by(Roadmap.stage_order).all()
    
    # Get student progress
    user_progress = LearningProgress.query.filter_by(user_id=user.id, career_id=career_id).all()
    progress_dict = {p.stage_id: p.status for p in user_progress}
    
    # In case there are missing entries, create pending progress for roadmap stages
    for stage in stages:
        if stage.id not in progress_dict:
            new_prog = LearningProgress(user_id=user.id, career_id=career_id, stage_id=stage.id, status='pending')
            db.session.add(new_prog)
            progress_dict[stage.id] = 'pending'
    db.session.commit()
    
    return render_template('student/roadmap.html', career=career, stages=stages, progress=progress_dict)


@student_bp.route('/roadmap/<int:career_id>/toggle/<int:stage_id>', methods=['POST'])
@login_required
def toggle_roadmap_stage(career_id, stage_id):
    user_id = session['user_id']
    prog = LearningProgress.query.filter_by(user_id=user_id, career_id=career_id, stage_id=stage_id).first()
    
    if prog:
        # Cycle status: pending -> in_progress -> completed -> pending
        if prog.status == 'pending':
            prog.status = 'in_progress'
        elif prog.status == 'in_progress':
            prog.status = 'completed'
        else:
            prog.status = 'pending'
            
        db.session.commit()
        return jsonify({'status': 'success', 'new_status': prog.status})
        
    return jsonify({'status': 'error', 'message': 'Stage progress not found'}), 404


# 4. Skill Gap Analysis
@student_bp.route('/skill_gap/<int:career_id>')
@login_required
def skill_gap(career_id):
    user = db.session.get(User, session['user_id'])
    career = db.session.get(Career, career_id)
    if not career:
        flash("Career profile not found.", "warning")
        return redirect(url_for('student.dashboard'))
        
    # Get required skills
    req_skills = career.skills_required
    
    # Get student skills
    student_skills = StudentSkill.query.filter_by(user_id=user.id).all()
    student_skills_dict = {s.skill_name.lower(): s for s in student_skills}
    
    strengths = []
    weak_areas = []
    missing_skills = []
    match_count = 0
    total_skills = len(req_skills)
    
    for req in req_skills:
        req_name = req.skill_name.lower()
        if req_name in student_skills_dict:
            skill = student_skills_dict[req_name]
            match_count += 1
            if skill.proficiency >= 70:
                strengths.append(skill)
            else:
                weak_areas.append(skill)
        else:
            missing_skills.append(req)
            
    match_percentage = int((match_count / total_skills) * 100) if total_skills > 0 else 100
    
    # Suggested Learning Order is determined by stages of the roadmap containing resources
    roadmap_stages = Roadmap.query.filter_by(career_id=career_id).order_by(Roadmap.stage_order).all()
    suggested_order = []
    for stage in roadmap_stages:
        # Check if this stage corresponds to any missing skill or weak skill
        for skill in missing_skills:
            if skill.skill_name.lower() in stage.description.lower() or skill.skill_name.lower() in (stage.recommended_resources or "").lower():
                suggested_order.append({
                    'skill': skill.skill_name,
                    'stage': stage.stage_name,
                    'resources': stage.recommended_resources
                })
                
    return render_template(
        'student/skill_gap.html',
        career=career,
        match_percentage=match_percentage,
        strengths=strengths,
        weak_areas=weak_areas,
        missing_skills=missing_skills,
        suggested_order=suggested_order
    )


# 5. Course Recommendations
@student_bp.route('/courses/<int:career_id>')
@login_required
def courses(career_id):
    career = db.session.get(Career, career_id)
    if not career:
        flash("Career not found.", "warning")
        return redirect(url_for('student.dashboard'))
        
    # Get courses recommended for this career grouped by category
    all_courses = career.courses
    
    grouped_courses = {
        'free_courses': [c for c in all_courses if c.category == 'free_course'],
        'paid_courses': [c for c in all_courses if c.category == 'paid_course'],
        'youtube_tutorials': [c for c in all_courses if c.category == 'youtube_tutorial'],
        'documentation': [c for c in all_courses if c.category == 'documentation'],
        'practice_websites': [c for c in all_courses if c.category == 'practice_website'],
        'coding_platforms': [c for c in all_courses if c.category == 'coding_platform'],
        'books': [c for c in all_courses if c.category == 'book']
    }
    
    return render_template('student/courses.html', career=career, grouped=grouped_courses)


# 6. Portfolio Builder
@student_bp.route('/portfolio', methods=['GET', 'POST'])
@login_required
def portfolio():
    user = db.session.get(User, session['user_id'])
    port = Portfolio.query.filter_by(user_id=user.id).first()
    
    if not port:
        port = Portfolio(user_id=user.id)
        db.session.add(port)
        db.session.commit()
        
    if request.method == 'POST':
        port.bio = request.form.get('bio', '').strip()
        port.github_profile = request.form.get('github_profile', '').strip()
        port.linkedin_profile = request.form.get('linkedin_profile', '').strip()
        port.website = request.form.get('website', '').strip()
        port.achievements = request.form.get('achievements', '').strip()
        
        # Also process skill edits (Add Skill)
        new_skill = request.form.get('new_skill', '').strip()
        new_proficiency = request.form.get('new_proficiency')
        
        if new_skill:
            try:
                prof = int(new_proficiency)
            except:
                prof = 50
            # Check if skill exists
            existing_skill = StudentSkill.query.filter_by(user_id=user.id, skill_name=new_skill).first()
            if not existing_skill:
                s = StudentSkill(user_id=user.id, skill_name=new_skill, proficiency=prof)
                db.session.add(s)
            else:
                existing_skill.proficiency = prof
                
        db.session.commit()
        flash('Portfolio and Skills profile updated successfully!', 'success')
        return redirect(url_for('student.portfolio'))
        
    user_projects = Project.query.filter_by(user_id=user.id).all()
    user_skills = StudentSkill.query.filter_by(user_id=user.id).all()
    
    return render_template('student/portfolio_builder.html', user=user, portfolio=port, projects=user_projects, skills=user_skills)


@student_bp.route('/portfolio/skill/delete/<int:skill_id>', methods=['POST'])
@login_required
def delete_skill(skill_id):
    user_id = session['user_id']
    skill = StudentSkill.query.filter_by(id=skill_id, user_id=user_id).first()
    if skill:
        db.session.delete(skill)
        db.session.commit()
        flash('Skill deleted from portfolio.', 'success')
    return redirect(url_for('student.portfolio'))


@student_bp.route('/portfolio/project/add', methods=['POST'])
@login_required
def add_project():
    user_id = session['user_id']
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    tools = request.form.get('tools_used', '').strip()
    github = request.form.get('github_link', '').strip()
    live = request.form.get('live_link', '').strip()
    
    if title and description:
        proj = Project(
            user_id=user_id,
            title=title,
            description=description,
            tools_used=tools,
            github_link=github,
            live_link=live
        )
        db.session.add(proj)
        db.session.commit()
        flash('Project added to portfolio!', 'success')
    else:
        flash('Project title and description are required.', 'danger')
        
    return redirect(url_for('student.portfolio'))


@student_bp.route('/portfolio/project/delete/<int:project_id>', methods=['POST'])
@login_required
def delete_project(project_id):
    user_id = session['user_id']
    proj = Project.query.filter_by(id=project_id, user_id=user_id).first()
    if proj:
        db.session.delete(proj)
        db.session.commit()
        flash('Project deleted from portfolio.', 'success')
    return redirect(url_for('student.portfolio'))


# 7. Resume Builder
@student_bp.route('/resume', methods=['GET', 'POST'])
@login_required
def resume():
    user = db.session.get(User, session['user_id'])
    portfolio = Portfolio.query.filter_by(user_id=user.id).first()
    
    # Store standard fields in session for simple CV generation config
    if request.method == 'POST':
        session['cv_education'] = request.form.get('education_history', '')
        session['cv_experience'] = request.form.get('experience_history', '')
        session['cv_summary'] = request.form.get('summary', '')
        
        flash("Resume parameters compiled! Click Preview to see your ATS Resume.", "success")
        return redirect(url_for('student.resume'))
        
    # Standard mocks if session is empty
    edu_mock = session.get('cv_education', f"B.Tech in Computer Science\nXYZ Institute of Technology, 2023 - 2027\nCGPA: 8.9/10")
    exp_mock = session.get('cv_experience', f"Software Developer Intern\nTech Solutions Inc., May 2025 - July 2025\n- Developed dashboard widgets using Bootstrap & Flask\n- Optimized database indexes improving query response by 25%")
    summary_mock = session.get('cv_summary', portfolio.bio if portfolio else "Motivated engineering student with skills in coding and web design.")
    
    user_skills = StudentSkill.query.filter_by(user_id=user.id).all()
    user_projects = Project.query.filter_by(user_id=user.id).all()
    
    return render_template(
        'student/resume_builder.html',
        user=user,
        skills=user_skills,
        projects=user_projects,
        education=edu_mock,
        experience=exp_mock,
        summary=summary_mock
    )


@student_bp.route('/resume/preview')
@login_required
def resume_preview():
    user = db.session.get(User, session['user_id'])
    portfolio = Portfolio.query.filter_by(user_id=user.id).first()
    
    edu = session.get('cv_education', "B.Tech in Computer Science")
    exp = session.get('cv_experience', "Developer Intern")
    summary = session.get('cv_summary', portfolio.bio if portfolio else "")
    
    skills = StudentSkill.query.filter_by(user_id=user.id).all()
    projects = Project.query.filter_by(user_id=user.id).all()
    
    return render_template(
        'student/resume_ats_preview.html',
        user=user,
        portfolio=portfolio,
        education=edu.split('\n'),
        experience=exp.split('\n'),
        summary=summary,
        skills=skills,
        projects=projects
    )


# 8. Certification Tracker
@student_bp.route('/certifications', methods=['GET', 'POST'])
@login_required
def certifications():
    user_id = session['user_id']
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        issuer = request.form.get('issuing_organization', '').strip()
        issue_date_str = request.form.get('issue_date', '').strip()
        cred_url = request.form.get('credential_url', '').strip()
        status = request.form.get('status', 'completed')
        
        # Validations
        if title and issuer and issue_date_str:
            from datetime import datetime
            try:
                issue_date = datetime.strptime(issue_date_str, '%Y-%m-%d').date()
            except:
                issue_date = datetime.utcnow().date()
                
            new_cert = Certificate(
                user_id=user_id,
                title=title,
                issuing_organization=issuer,
                issue_date=issue_date,
                credential_url=cred_url,
                status=status
            )
            
            # Simple mock verification upload
            file = request.files.get('verification_file')
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], f"cert_{user_id}_{filename}")
                file.save(file_path)
                new_cert.verification_file = f"cert_{user_id}_{filename}"
                new_cert.status = 'completed'  # auto-verified if file uploaded
                
            db.session.add(new_cert)
            db.session.commit()
            flash("Certification logged successfully!", "success")
        else:
            flash("Certification title, issuer, and date are required.", "danger")
            
        return redirect(url_for('student.certifications'))
        
    certs = Certificate.query.filter_by(user_id=user_id).all()
    
    # Extract recommendations based on the user's top matched career (if any)
    recommended_certs = []
    latest_result = QuizResult.query.filter_by(user_id=user_id).order_by(QuizResult.created_at.desc()).first()
    if latest_result:
        matches = latest_result.get_matches()
        if matches:
            top_career_id = int(list(matches.keys())[0])
            c_obj = db.session.get(Career, top_career_id)
            if c_obj and c_obj.required_certifications:
                recommended_certs = [cert.strip() for cert in c_obj.required_certifications.split(';') if cert.strip()]
                
    return render_template('student/certifications.html', certs=certs, recommendations=recommended_certs)


@student_bp.route('/certifications/delete/<int:cert_id>', methods=['POST'])
@login_required
def delete_certification(cert_id):
    user_id = session['user_id']
    cert = Certificate.query.filter_by(id=cert_id, user_id=user_id).first()
    if cert:
        db.session.delete(cert)
        db.session.commit()
        flash('Certification removed.', 'success')
    return redirect(url_for('student.certifications'))


# 9. Job Readiness Score Page
@student_bp.route("/job-readiness/<int:career_id>")
@login_required
def job_readiness(career_id):
    career = Career.query.get_or_404(career_id)

    readiness_score = 0
    score_breakdown = {
        "skills_score": 0,
        "projects_score": 0,
        "quiz_score": 0,
        "certs_score": 0,
        "portfolio_score": 0
    }

    advice = [
        {
            "title": "Complete your profile",
            "desc": "Add your basic information and target career.",
            "status": True
        },
        {
            "title": "Improve technical skills",
            "desc": "Work on the main skills needed for this role.",
            "status": False
        },
        {
            "title": "Add projects",
            "desc": "Upload at least one solid project to show proof of work.",
            "status": False
        },
        {
            "title": "Earn certifications",
            "desc": "Add relevant certifications to increase readiness.",
            "status": False
        },
        {
            "title": "Update resume",
            "desc": "Make sure your resume matches the target career.",
            "status": False
        }
    ]

    return render_template(
        "student/job_readiness.html",
        career=career,
        readiness_score=readiness_score,
        score_breakdown=score_breakdown,
        advice=advice
    )

# 10. AI Career Counselor Chatbot Routing
@student_bp.route('/chatbot')
@login_required
def chatbot_ui():
    return render_template('student/chatbot.html')


@student_bp.route('/chatbot/send', methods=['POST'])
@login_required
def chatbot_send():
    user = db.session.get(User, session['user_id'])
    data = request.get_json() or {}
    message = data.get('message', '').strip()
    
    if not message:
        return jsonify({'response': "I didn't receive any message. How can I help you?"})
        
    # Get user context for better personalized chat
    skills = StudentSkill.query.filter_by(user_id=user.id).all()
    skills_str = ", ".join([s.skill_name for s in skills]) if skills else "None added yet"
    
    user_context = {
        'name': user.full_name,
        'dept': user.department or 'N/A',
        'qual': user.qualification or 'N/A',
        'skills': skills_str
    }
    
    response_text = generate_chatbot_response(message, user_context)
    return jsonify({'response': response_text})


# --- Notifications System ---
@student_bp.route('/notifications')
@login_required
def notifications():
    user_id = session['user_id']

    user_notifications = Notification.query.filter_by(
        user_id=user_id
    ).order_by(Notification.created_at.desc()).all()

    unread_notifications_count = Notification.query.filter_by(
        user_id=user_id,
        is_read=False
    ).count()

    return render_template(
        'student/notifications.html',
        notifications=user_notifications,
        unread_notifications_count=unread_notifications_count
    )


@student_bp.route('/notifications/read/all', methods=['POST'])
@login_required
def mark_all_notifications_read():
    user_id = session['user_id']

    Notification.query.filter_by(
        user_id=user_id,
        is_read=False
    ).update(
        {Notification.is_read: True},
        synchronize_session=False
    )

    db.session.commit()

    flash("All notifications marked as read successfully.", "success")

    return redirect(url_for('student.notifications'))