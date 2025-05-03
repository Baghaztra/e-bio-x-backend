from flask import Flask, request
from flask_migrate import Migrate
from src.config.database import init_db, db
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from datetime import timedelta
import os

def create_app():
    app = Flask(__name__)

    # JWT
    app.config['JWT_SECRET_KEY'] = os.getenv("SECRET_KEY")
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=3)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=7)
    JWTManager(app)
    
    # Database & Migration
    init_db(app)
    Migrate(app, db)

    # CORS
    CORS(app, resources={r"/api/*": {"origins": os.getenv("FRONTEND_URL")}})
    
    # Import routes
    from src.controllers.user_controller import google_login, login, get_all_users, create_user, update_user, update_user_me, delete_user, protected
    from src.controllers.course_controller import create_course, get_courses, get_teacher_courses, get_student_courses, delete_course, enroll, out, get_course_by_id
    from src.controllers.material_controller import upload_material, get_material_by_id, get_material_by_course, delete_material
    from src.controllers.quiz_controller import create_quiz, get_quiz_by_id, delete_quiz, get_quizzes_by_course, submit_quiz, remove_sumbission, get_submission_by_quiz, toggle_open_quiz, edit_quiz_title, edit_question, edit_option
    from src.controllers.analysis_controller import analyze_quiz, get_analyze
    
    # Register routes
    app.add_url_rule('/api/google-login', view_func=google_login, methods=['POST'])
    app.add_url_rule('/api/login', view_func=login, methods=['POST'])
    
    app.add_url_rule('/api/users', view_func=get_all_users, methods=['GET'])
    app.add_url_rule('/api/users', view_func=create_user, methods=['POST'])
    app.add_url_rule('/api/users/<user_id>', view_func=update_user, methods=['PUT'])
    app.add_url_rule('/api/users/<user_id>', view_func=delete_user, methods=['DELETE'])
    app.add_url_rule('/api/user/me', view_func=update_user_me, methods=['PUT'])
    
    app.add_url_rule('/api/courses', view_func=create_course, methods=['POST'])
    app.add_url_rule('/api/courses', view_func=get_courses, methods=['GET'])
    app.add_url_rule('/api/courses/<course_id>', view_func=get_course_by_id, methods=['GET'])
    app.add_url_rule('/api/courses/<course_id>', view_func=delete_course, methods=['DELETE'])
    app.add_url_rule('/api/courses/teacher', view_func=get_teacher_courses, methods=['GET'])
    app.add_url_rule('/api/courses/student', view_func=get_student_courses, methods=['GET'])
    app.add_url_rule('/api/courses/enroll/<course_id>', view_func=enroll, methods=['GET'])
    app.add_url_rule('/api/courses/out/<course_id>', view_func=out, methods=['GET'])
    app.add_url_rule('/api/courses/materials/<course_id>', view_func=get_material_by_course, methods=['GET'])
    app.add_url_rule('/api/course/quiz/<course_id>', view_func=get_quizzes_by_course, methods=['GET'])
    
    app.add_url_rule('/api/materials', view_func=upload_material, methods=['POST'])
    app.add_url_rule('/api/materials/<material_id>', view_func=get_material_by_id, methods=['GET'])
    app.add_url_rule('/api/materials/<material_id>', view_func=delete_material, methods=['DELETE'])
    
    app.add_url_rule('/api/quiz', view_func=create_quiz, methods=['POST'])
    app.add_url_rule('/api/quiz/<quiz_id>', view_func=get_quiz_by_id, methods=['GET'])
    app.add_url_rule('/api/quiz/<quiz_id>', view_func=toggle_open_quiz, methods=['PUT'])
    app.add_url_rule('/api/quiz/<quiz_id>', view_func=delete_quiz, methods=['DELETE'])
    app.add_url_rule('/api/quiz/<quiz_id>/submit', view_func=submit_quiz, methods=['POST'])
    app.add_url_rule('/api/quiz/submission/<quiz_id>', view_func=get_submission_by_quiz, methods=['GET'])
    app.add_url_rule('/api/quiz/submission/<quiz_id>', view_func=remove_sumbission, methods=['DELETE'])
    
    app.add_url_rule('/api/quiz/<quiz_id>/edit_title', view_func=edit_quiz_title, methods=['PUT'])
    app.add_url_rule('/api/quiz/<question_id>/edit_question', view_func=edit_question, methods=['PUT'])
    app.add_url_rule('/api/quiz/<option_id>/edit_option', view_func=edit_option, methods=['PUT'])
    
    app.add_url_rule('/api/analysis/<quiz_id>', view_func=get_analyze, methods=['GET'])
    app.add_url_rule('/api/analysis/<quiz_id>', view_func=analyze_quiz, methods=['POST'])
    
    # Protected route
    app.add_url_rule('/api/protected', view_func=protected, methods=['GET'])

    
    return app

# Create the app instance
app = create_app() 