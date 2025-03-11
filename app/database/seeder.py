from faker import Faker
from app.models.user import User
from app.config.database import db
from app import app

fake = Faker('id_ID')  # Menggunakan locale Indonesia

def seed_users(num_users=10):
    """Seed users table with dummy data"""
    try:
        with app.app_context():
            for _ in range(num_users):
                user = User(
                    username=fake.user_name(),
                    email=fake.email()
                )
                db.session.add(user)
            
            db.session.commit()
            print(f"{num_users} users berhasil ditambahkan!")
    except Exception as e:
        print(f"Error saat seeding users: {str(e)}")
        db.session.rollback()

if __name__ == '__main__':
    seed_users() 