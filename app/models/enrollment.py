import random
from app.config.database import db
from datetime import datetime

def generate_enrollment_id():
    return str(random.randint(1000, 9999))

class Enrollment(db.Model):
    __tablename__ = 'enrollments'
    
    id = db.Column(db.String(4), primary_key=True, default=generate_enrollment_id)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    enrolled_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    student = db.relationship('User', backref=db.backref('enrollments', lazy=True))
    course = db.relationship('Course', backref=db.backref('enrollments', lazy=True))

    def __repr__(self):
        return f'<Enrollment {self.id}>'
