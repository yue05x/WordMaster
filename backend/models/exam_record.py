from datetime import datetime

from . import db


class ExamRecord(db.Model):
    __tablename__ = "exam_record"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)
    correct_count = db.Column(db.Integer, default=0)
    score = db.Column(db.Numeric(5, 2), default=0)
    status = db.Column(db.String(20), default="in_progress")
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)

    user = db.relationship("User", back_populates="exam_records")
    answers = db.relationship(
        "AnswerRecord", back_populates="exam", lazy="dynamic", cascade="all, delete-orphan"
    )

    def duration_seconds(self):
        if not self.start_time or not self.end_time:
            return None
        return int((self.end_time - self.start_time).total_seconds())

    def to_dict(self, include_answers=False):
        data = {
            "id": self.id,
            "user_id": self.user_id,
            "total_questions": self.total_questions,
            "correct_count": self.correct_count,
            "score": float(self.score) if self.score is not None else 0,
            "status": self.status,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": self.duration_seconds(),
        }
        if include_answers:
            data["answers"] = [a.to_dict() for a in self.answers.order_by(AnswerRecord.question_order)]
        return data


from .answer_record import AnswerRecord  # noqa: E402
