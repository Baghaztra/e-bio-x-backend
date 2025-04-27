from src.config.database import db
from datetime import datetime

class Quiz(db.Model):
    __tablename__ = 'quizzes'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_closed = db.Column(db.Boolean, default=False)

    course = db.relationship('Course', backref=db.backref('quizzes', lazy=True, cascade="all, delete-orphan"))

    def __repr__(self):
        return f'<Quiz {self.title}>'
