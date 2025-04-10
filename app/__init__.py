from flask import Flask
from flask_migrate import Migrate
from app.config.database import init_db, db
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import os

def create_app():
    app = Flask(__name__)
    init_db(app)
    migrate = Migrate(app, db)
    CORS(app, resources={r"/api/*": {"origins": os.getenv("FRONTEND_URL")}})
    jwt = JWTManager(app)
    
    # Import routes
    from app.controllers.user_controller import google_login, login, get_all_users, create_user, update_user, delete_user, protected
    from app.controllers.course_controller import create_course, get_courses, get_my_courses, enroll
    
    # Register routes
    app.add_url_rule('/api/google-login', view_func=google_login, methods=['POST'])
    app.add_url_rule('/api/login', view_func=login, methods=['POST'])
    
    app.add_url_rule('/api/users', view_func=get_all_users, methods=['GET'])
    app.add_url_rule('/api/users', view_func=create_user, methods=['POST'])
    app.add_url_rule('/api/users/<user_id>', view_func=update_user, methods=['PUT'])
    app.add_url_rule('/api/users/<user_id>', view_func=delete_user, methods=['DELETE'])
    
    app.add_url_rule('/api/courses', view_func=create_course, methods=['POST'])
    app.add_url_rule('/api/courses', view_func=get_courses, methods=['GET'])
    app.add_url_rule('/api/courses/teacher', view_func=get_my_courses, methods=['GET'])
    app.add_url_rule('/api/courses/enroll/<course_id>', view_func=enroll, methods=['GET'])
    
    # Protected route
    app.add_url_rule('/api/protected', view_func=protected, methods=['GET'])

    
    return app

# Create the app instance
app = create_app() 