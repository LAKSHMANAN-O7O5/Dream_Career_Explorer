import json
from app.models import Career, StudentSkill, Project, Certificate, Portfolio, QuizResult, Course

def calculate_job_readiness(user, career_id, db_session):
    """
    Calculates a student's job readiness score (0-100%) for a target career and
    provides suggestions for improvement.
    
    Weights:
    - Skills Profile: 30%
    - Projects: 20%
    - Quiz compatibility: 15%
    - Certifications: 15%
    - Resume & Portfolio Completion: 20%
    """
    career = db_session.get(Career, int(career_id))
    if not career:
        return 0, ["Target career not found"]
        
    suggestions = []
    
    # 1. Skills Profile (30%)
    skills_score = 0.0
    req_skills = career.skills_required
    student_skills = StudentSkill.query.filter_by(user_id=user.id).all()
    student_skills_dict = {s.skill_name.lower(): s for s in student_skills}
    
    if req_skills:
        matched_points = 0.0
        total_importance = 0.0
        missing_skills_list = []
        
        for req in req_skills:
            importance = req.importance or 3
            total_importance += importance * 100
            
            req_name = req.skill_name.lower()
            if req_name in student_skills_dict:
                skill_obj = student_skills_dict[req_name]
                proficiency = skill_obj.proficiency or 50
                # Give full weight if verified, else 80% weight
                verification_multiplier = 1.0 if skill_obj.verified else 0.8
                matched_points += (proficiency * importance) * verification_multiplier
                
                if proficiency < 70:
                    suggestions.append(f"Improve proficiency in required skill: **{req.skill_name}** (Current: {proficiency}%)")
            else:
                missing_skills_list.append(req.skill_name)
                
        if total_importance > 0:
            skills_score = (matched_points / total_importance) * 30.0
            
        if missing_skills_list:
            limit_display = missing_skills_list[:3]
            suffix = "..." if len(missing_skills_list) > 3 else ""
            suggestions.append(f"Acquire missing core skills: **{', '.join(limit_display)}{suffix}**")
    else:
        skills_score = 30.0  # baseline if career requires no skills
        
    # 2. Projects (20%)
    projects_score = 0.0
    user_projects = Project.query.filter_by(user_id=user.id).all()
    project_count = len(user_projects)
    
    # Award 5% per project up to 4 projects
    projects_score = min(20.0, project_count * 5.0)
    
    if project_count < 3:
        suggestions.append(f"Build more projects. You currently have {project_count} project(s), aim for at least 3 relevant portfolio projects.")
        
    # Check for links in projects
    linkless_projects = [p.title for p in user_projects if not p.github_link and not p.live_link]
    if linkless_projects:
        suggestions.append(f"Add GitHub or Live Deployment links to projects: **{', '.join(linkless_projects[:2])}** to boost technical score.")

    # 3. Quiz Score (15%)
    quiz_score = 0.0
    latest_quiz = QuizResult.query.filter_by(user_id=user.id).order_by(QuizResult.created_at.desc()).first()
    
    if latest_quiz:
        matches = latest_quiz.get_matches()
        match_pct = matches.get(str(career_id), 0)
        quiz_score = (match_pct / 100.0) * 15.0
        if match_pct < 60:
            suggestions.append(f"Your compatibility quiz score for this career is low ({match_pct}%). Review learning material to bridge core knowledge gaps.")
    else:
        suggestions.append("Complete the **Career Assessment Quiz** to verify compatibility with this role.")

    # 4. Certifications (15%)
    cert_score = 0.0
    completed_certs = Certificate.query.filter_by(user_id=user.id, status='completed').all()
    cert_count = len(completed_certs)
    
    # Award 5% per completed certificate up to 3 certificates
    cert_score = min(15.0, cert_count * 5.0)
    
    if cert_count < 2:
        suggestions.append("Obtain relevant certifications. Add completed certifications to demonstrate domain expertise.")
        
    unverified_certs = Certificate.query.filter_by(user_id=user.id, status='pending').all()
    if unverified_certs:
        suggestions.append(f"Upload verification files or credential links for pending certifications: **{unverified_certs[0].title}**.")

    # 5. Resume & Portfolio (20%)
    portfolio_score = 0.0
    portfolio = Portfolio.query.filter_by(user_id=user.id).first()
    
    portfolio_points = 0
    if portfolio:
        if portfolio.bio and len(portfolio.bio.strip()) > 15:
            portfolio_points += 2
        else:
            suggestions.append("Write a detailed professional summary/bio in your portfolio.")
            
        if portfolio.github_profile:
            portfolio_points += 2
        else:
            suggestions.append("Link your GitHub profile in the portfolio section.")
            
        if portfolio.linkedin_profile:
            portfolio_points += 2
        else:
            suggestions.append("Link your LinkedIn profile to expand professional networking.")
            
        if portfolio.website:
            portfolio_points += 2
        if portfolio.achievements and len(portfolio.achievements.strip()) > 10:
            portfolio_points += 2
    else:
        suggestions.append("Setup your professional Portfolio profile (Bio, external profile links, achievements).")
        
    # Resume completion check
    resume_points = 0
    if user.department and user.qualification:
        resume_points += 5
    else:
        suggestions.append("Update your Profile with your academic Department and Qualification.")
        
    if student_skills and user_projects:
        resume_points += 5
        
    portfolio_score = portfolio_points + resume_points  # total max is 10 + 10 = 20

    # Calculate overall readiness percentage
    total_score = skills_score + projects_score + quiz_score + cert_score + portfolio_score
    readiness_percentage = int(min(100.0, max(0.0, total_score)))
    
    # Default message if user is 100% ready
    if readiness_percentage >= 90:
        suggestions.insert(0, "You are Job Ready! Prepare for mock interviews and apply for jobs.")
    elif not suggestions:
        suggestions.append("Update details like project descriptions or complete recommended courses to boost your readiness score.")

    return readiness_percentage, suggestions
