from flask import Blueprint, render_template, redirect, url_for, flash, request, session, current_app
from app import db
from app.models import User, Career, QuizQuestion, QuizOption, QuizResult, StudentSkill, Course, Roadmap, Blog
#from app.blueprints.auth.routes import admin_required
import json

admin_bp = Blueprint('admin', __name__)

from functools import wraps
from flask import session, flash, redirect, url_for

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            flash('Access restricted to administrators.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

# 1. Admin Dashboard with Analytics & Charts
@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    # 1. Basic Stats
    total_students = User.query.filter_by(role='student').count()
    total_careers = Career.query.count()
    total_quizzes = QuizResult.query.count()
    total_courses = Course.query.count()
    
    # Calculate average quiz score parameter (e.g. general compatibility)
    all_results = QuizResult.query.all()
    avg_score = 0
    if all_results:
        sum_scores = sum((r.technical_score + r.logical_score + r.communication_score) // 3 for r in all_results)
        avg_score = int(sum_scores / len(all_results))
        
    # 2. Career Distribution (Aggregation of top career matches)
    career_distribution = {}
    careers = Career.query.all()
    career_map = {str(c.id): c.title for c in careers}
    
    for result in all_results:
        matches = result.get_matches()
        if matches:
            top_career_id = list(matches.keys())[0]
            top_title = career_map.get(top_career_id, "Unknown")
            career_distribution[top_title] = career_distribution.get(top_title, 0) + 1
            
    # Format for Chart.js Pie Chart
    career_labels = list(career_distribution.keys())
    career_counts = list(career_distribution.values())
    
    # 3. Skill Statistics (Average proficiencies of top skills)
    skill_stats = {}
    all_student_skills = StudentSkill.query.all()
    skill_totals = {}
    skill_counts = {}
    for s in all_student_skills:
        name = s.skill_name.capitalize()
        skill_totals[name] = skill_totals.get(name, 0) + s.proficiency
        skill_counts[name] = skill_counts.get(name, 0) + 1
        
    for name in skill_totals:
        skill_stats[name] = int(skill_totals[name] / skill_counts[name])
        
    # Sort and take top 7 skills for Bar Chart
    sorted_skills = sorted(skill_stats.items(), key=lambda x: x[1], reverse=True)[:7]
    skill_labels = [s[0] for s in sorted_skills]
    skill_values = [s[1] for s in sorted_skills]
    
    # 4. Monthly Registrations (Line chart mock / actual timestamps)
    # Group users by month created
    monthly_data = {}
    users = User.query.filter_by(role='student').all()
    for u in users:
        month_name = u.created_at.strftime('%B')
        monthly_data[month_name] = monthly_data.get(month_name, 0) + 1
        
    # Ensure there are labels
    month_labels = list(monthly_data.keys()) if monthly_data else ["June", "July"]
    month_values = list(monthly_data.values()) if monthly_data else [0, len(users)]

    return render_template(
        'admin/dashboard.html',
        stats={
            'students': total_students,
            'careers': total_careers,
            'quizzes': total_quizzes,
            'courses': total_courses,
            'avg_score': avg_score
        },
        career_labels=json.dumps(career_labels),
        career_counts=json.dumps(career_counts),
        skill_labels=json.dumps(skill_labels),
        skill_values=json.dumps(skill_values),
        month_labels=json.dumps(month_labels),
        month_values=json.dumps(month_values)
    )


# 2. Manage Students
@admin_bp.route('/students')
@admin_required
def manage_users():
    students = User.query.filter_by(role='student').all()
    return render_template('admin/manage_users.html', students=students)


@admin_bp.route('/students/delete/<int:student_id>', methods=['POST'])
@admin_required
def delete_student(student_id):
    student = db.session.get(User, student_id)
    if student:
        db.session.delete(student)
        db.session.commit()
        flash('Student account deleted successfully.', 'success')
    return redirect(url_for('admin.manage_users'))


# 3. Manage Careers
@admin_bp.route('/careers', methods=['GET', 'POST'])
@admin_required
def manage_careers():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        overview = request.form.get('overview', '').strip()
        responsibilities = request.form.get('responsibilities', '').strip()
        salary_in = request.form.get('average_salary_in', '').strip()
        salary_intl = request.form.get('average_salary_intl', '').strip()
        growth = request.form.get('growth_rate', '').strip()
        future = request.form.get('future_scope', '').strip()
        companies = request.form.get('top_companies', '').strip()
        certs = request.form.get('required_certifications', '').strip()
        degrees = request.form.get('required_degrees', '').strip()
        
        # Validations
        if not title or not overview:
            flash("Title and Overview are required.", "danger")
            return redirect(url_for('admin.manage_careers'))
            
        new_career = Career(
            title=title,
            overview=overview,
            responsibilities=responsibilities,
            average_salary_in=salary_in or "₹6,000,000",
            average_salary_intl=salary_intl or "$90,000",
            growth_rate=growth or "10%",
            future_scope=future or "Steady Demand",
            top_companies=companies or "Google, Microsoft",
            required_certifications=certs,
            required_degrees=degrees,
            portfolio_projects=json.dumps([
                {"title": "Sample Project 1", "description": "Build a baseline implementation."},
                {"title": "Sample Project 2", "description": "Integrate advanced APIs."}
            ])
        )
        db.session.add(new_career)
        db.session.commit()
        
        flash(f"Career: '{title}' added successfully!", 'success')
        return redirect(url_for('admin.manage_careers'))
        
    careers = Career.query.all()
    return render_template('admin/manage_careers.html', careers=careers)


@admin_bp.route('/careers/delete/<int:career_id>', methods=['POST'])
@admin_required
def delete_career(career_id):
    career = db.session.get(Career, career_id)
    if career:
        db.session.delete(career)
        db.session.commit()
        flash('Career profile deleted.', 'success')
    return redirect(url_for('admin.manage_careers'))


# 4. Manage Quiz Questions
@admin_bp.route('/quiz', methods=['GET', 'POST'])
@admin_required
def manage_quiz():
    if request.method == 'POST':
        question_text = request.form.get('question_text', '').strip()
        category = request.form.get('category', 'personality')
        
        # Options & weights mapping input format (e.g. Option A | CareerName:Weight,CareerName:Weight)
        opt1_text = request.form.get('option1', '').strip()
        opt1_weights_str = request.form.get('option1_weights', '').strip()
        
        opt2_text = request.form.get('option2', '').strip()
        opt2_weights_str = request.form.get('option2_weights', '').strip()
        
        if not question_text or not opt1_text or not opt2_text:
            flash("Question and at least 2 options are required.", "danger")
            return redirect(url_for('admin.manage_quiz'))
            
        # Parse weights helper
        def parse_weights(w_str):
            res = {}
            if w_str:
                for pair in w_str.split(','):
                    if ':' in pair:
                        k, v = pair.split(':')
                        try:
                            res[k.strip()] = int(v.strip())
                        except:
                            res[k.strip()] = 2
            return res
            
        new_q = QuizQuestion(question_text=question_text, category=category)
        db.session.add(new_q)
        db.session.commit() # get question.id
        
        o1 = QuizOption(question_id=new_q.id, option_text=opt1_text, score_value=json.dumps(parse_weights(opt1_weights_str)))
        o2 = QuizOption(question_id=new_q.id, option_text=opt2_text, score_value=json.dumps(parse_weights(opt2_weights_str)))
        db.session.add(o1)
        db.session.add(o2)
        
        # Optional options 3 & 4
        opt3_text = request.form.get('option3', '').strip()
        if opt3_text:
            o3 = QuizOption(question_id=new_q.id, option_text=opt3_text, score_value=json.dumps(parse_weights(request.form.get('option3_weights', ''))))
            db.session.add(o3)
            
        opt4_text = request.form.get('option4', '').strip()
        if opt4_text:
            o4 = QuizOption(question_id=new_q.id, option_text=opt4_text, score_value=json.dumps(parse_weights(request.form.get('option4_weights', ''))))
            db.session.add(o4)
            
        db.session.commit()
        flash("Quiz question and options added successfully!", "success")
        return redirect(url_for('admin.manage_quiz'))
        
    questions = QuizQuestion.query.all()
    return render_template('admin/manage_quiz.html', questions=questions)


@admin_bp.route('/quiz/delete/<int:question_id>', methods=['POST'])
@admin_required
def delete_question(question_id):
    question = db.session.get(QuizQuestion, question_id)
    if question:
        db.session.delete(question)
        db.session.commit()
        flash('Quiz question deleted.', 'success')
    return redirect(url_for('admin.manage_quiz'))


# 5. Printable / Downloadable Analytical Reports Page
@admin_bp.route('/reports')
@admin_required
def reports():
    total_students = User.query.filter_by(role='student').count()
    total_careers = Career.query.count()
    total_quizzes = QuizResult.query.count()
    
    # Group results to see popularity
    all_results = QuizResult.query.all()
    career_distribution = {}
    careers = Career.query.all()
    career_map = {str(c.id): c.title for c in careers}
    
    for result in all_results:
        matches = result.get_matches()
        if matches:
            top_career_id = list(matches.keys())[0]
            top_title = career_map.get(top_career_id, "Unknown")
            career_distribution[top_title] = career_distribution.get(top_title, 0) + 1
            
    # Average compatibility stats
    skills = StudentSkill.query.all()
    avg_skills_per_student = len(skills) / max(total_students, 1)
    
    return render_template(
        'admin/reports.html',
        stats={
            'students': total_students,
            'careers': total_careers,
            'quizzes': total_quizzes,
            'avg_skills': round(avg_skills_per_student, 1)
        },
        distribution=career_distribution
    )
