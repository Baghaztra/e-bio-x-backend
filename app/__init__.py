# This file makes the app directory a Python package 

from flask import Flask
from flask_migrate import Migrate
from app.config.database import init_db, db

def create_app():
    app = Flask(__name__)
    
    # Initialize database
    init_db(app)
    
    # Setup migrations
    migrate = Migrate(app, db)
    
    # Import routes
    from app.controllers.user_controller import get_all_users, create_user
    
    # Register routes
    app.add_url_rule('/api/users', view_func=get_all_users, methods=['GET'])
    app.add_url_rule('/api/users', view_func=create_user, methods=['POST'])
    
    return app

# Create the app instance
app = create_app() 