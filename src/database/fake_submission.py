from faker import Faker
from src.models.enrollment import Enrollment
from src.models.quiz import Quiz
from src.models.submission import Submission
from src.models.question import Question
from src.models.option import Option
from src.models.answer import Answer
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
    questions = Question.query.filter_by(quiz_id=quiz_id).all()

    if not questions:
        print(f"Tidak ada soal di quiz {quiz_id}.")
        return

    for enrolment in student_enrolments:
        existing_submission = Submission.query.filter_by(student_id=enrolment.student_id, quiz_id=quiz_id).first()
        if existing_submission:
            print(f"Student {enrolment.student_id} is already submitted.")
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
        db.session.flush()  # supaya submission.id langsung bisa dipakai

        # Buat jawaban random untuk tiap soal
        for question in questions:
            options = Option.query.filter_by(question_id=question.id).all()
            if not options:
                continue

            selected_option = random.choice(options)
            answer = Answer(
                submission_id=submission.id,
                question_id=question.id,
                student_id=enrolment.student_id,
                option_id=selected_option.id
            )
            db.session.add(answer)

    db.session.commit()
    print(f"Submissions for quiz {quiz_id} created successfully.")

if __name__ == "__main__":
    with app.app_context():
        seed(8)
