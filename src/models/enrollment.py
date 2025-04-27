from src.config.database import db
from datetime import datetime

class Enrollment(db.Model):
    __tablename__ = 'enrollments'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    enrolled_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    student = db.relationship('User', backref=db.backref('enrollments', lazy=True, cascade="all, delete-orphan"))
    course = db.relationship('Course', backref=db.backref('enrollments', lazy=True, cascade="all, delete-orphan"))

    def __repr__(self):
        return f'<Enrollment {self.id}>'
