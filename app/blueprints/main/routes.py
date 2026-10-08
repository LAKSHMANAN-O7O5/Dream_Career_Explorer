from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from app import db
from app.models import Career, Blog, User, QuizResult, Certificate

main_bp = Blueprint('main', __name__)

# 1. Landing Page
@main_bp.route('/')
def index():
    # Calculate statistics for the hero page
    total_students = User.query.filter_by(role='student').count()
    total_careers = Career.query.count()
    total_quizzes = QuizResult.query.count()
    total_certs = Certificate.query.filter_by(status='completed').count()
    
    # Pre-populate sample statistics if DB is empty
    stats = {
        'students': max(total_students, 2580),
        'careers': max(total_careers, 26),
        'quizzes': max(total_quizzes, 1420),
        'certs': max(total_certs, 890)
    }
    
    # Fetch 3 latest blogs to display
    recent_blogs = Blog.query.order_by(Blog.created_at.desc()).limit(3).all()
    
    return render_template('landing.html', stats=stats, blogs=recent_blogs)


# 2. Public Career Catalog
@main_bp.route('/careers')
def careers():
    search_query = request.args.get('search', '').strip()
    category_filter = request.args.get('category', '').strip()
    
    query = Career.query
    
    if search_query:
        query = query.filter(Career.title.like(f"%{search_query}%") | Career.overview.like(f"%{search_query}%"))
        
    all_careers = query.all()
    
    # Categorize careers locally based on keywords for filtering
    categorized_careers = []
    for c in all_careers:
        title_lower = c.title.lower()
        cat = 'Tech & Engineering'
        if any(w in title_lower for w in ['designer', 'ux', 'ui', 'graphic']):
            cat = 'Design & Creative'
        elif any(w in title_lower for w in ['manager', 'analyst', 'hr', 'marketing', 'financial', 'business']):
            cat = 'Business & Analytics'
        elif any(w in title_lower for w in ['teacher', 'professor']):
            cat = 'Education & Academics'
            
        if not category_filter or category_filter == cat:
            c.assigned_category = cat  # Dynamically add category to object
            categorized_careers.append(c)
            
    return render_template('careers.html', careers=categorized_careers, search=search_query, active_cat=category_filter)


# 3. Career Details Page
@main_bp.route('/careers/<int:career_id>')
def career_detail(career_id):
    career = db.session.get(Career, career_id)
    if not career:
        flash("Career profile not found.", "warning")
        return redirect(url_for('main.careers'))
        
    # Get other related careers to suggest
    related = Career.query.filter(Career.id != career_id).limit(3).all()
    
    # Convert comma-separated top companies to list
    companies_list = [comp.strip() for comp in career.top_companies.split(',') if comp.strip()]
    
    # Split certifications, degrees, and success stories by line or semi-colon
    certs_list = [cert.strip() for cert in (career.required_certifications or "").split(';') if cert.strip()]
    degrees_list = [deg.strip() for deg in (career.required_degrees or "").split(';') if deg.strip()]
    
    return render_template(
        'student/career_details.html',
        career=career,
        related=related,
        companies=companies_list,
        certifications=certs_list,
        degrees=degrees_list
    )


# 4. Career Comparison Widget
@main_bp.route('/comparison', methods=['GET', 'POST'])
def comparison():
    all_careers = Career.query.all()
    career1_id = request.args.get('c1') or request.form.get('career1')
    career2_id = request.args.get('c2') or request.form.get('career2')
    
    c1 = None
    c2 = None
    
    if career1_id:
        c1 = db.session.get(Career, int(career1_id))
    if career2_id:
        c2 = db.session.get(Career, int(career2_id))
        
    return render_template('student/comparison.html', careers=all_careers, c1=c1, c2=c2)


# 5. Career Trends
@main_bp.route('/trends')
def trends():
    # Gather trend reports
    careers_list = Career.query.all()
    
    # Sort highest salary
    def extract_sal(sal_str):
        # Extracts digits from salary e.g. "₹8,500,000" -> 8500000
        digits = ''.join(c for c in sal_str if c.isdigit())
        return int(digits) if digits else 0
        
    highest_paying = sorted(careers_list, key=lambda c: extract_sal(c.average_salary_in), reverse=True)[:5]
    
    # Sort fastest growing (growth rate string to int, e.g. "25%" -> 25)
    def extract_growth(growth_str):
        digits = ''.join(c for c in growth_str if c.isdigit())
        return int(digits) if digits else 0
        
    fastest_growing = sorted(careers_list, key=lambda c: extract_growth(c.growth_rate), reverse=True)[:5]
    
    # Mock some categorizations
    remote_friendly = [c for c in careers_list if any(x in c.title.lower() for x in ['developer', 'engineer', 'ui', 'ux', 'analyst', 'marketer'])][:6]
    gov_jobs = [c for c in careers_list if any(x in c.title.lower() for x in ['teacher', 'professor', 'civil', 'network', 'security'])][:6]
    
    return render_template(
        'student/trends.html',
        highest_paying=highest_paying,
        fastest_growing=fastest_growing,
        remote_friendly=remote_friendly,
        gov_jobs=gov_jobs
    )


# 6. Blog Listing
@main_bp.route('/blogs')
def blogs():
    all_blogs = Blog.query.order_by(Blog.created_at.desc()).all()
    return render_template('blogs.html', blogs=all_blogs)


# 7. Blog Detail Page
@main_bp.route('/blogs/<int:blog_id>')
def blog_detail(blog_id):
    blog = db.session.get(Blog, blog_id)
    if not blog:
        flash("Blog article not found.", "warning")
        return redirect(url_for('main.blogs'))
    return render_template('blog_detail.html', blog=blog)


# 8. Landing Page Contact Request Form (Mock Submission)
@main_bp.route('/contact', methods=['POST'])
def contact():
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')
    
    flash(f"Thank you, {name}! Your message has been received. Our team will contact you at {email} soon.", "success")
    return redirect(url_for('main.index'))
