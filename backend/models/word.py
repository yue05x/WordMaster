from datetime import datetime

from . import db


class Word(db.Model):
    """单词表 — 由模块2维护，此处提供基础模型供考试模块使用。"""

    __tablename__ = "word"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    word = db.Column(db.String(100), nullable=False, unique=True)
    meaning = db.Column(db.String(500), nullable=False)
    phonetic = db.Column(db.String(100))
    level = db.Column(db.String(20))
    create_time = db.Column(db.DateTime, default=datetime.utcnow)

    def to_question_dict(self):
        return {
            "word_id": self.id,
            "word": self.word,
            "phonetic": self.phonetic,
            "level": self.level,
        }

    def to_dict(self):
        return {
            "id": self.id,
            "word": self.word,
            "meaning": self.meaning,
            "phonetic": self.phonetic,
            "level": self.level,
        }
