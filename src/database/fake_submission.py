from faker import Faker
from src.models.enrollment import Enrollment
from src.models.quiz import Quiz
from src.models.submission import Submission
from src.config.database import db
from src import app
from datetime import timedelta, datetime
import random

def random_work_time():
    seconds = random.randint(300, 1800)
    waktu = (datetime.min + timedelta(seconds=seconds)).time()
    return waktu

def seed(quiz_id):
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        print(f"Quiz with ID {quiz_id} not found.")
        return
    
    student_enrolments = Enrollment.query.filter_by(course_id=quiz.course_id).all()

    for enrolment in student_enrolments:
        exsisting_submission = Submission.query.filter_by(student_id=enrolment.student_id, quiz_id=quiz_id).first()
        if exsisting_submission:
            print(f"Student {enrolment.student_id} is already sumbited.")
            continue
        
        print(f"Creating submission for student {enrolment.student_id} ...")
        score = random.uniform(0, 100)
        work_time = random_work_time()
        
        submission = Submission(
            quiz_id=quiz_id, 
            student_id=enrolment.student_id,
            score=score,
            work_time=work_time,
        )
        db.session.add(submission)


    db.session.commit()
    print(f"Submissions for quiz {quiz_id} created successfully.")

if __name__ == "__main__":
    with app.app_context():
        seed(6)
