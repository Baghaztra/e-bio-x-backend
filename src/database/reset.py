from src import app
from src.config.database import db
from flask_migrate import upgrade, downgrade

def reset_database():
    with app.app_context():
        db.drop_all()
        print("All tables dropped.")
        
        db.create_all()
        print("All tables created.")
        
        upgrade()
        print("Database migrated.")

if __name__ == '__main__':
    reset_database()