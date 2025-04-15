from src.config.database import db

class Option(db.Model):
    __tablename__ = 'options'

    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    answer = db.Column(db.String(1), nullable=False)
    answer_text = db.Column(db.String(70), nullable=False)
    check = db.Column(db.Boolean, nullable=False, default=False)

    question = db.relationship('Question', backref=db.backref('option', lazy=True))

    def __repr__(self):
        return f'<Option {self.id}>'
