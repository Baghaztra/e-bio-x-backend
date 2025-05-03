from src.config.database import db
from datetime import datetime

class Submission(db.Model):
    __tablename__ = 'submissions'

    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    work_time = db.Column(db.Time, nullable=False)
    score = db.Column(db.Float, nullable=True)
    cluster = db.Column(db.Integer, nullable=True)
    submitted_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    quiz = db.relationship('Quiz', backref=db.backref('results', lazy=True, cascade="all, delete-orphan"))
    student = db.relationship('User', backref=db.backref('quiz_results', lazy=True, cascade="all, delete-orphan"))

    def __repr__(self):
        return f'<Submission {self.student_id} - {self.score}>'