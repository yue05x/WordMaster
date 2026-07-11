"""
WordCloud 字符云展示模块 - 数据库模型
复用 exam_record（考试记录表）和 answer_record（答题记录表）
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class ExamRecord(db.Model):
    """考试记录表"""
    __tablename__ = 'exam_record'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=False, index=True, comment='用户ID')
    score = db.Column(db.Float, nullable=False, default=0.0, comment='考试得分')
    total_questions = db.Column(db.Integer, nullable=False, default=0, comment='题目总数')
    correct_count = db.Column(db.Integer, nullable=False, default=0, comment='正确题数')
    wrong_count = db.Column(db.Integer, nullable=False, default=0, comment='错误题数')
    exam_date = db.Column(db.DateTime, nullable=False, default=datetime.now, comment='考试时间')
    duration = db.Column(db.Integer, nullable=True, default=0, comment='考试用时（秒）')

    answers = db.relationship('AnswerRecord', backref='exam', lazy='dynamic',
                              cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'score': self.score,
            'total_questions': self.total_questions,
            'correct_count': self.correct_count,
            'wrong_count': self.wrong_count,
            'exam_date': self.exam_date.strftime('%Y-%m-%d %H:%M:%S') if self.exam_date else None,
            'duration': self.duration,
            'accuracy': round(self.correct_count / self.total_questions * 100, 2) if self.total_questions > 0 else 0
        }


class AnswerRecord(db.Model):
    """答题记录表"""
    __tablename__ = 'answer_record'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    exam_id = db.Column(db.Integer, db.ForeignKey('exam_record.id', ondelete='CASCADE'),
                        nullable=False, index=True, comment='考试记录ID')
    word_id = db.Column(db.Integer, nullable=False, comment='单词ID')
    word_text = db.Column(db.String(255), nullable=False, comment='单词文本')
    correct_answer = db.Column(db.String(255), nullable=False, comment='正确答案')
    user_answer = db.Column(db.String(255), nullable=False, comment='用户答案')
    is_correct = db.Column(db.Boolean, nullable=False, default=False, comment='是否回答正确')

    def to_dict(self):
        return {
            'id': self.id,
            'exam_id': self.exam_id,
            'word_id': self.word_id,
            'word_text': self.word_text,
            'correct_answer': self.correct_answer,
            'user_answer': self.user_answer,
            'is_correct': self.is_correct
        }