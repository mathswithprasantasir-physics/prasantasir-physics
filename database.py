from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(100), nullable=False)
    subtopic = db.Column(db.String(100))
    year = db.Column(db.String(10), default='2026')
    question_text = db.Column(db.Text, nullable=False)
    question_image = db.Column(db.String(500))
    option_a = db.Column(db.String(500))
    option_b = db.Column(db.String(500))
    option_c = db.Column(db.String(500))
    option_d = db.Column(db.String(500))
    option_a_image = db.Column(db.String(500))
    option_b_image = db.Column(db.String(500))
    option_c_image = db.Column(db.String(500))
    option_d_image = db.Column(db.String(500))
    correct_answer = db.Column(db.String(10))
    solution = db.Column(db.Text)
    solution_image = db.Column(db.String(500))
    explanation = db.Column(db.Text)
    marks = db.Column(db.Integer, default=4)
    negative_marks = db.Column(db.Integer, default=1)
    exam_type = db.Column(db.String(50), default='NEET')
    difficulty = db.Column(db.String(20), default='Medium')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Question {self.id}: {self.question_text[:50]}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'topic': self.topic,
            'subtopic': self.subtopic,
            'year': self.year,
            'question_text': self.question_text,
            'question_image': self.question_image,
            'option_a': self.option_a,
            'option_b': self.option_b,
            'option_c': self.option_c,
            'option_d': self.option_d,
            'option_a_image': self.option_a_image,
            'option_b_image': self.option_b_image,
            'option_c_image': self.option_c_image,
            'option_d_image': self.option_d_image,
            'correct_answer': self.correct_answer,
            'solution': self.solution,
            'solution_image': self.solution_image,
            'explanation': self.explanation,
            'marks': self.marks,
            'negative_marks': self.negative_marks,
            'exam_type': self.exam_type,
            'difficulty': self.difficulty,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else None
        }
