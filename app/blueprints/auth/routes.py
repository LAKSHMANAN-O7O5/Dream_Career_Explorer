import os
from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, request, session, current_app
from werkzeug.utils import secure_filename
from app import db
from app.models import User, Portfolio, Notification

auth_bp = Blueprint('auth', __name__)

# Security Helper: Allowed Extensions for Profile Pics
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

# Auth Middleware Decorators
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            flash('Access restricted to administrators.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function


# --- Routes ---

# 1. Register Route
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('student.dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        full_name = request.form.get('full_name', '').strip()
        role = request.form.get('role', 'student')
        
        # Validations
        if not username or not email or not password or not full_name:
            flash('All fields are required.', 'danger')
            return render_template('auth/register.html')
            
        if User.query.filter_by(username=username).first():
            flash('Username is already taken.', 'danger')
            return render_template('auth/register.html')
            
        if User.query.filter_by(email=email).first():
            flash('Email is already registered.', 'danger')
            return render_template('auth/register.html')

    # Check maximum number of admins
        if role == 'admin':
            admin_count = User.query.filter_by(role='admin').count()

            if admin_count >= 3:
                flash('Only 3 administrator accounts are allowed.', 'danger')
                return render_template('auth/register.html')
            
        # Create User
        new_user = User(
            username=username,
            email=email,
            full_name=full_name,
            role=role
        )
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()  # commit first to get user.id
        
        # Automatically generate default portfolio & welcome notification for students
        if role == 'student':
            new_portfolio = Portfolio(user_id=new_user.id, bio="")
            db.session.add(new_portfolio)
            
            welcome_notification = Notification(
                user_id=new_user.id,
                title="Welcome to Dream Career Explorer!",
                message="Your account has been created successfully. Get started by taking the Career Assessment Quiz to find your matched careers!"
            )
            db.session.add(welcome_notification)
            db.session.commit()
            
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/register.html')


# 2. Login Route
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('student.dashboard'))

    if request.method == 'POST':
        role = request.form.get('role')
        username_or_email = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        user = User.query.filter(
            (User.username == username_or_email) |
            (User.email == username_or_email)
        ).first()

        if user and user.check_password(password):

            # Role validation
            if role != user.role:
                flash(f"You selected '{role.title()}', but this account belongs to '{user.role.title()}'.", "danger")
                return render_template('auth/login.html')

            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role

            flash(f'Welcome back, {user.full_name}!', 'success')

            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)

            if user.role == 'admin':
                return redirect(url_for('admin.dashboard'))

            return redirect(url_for('student.dashboard'))

        flash('Invalid username/email or password.', 'danger')

    return render_template('auth/login.html')


# 3. Forgot Password Route
@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        new_password = request.form.get('password', '')
        
        user = User.query.filter_by(email=email).first()
        if user:
            user.set_password(new_password)
            db.session.commit()
            flash('Password reset successful! You can now log in.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('No user found with that email address.', 'danger')
            
    return render_template('auth/forgot_password.html')


# 4. Profile / Edit Profile Route
@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = db.session.get(User, session['user_id'])
    
    if request.method == 'POST':
        user.full_name = request.form.get('full_name', '').strip()
        user.department = request.form.get('department', '').strip()
        user.qualification = request.form.get('qualification', '').strip()
        
        # Handle file upload
        file = request.files.get('profile_pic')
        if file and file.filename != '':
            if allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Prefix user ID to avoid collision
                filename = f"user_{user.id}_{filename}"
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                user.profile_pic = filename
            else:
                flash('Invalid image format. Allowed formats: PNG, JPG, JPEG, GIF', 'danger')
                return render_template('auth/profile.html', user=user)
                
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('auth.profile'))
        
    return render_template('auth/profile.html', user=user)


# 5. Logout Route
@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('main.index'))
