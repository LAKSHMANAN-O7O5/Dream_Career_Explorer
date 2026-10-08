import os
from dotenv import load_dotenv
load_dotenv()
class Config:
    # Flask Security settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dream_career_explorer_super_secret_key_129847')
    
    # DB configuration: SQLITE fallback, MySQL default if environment variables are set
    DB_USER = os.environ.get('DB_USER')
    DB_PASSWORD = os.environ.get('DB_PASSWORD')
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = os.environ.get('DB_PORT', '3306')
    DB_NAME = os.environ.get('DB_NAME')

    if DB_USER and DB_PASSWORD and DB_NAME:
        SQLALCHEMY_DATABASE_URI = (
            f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}"
            f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        )

        SQLALCHEMY_ENGINE_OPTIONS = {
            "connect_args": {
                "ssl": {
                    "ca": os.path.join(
                        os.path.dirname(os.path.abspath(__file__)),
                        "..",
                        "ca.pem"
                    )
                }
            }
        }
    else:
        SQLALCHEMY_DATABASE_URI = "sqlite:///dream_career.db"
        
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # File upload configurations
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static/uploads')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB Max upload limit
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    # Optional Gemini AI API Key
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
