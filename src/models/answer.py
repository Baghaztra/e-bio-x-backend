from src.config.database import db

class Answer(db.Model):
    __tablename__ = 'answers'

    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey('submissions.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    option_id = db.Column(db.Integer, db.ForeignKey('options.id'), nullable=False)

    submission = db.relationship('Submission', backref=db.backref('answers', lazy=True, cascade="all, delete-orphan"))
    question = db.relationship('Question', backref=db.backref('answers', lazy=True, cascade="all, delete-orphan"))
    option = db.relationship('Option', backref=db.backref('answers', lazy=True, cascade="all, delete-orphan"))
    student = db.relationship('User', backref=db.backref('answers', lazy=True, cascade="all, delete-orphan"))

    def __repr__(self):
        return f'<Answer {self.id}>'
