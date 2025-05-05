from faker import Faker
from src.models.user import User
from src.models.course import Course
from src.models.enrollment import Enrollment
from src.config.database import db
from src import app

fake = Faker('id_ID')

def seed_users(num_users=30, teacher=None):
    print(f"Seeding {str(num_users)} users...")
    try:
        course_names = ['Biologi 1', 'Biologi 2']
        courses = []
        for name in course_names:
            course = Course(name=name, teacher_id=teacher.id)
            db.session.add(course)
            courses.append(course)

        db.session.commit()
        for _ in range(num_users):
            student = User(
                name=f"{fake.first_name()} {fake.last_name()}",
                email=fake.unique.email(),
                role='student'
            )
            student.set_password('123123123')
            db.session.add(student)
            db.session.flush() 

            import random
            enrolled_courses = random.sample(courses, k=random.randint(1, len(courses)))
            for course in enrolled_courses:
                enrollment = Enrollment(student_id=student.id, course_id=course.id)
                db.session.add(enrollment)

        db.session.commit()
        print(f"Done.")
    except Exception as e:
        print(f"Error seeding users: {str(e)}")
        db.session.rollback()

if __name__ == '__main__':
    with app.app_context():
        users = db.session.query(User).all()
        for user in users:
            db.session.delete(user)
        db.session.commit()
        
        # Create admin
        print(f"Create new admin...")
        try:
            admin = User(
                name='Admin',
                email='admin@ebiox.com',
                role='admin'
            )
            admin.set_password('123123123')
            db.session.add(admin)
            db.session.commit()
            print(f"Done.")
        except Exception as e:
            print(f"Error creating admin")
            db.session.rollback()
            
        # Create teacher
        print(f"Create new teacher...")
        try:
            teacher = User(
                name='Guru 1',
                email='guru@ebiox.com',
                role='teacher'
            )
            teacher.set_password('123123123')
            db.session.add(teacher)
            db.session.commit()
            print(f"Done.")
        except Exception as e:
            print(f"Error creating teacher")
            db.session.rollback()
            
        teacher = User.query.filter_by(name='Guru 1').first()
        
        seed_users(teacher=teacher, num_users=60)
