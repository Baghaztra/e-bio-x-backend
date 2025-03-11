from flask_sqlalchemy import SQLAlchemy
from os import environ
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()

def init_db(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql://{environ.get('MYSQL_USER')}:{environ.get('MYSQL_PASSWORD')}@{environ.get('MYSQL_HOST')}/{environ.get('MYSQL_DATABASE')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = environ.get('SECRET_KEY')
    
    db.init_app(app) 