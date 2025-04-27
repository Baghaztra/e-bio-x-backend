from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
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
        quiz = Quiz(title=title, course_id=course_id)
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
def get_quiz_by_id(quiz_id):
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        return jsonify({"error": "Quiz not found"}), 404

    return (
        jsonify(
            {
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
                                # "is_correct": o.is_correct
                            }
                            for o in q.options
                        ],
                    }
                    for q in quiz.questions
                ],
            }
        ),
        200,
    )

@jwt_required()
def get_quizzes_by_course(course_id):
    quizzes = Quiz.query.filter_by(course_id=course_id).all()
    
    for quiz in quizzes:
        quiz.is_submited = False
        
        student_id = get_jwt_identity()
        if student_id:
            submission = Submission.query.filter_by(student_id=student_id, quiz_id=quiz.id).first()
            if submission:
                quiz.is_submited = True
                
    return (
        jsonify(
            {
                "quizzes": [
                    {
                        "quiz_id": quiz.id,
                        "title": quiz.title,
                        "is_closed": quiz.is_closed,
                        "is_submited": quiz.is_submited,
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
 