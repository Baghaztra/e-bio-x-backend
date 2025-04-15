from src.config.database import db
from datetime import datetime

class Answer(db.Model):
    __tablename__ = 'answers'

    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    answer = db.Column(db.String(1), nullable=False)
    submitted_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    question = db.relationship('Question', backref=db.backref('answers', lazy=True))
    student = db.relationship('User', backref=db.backref('answers', lazy=True))

    def __repr__(self):
        return f'<Answer {self.id}>'
