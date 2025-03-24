from app.config.database import db
from datetime import datetime

class Course(db.Model): 
    __tablename__ = 'courses'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    teacher = db.relationship('User', backref=db.backref('courses', lazy=True))

    def __repr__(self):
        return f'<Course {self.name}>'
