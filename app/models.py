from datetime import datetime
import json
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

# 1. User Model
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.Enum('student', 'admin', name='user_roles'), default='student', nullable=False)
    profile_pic = db.Column(db.String(256), default='default.png')
    department = db.Column(db.String(100), nullable=True)
    qualification = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    portfolio = db.relationship('Portfolio', backref='user', uselist=False, cascade="all, delete-orphan")
    skills = db.relationship('StudentSkill', backref='user', cascade="all, delete-orphan")
    certificates = db.relationship('Certificate', backref='user', cascade="all, delete-orphan")
    projects = db.relationship('Project', backref='user', cascade="all, delete-orphan")
    quiz_results = db.relationship('QuizResult', backref='user', cascade="all, delete-orphan")
    progress = db.relationship('LearningProgress', backref='user', cascade="all, delete-orphan")
    notifications = db.relationship('Notification', backref='user', cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# 2. Career Model
class Career(db.Model):
    __tablename__ = 'careers'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=True, nullable=False)
    overview = db.Column(db.Text, nullable=False)
    responsibilities = db.Column(db.Text, nullable=False)
    average_salary_in = db.Column(db.String(50), nullable=False)  # e.g. "₹8,000,000"
    average_salary_intl = db.Column(db.String(50), nullable=False)  # e.g. "$110,000"
    future_scope = db.Column(db.Text, nullable=False)
    growth_rate = db.Column(db.String(20), nullable=False)  # e.g. "22%"
    top_companies = db.Column(db.Text, nullable=False)  # Comma-separated (Google, Microsoft)
    required_certifications = db.Column(db.Text, nullable=True)
    required_degrees = db.Column(db.Text, nullable=True)
    #department_focus = db.Column(db.String(255), nullable=True)
    portfolio_projects = db.Column(db.Text, nullable=True)  # JSON-string array of projects
    interview_tips = db.Column(db.Text, nullable=True)
    video_url = db.Column(db.String(256), nullable=True)
    success_story = db.Column(db.Text, nullable=True)
    

    # Relationships
    skills_required = db.relationship('CareerSkill', backref='career', cascade="all, delete-orphan")
    courses = db.relationship('Course', backref='career', cascade="all, delete-orphan")
    roadmap_stages = db.relationship('Roadmap', backref='career', cascade="all, delete-orphan")

    def get_portfolio_projects(self):
        try:
            return json.loads(self.portfolio_projects) if self.portfolio_projects else []
        except:
            return []


# 3. CareerSkill Model (Skills required for a career)
class CareerSkill(db.Model):
    __tablename__ = 'career_skills'
    id = db.Column(db.Integer, primary_key=True)
    career_id = db.Column(db.Integer, db.ForeignKey('careers.id'), nullable=False)
    skill_name = db.Column(db.String(100), nullable=False)
    skill_type = db.Column(db.Enum('technical', 'soft', name='skill_types'), default='technical')
    importance = db.Column(db.Integer, default=3)  # Scale 1-5


# 4. Course Model
class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    career_id = db.Column(db.Integer, db.ForeignKey('careers.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.Enum('free_course', 'paid_course', 'youtube_tutorial', 'documentation', 'practice_website', 'coding_platform', 'book', name='course_categories'), nullable=False)
    level = db.Column(db.Enum('beginner', 'intermediate', 'advanced', name='course_levels'), default='beginner')
    link = db.Column(db.String(500), nullable=False)
    platform_name = db.Column(db.String(100), nullable=False)  # Coursera, Udemy, YouTube, etc.


# 5. Roadmap Model
class Roadmap(db.Model):
    __tablename__ = 'roadmaps'
    id = db.Column(db.Integer, primary_key=True)
    career_id = db.Column(db.Integer, db.ForeignKey('careers.id'), nullable=False)
    stage_order = db.Column(db.Integer, nullable=False)  # 1 to 12
    stage_name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    recommended_resources = db.Column(db.Text, nullable=True)


# 6. QuizQuestion Model
class QuizQuestion(db.Model):
    __tablename__ = 'quiz_questions'
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.String(500), nullable=False)
    category = db.Column(db.Enum('personality', 'technical_interest', 'creativity', 'logical_thinking', 'communication', 'leadership', 'business', 'problem_solving', 'mathematics', 'analytical_skills', name='quiz_categories'), nullable=False)
    
    # Relationship
    options = db.relationship('QuizOption', backref='question', cascade="all, delete-orphan")


# 7. QuizOption Model
class QuizOption(db.Model):
    __tablename__ = 'quiz_options'
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('quiz_questions.id'), nullable=False)
    option_text = db.Column(db.String(300), nullable=False)
    score_value = db.Column(db.Text, nullable=False)  # JSON mapping of career titles to weights

    def get_weights(self):
        try:
            return json.loads(self.score_value) if self.score_value else {}
        except:
            return {}


# 8. QuizResult Model
class QuizResult(db.Model):
    __tablename__ = 'quiz_results'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    career_match_pct = db.Column(db.Text, nullable=False)  # JSON mapping, e.g. {"1": 95, "5": 78}
    interest_score = db.Column(db.Integer, default=0)
    personality_score = db.Column(db.Integer, default=0)
    technical_score = db.Column(db.Integer, default=0)
    communication_score = db.Column(db.Integer, default=0)
    logical_score = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_matches(self):
        try:
            return json.loads(self.career_match_pct) if self.career_match_pct else {}
        except:
            return {}


# 9. StudentSkill Model (Skills student possesses)
class StudentSkill(db.Model):
    __tablename__ = 'student_skills'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    skill_name = db.Column(db.String(100), nullable=False)
    proficiency = db.Column(db.Integer, default=50)  # Scale 1-100
    verified = db.Column(db.Boolean, default=False)


# 10. LearningProgress Model
class LearningProgress(db.Model):
    __tablename__ = 'learning_progress'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    career_id = db.Column(db.Integer, db.ForeignKey('careers.id'), nullable=False)
    stage_id = db.Column(db.Integer, db.ForeignKey('roadmaps.id'), nullable=False)
    status = db.Column(db.Enum('pending', 'in_progress', 'completed', name='progress_status'), default='pending', nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# 11. Project Model
class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    tools_used = db.Column(db.String(200), nullable=True)  # Comma-separated
    github_link = db.Column(db.String(256), nullable=True)
    live_link = db.Column(db.String(256), nullable=True)


# 12. Portfolio Model
class Portfolio(db.Model):
    __tablename__ = 'portfolios'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    bio = db.Column(db.Text, nullable=True)
    github_profile = db.Column(db.String(256), nullable=True)
    linkedin_profile = db.Column(db.String(256), nullable=True)
    website = db.Column(db.String(256), nullable=True)
    achievements = db.Column(db.Text, nullable=True)


# 13. Certificate Model
class Certificate(db.Model):
    __tablename__ = 'certificates'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    issuing_organization = db.Column(db.String(150), nullable=False)
    issue_date = db.Column(db.Date, nullable=False)
    credential_url = db.Column(db.String(500), nullable=True)
    status = db.Column(db.Enum('pending', 'completed', name='certificate_status'), default='pending', nullable=False)
    verification_file = db.Column(db.String(256), nullable=True)  # Name of uploaded certificate file


# 14. Notification Model
class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# 15. Blog Model
class Blog(db.Model):
    __tablename__ = 'blogs'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author_name = db.Column(db.String(100), default='Admin')
    tags = db.Column(db.String(150), nullable=True)  # Comma-separated tags
    read_time = db.Column(db.Integer, default=5)  # in minutes
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
