import os
from app import create_app, db

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        # Create database tables if they do not exist
        db.create_all()
        
        # Seed initial data (careers, quiz, courses) if database is empty
        try:
            from seed_data import seed_database
            seed_database()
        except Exception as e:
            app.logger.error(f"Error seeding database: {e}")
            
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
