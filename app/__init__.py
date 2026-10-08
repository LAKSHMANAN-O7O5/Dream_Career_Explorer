import os
from flask import Flask, session, g
from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')
    
    # Initialize DB with App
    db.init_app(app)
    
    # Ensure static upload directories exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Global context processor to make current user & notification count available in templates
    @app.context_processor
    def inject_global_data():
        from app.models import User, Notification
        user_id = session.get('user_id')
        current_user = None
        unread_notifications_count = 0
        
        if user_id:
            current_user = db.session.get(User, user_id)
            if current_user:
                unread_notifications_count = Notification.query.filter_by(user_id=user_id, is_read=False).count()
                
        return {
            'current_user': current_user,
            'unread_notifications_count': unread_notifications_count
        }
    
    # Register blueprints
    from app.blueprints.auth.routes import auth_bp
    from app.blueprints.student.routes import student_bp
    from app.blueprints.admin.routes import admin_bp
    from app.blueprints.main.routes import main_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(student_bp, url_prefix='/student')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    return app
