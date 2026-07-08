from . import db
from services.question_types import EN_TO_CN_TYPES, QUESTION_TYPES


class AnswerRecord(db.Model):
    __tablename__ = "answer_record"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    exam_id = db.Column(db.Integer, db.ForeignKey("exam_record.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    word_id = db.Column(db.Integer, db.ForeignKey("word.id"), nullable=False)
    user_answer = db.Column(db.String(500))
    question_type = db.Column(db.String(30), default="en_to_cn")
    is_correct = db.Column(db.SmallInteger, default=0)
    question_order = db.Column(db.Integer)

    exam = db.relationship("ExamRecord", back_populates="answers")
    word = db.relationship("Word")

    def to_dict(self):
        question_type = self.question_type or "en_to_cn"
        word = self.word
        prompt = None
        correct_answer = None
        if word:
            if question_type in EN_TO_CN_TYPES:
                prompt = word.word
                correct_answer = word.meaning
            else:
                prompt = word.meaning
                correct_answer = word.word

        return {
            "id": self.id,
            "word_id": self.word_id,
            "word": word.word if word else None,
            "correct_meaning": word.meaning if word else None,
            "question_type": question_type,
            "question_type_label": QUESTION_TYPES.get(question_type, question_type),
            "prompt": prompt,
            "correct_answer": correct_answer,
            "user_answer": self.user_answer,
            "is_correct": bool(self.is_correct),
            "question_order": self.question_order,
        }
