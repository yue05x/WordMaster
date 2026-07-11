from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Word(db.Model):
    __tablename__ = 'word'
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(100), nullable=False, unique=True)
    definition = db.Column(db.String(255), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'word': self.word,
            'definition': self.definition
        }