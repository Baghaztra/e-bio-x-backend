from src.config.database import db
from datetime import datetime

class Submission(db.Model):
    __tablename__ = 'submissions'

    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    score = db.Column(db.Float, nullable=False)
    analyzed_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    quiz = db.relationship('Quiz', backref=db.backref('results', lazy=True))
    student = db.relationship('User', backref=db.backref('quiz_results', lazy=True))

    def __repr__(self):
        return f'<Submission {self.student_id} - {self.score}>'