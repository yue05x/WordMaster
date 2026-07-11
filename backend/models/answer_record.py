from . import db


class AnswerRecord(db.Model):
    __tablename__ = "answer_record"

    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey("exam_record.id"), nullable=False, index=True)
    exam_question_id = db.Column(db.Integer, db.ForeignKey("exam_question.id"), nullable=False)
    word_id = db.Column(db.Integer, db.ForeignKey("word.id"), nullable=False)
    user_answer = db.Column(db.String(500), default="")
    correct_answer = db.Column(db.String(500), nullable=False)
    question_type = db.Column(db.String(30), nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False, default=False)
    question_order = db.Column(db.Integer, nullable=False)

    attempt = db.relationship("ExamRecord", back_populates="answers")
    question = db.relationship("ExamQuestion")
    word = db.relationship("Word")

    def to_dict(self):
        return {
            "id": self.id,
            "word_id": self.word_id,
            "word": self.word.word if self.word else None,
            "prompt": self.word.word if self.question_type == "en_to_cn" else self.word.meaning,
            "correct_answer": self.correct_answer,
            "user_answer": self.user_answer,
            "question_type": self.question_type,
            "is_correct": self.is_correct,
            "question_order": self.question_order,
        }
