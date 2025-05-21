from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import User
from src.models.quiz import Quiz
from src.models.question import Question
from src.models.option import Option
from src.models.submission import Submission
from src.models.answer import Answer
from src.config.database import db

@jwt_required()
def create_quiz():
    data = request.get_json()
    course_id = data.get('course_id')
    title = data.get('title')
    
    if not course_id or not title:
        return jsonify({"error": "Course ID and title are required"}), 400

    if Quiz.query.filter_by(title=title, course_id=course_id).first():
        return jsonify({"error": "Quiz with this title already exists"}), 400

    try:
        quiz = Quiz(title=title, course_id=course_id, is_closed=True)
        db.session.add(quiz)

        questions = data.get('questions', [])
        for q in questions:
            question_text = q.get('question_text')
            new_question = Question(quiz=quiz, text=question_text)
            db.session.add(new_question)

            options = q.get('options', [])
            for o in options:
                option_text = o.get('option_text')
                is_correct = o.get('is_correct', False)
                new_option = Option(
                    question=new_question,
                    option_text=option_text,
                    is_correct=is_correct
                )
                db.session.add(new_option)

        db.session.commit()

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error creating quiz: {str(e)}"}), 500

    return jsonify({"message": "Quiz created successfully", "quiz_id": quiz.id}), 201

@jwt_required()
def toggle_open_quiz(quiz_id):
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        return jsonify({"error": "Quiz not found"}), 404
    
    try:
        quiz.is_closed = not quiz.is_closed
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error toggling quiz: {str(e)}"}), 500

    status = 'closed' if quiz.is_closed else 'opened'
    return jsonify({"message": f"Quiz {status} successfully"}), 200

@jwt_required()
def edit_quiz_title(quiz_id):
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        return jsonify({"error": "Quiz not found"}), 404
    
    try:
        title = request.get_json().get('title')
        if not title:
            return jsonify({"error": "Title is required"}), 400
        quiz.title = title
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error editing quiz: {str(e)}"}), 500
    
    return jsonify({"message": "Quiz edited successfully"}), 200

@jwt_required()
def edit_question(question_id):
    question = Question.query.get(question_id)
    if not question:
        return jsonify({"error": "Question not found"}), 404
    
    try:
        question_text = request.get_json().get('question_text')
        if not question_text:
            return jsonify({"error": "Question text is required"}), 400
        question.text = question_text
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error editing quiz: {str(e)}"}), 500
    
    return jsonify({"message": "Question edited successfully"}), 200

@jwt_required()
def edit_option(option_id):
    option = Option.query.get(option_id)
    if not option:
        return jsonify({"error": "Option not found"}), 404
    
    try:
        data = request.get_json()
        option_text = data.get('option_text')
        is_correct = data.get('is_correct')

        if option_text:
            option.text = option_text

        if is_correct is not None:
            question = Question.query.get(option.question_id)
            other_options = Option.query.filter_by(question_id=question.id).all()

            if is_correct is True:
                for o in other_options:
                    o.is_correct = (o.id == option.id)
            else:
                option.is_correct = False

        db.session.commit()

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error editing quiz: {str(e)}"}), 500
    
    return jsonify({"message": "Option edited successfully"}), 200

@jwt_required()
def get_quiz_by_id(quiz_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        return jsonify({"error": "Quiz not found"}), 404

    access = user.role == 'teacher' or user.role == 'admin'

    return jsonify({
        "quiz_id": quiz.id,
        "course_id": quiz.course_id,
        "title": quiz.title,
        "is_closed": quiz.is_closed,
        "created_at": quiz.created_at,
        "questions": [
            {
                "question_id": q.id,
                "question_text": q.text,
                "options": [
                    {
                        "option_id": o.id,
                        "option_text": o.option_text,
                        "is_correct": o.is_correct if access else 'hidden'
                    }
                    for o in q.options
                ],
            }
            for q in quiz.questions
        ],
    }), 200

@jwt_required()
def get_quizzes_by_course(course_id):
    quizzes = Quiz.query.filter_by(course_id=course_id).all()
    
    for quiz in quizzes:
        quiz.is_submited = False
        quiz.score = 0
        quiz.work_time = None
        
        student_id = get_jwt_identity()
        if student_id:
            submission = Submission.query.filter_by(student_id=student_id, quiz_id=quiz.id).first()
            if submission:
                quiz.is_submited = True
                quiz.score = submission.score
                quiz.work_time = submission.work_time.strftime('%H:%M:%S')
                
    return (
        jsonify(
            {
                "quizzes": [
                    {
                        "quiz_id": quiz.id,
                        "title": quiz.title,
                        "is_closed": quiz.is_closed,
                        "is_submited": quiz.is_submited,
                        "score": quiz.score,
                        "work_time": quiz.work_time,
                        "questions": len(quiz.questions),
                        "created_at": quiz.created_at,
                    }
                    for quiz in quizzes
                ]
            }
        ),
        200,
    )

@jwt_required()
def delete_quiz(quiz_id):
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        return jsonify({"error": "Quiz not found"}), 404

    try:
        db.session.delete(quiz)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error deleting quiz: {str(e)}"}), 500

    return jsonify({"message": "Quiz deleted successfully"}), 200

@jwt_required()
def submit_quiz(quiz_id):
    student_id = get_jwt_identity()
    if not student_id:
        return jsonify({"error": "Student not authenticated"}), 401
    
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        return jsonify({"error": "Quiz not found"}), 404
    
    submission = Submission.query.filter_by(student_id=student_id, quiz_id=quiz_id).first()
    if submission:
        return jsonify({"error": "You have already submitted this quiz"}), 400
    
    data = request.get_json()
    submited_answers = data.get('answers')
    
    if not submited_answers:
        return jsonify({"error": "Answers required"}), 400
    
    try:
        new_submission = Submission(
            student_id=student_id,
            quiz_id=quiz_id,
            work_time=data.get("work_time")
        )

        db.session.add(new_submission)
        db.session.flush()

        correct_answers = 0
        for ans in submited_answers:
            option = Option.query.get(ans['option_id'])
            if option and option.is_correct:
                correct_answers += 1
            
            answer = Answer(
                submission_id=new_submission.id,
                question_id=ans['question_id'],
                student_id=student_id,
                option_id=ans['option_id']
            )
            db.session.add(answer)
            
        total_questions = len(Quiz.query.get(quiz_id).questions)
        
        if total_questions == 0:
            score = 0
        else:
            score = (correct_answers / total_questions) * 100

        new_submission.score = score
        
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error submitting quiz: {str(e)}"}), 500

    return jsonify({
        "message": "Quiz submitted successfully",
        "data": {
            "student": new_submission.student.name,
            "work_time": new_submission.work_time.strftime('%H:%M:%S'),
            "score": new_submission.score
        }
    }), 201

@jwt_required()
def remove_sumbission(quiz_id):
    student_id = get_jwt_identity()
    if not student_id:
        return jsonify({"error": "Student not authenticated"}), 401
    
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        return jsonify({"error": "Quiz not found"}), 404
    
    submission = Submission.query.filter_by(student_id=student_id, quiz_id=quiz_id).first()
    if not submission:
        return jsonify({"error": "Submission not found"}), 404
    
    try:
        db.session.delete(submission)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error deleting submission: {str(e)}"}), 500
    
    return jsonify({"message": "Submission deleted successfully"}), 200
 
def get_submission_by_quiz(quiz_id):
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        return jsonify({"error": "Quiz not found"}), 404
    
    submissions = Submission.query.filter_by(quiz_id=quiz_id).all()
    if not submissions:
        return jsonify({"error": "Not submissions found"}), 404
    
    return (
        jsonify(
            {
                "quiz_id": quiz.id,
                "quiz_title": quiz.title,
                "submissions": [
                    {
                        "student": submission.student.name,
                        "student_id": submission.student.id,
                        "work_time": submission.work_time.strftime('%H:%M:%S'),
                        "score": submission.score,
                    } for submission in submissions
                ]
            }
        ),
        200,
    )

def get_my_submission_by_id(quiz_id):
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        return jsonify({"error": "Quiz not found"}), 404
    
    submission = Submission.query.filter_by(quiz_id=quiz_id).first()
    if not submission:
        return jsonify({"error": "Submission not found"}), 404
    
    answers = Answer.query.filter_by(submission_id=submission.id).all()
    
    return (
        jsonify(
            {
                "quiz_title": quiz.title,
                "submission": {
                    "student": submission.student.name,
                    "work_time": submission.work_time.strftime('%H:%M:%S'),
                    "score": submission.score,
                    "answers": [
                        {
                            "question_id": ans.question.id,
                            "option_id": ans.option.id,
                            "option_text": ans.option.option_text,
                            "is_correct": ans.option.is_correct
                        }
                        for ans in answers
                    ]
                }
            }
        ),
        200,
    )