from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.quiz import Quiz
from src.models.question import Question
from src.models.option import Option
from src.config.database import db


# @jwt_required()
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


# @jwt_required()
def get_quizzes_by_course(course_id):
    quizzes = Quiz.query.filter_by(course_id=course_id).all()
    if not quizzes:
        return jsonify({"error": "No quizzes found for this course"}), 404

    return (
        jsonify(
            {
                "quizzes": [
                    {
                        "quiz_id": quiz.id,
                        "title": quiz.title,
                        "is_closed": quiz.is_closed,
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
