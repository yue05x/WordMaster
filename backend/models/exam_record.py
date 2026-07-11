from datetime import datetime

from . import db


class ExamRecord(db.Model):
    """A student's attempt at one published exam."""

    __tablename__ = "exam_record"
    __table_args__ = (db.UniqueConstraint("exam_id", "user_id", name="uq_exam_attempt"),)

    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, db.ForeignKey("exam.id"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    total_questions = db.Column(db.Integer, nullable=False)
    correct_count = db.Column(db.Integer, default=0)
    score = db.Column(db.Numeric(5, 2), default=0)
    status = db.Column(db.String(20), default="in_progress")
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)

    exam = db.relationship("Exam", back_populates="attempts")
    user = db.relationship("User", back_populates="attempts")
    answers = db.relationship(
        "AnswerRecord", back_populates="attempt", order_by="AnswerRecord.question_order",
        cascade="all, delete-orphan"
    )

    def duration_seconds(self):
        if not self.start_time or not self.end_time:
            return None
        return int((self.end_time - self.start_time).total_seconds())

    def to_dict(self, include_answers=False):
        data = {
            "id": self.id,
            "exam_id": self.exam_id,
            "exam_title": self.exam.title if self.exam else None,
            "user_id": self.user_id,
            "student_name": self.user.nickname or self.user.username if self.user else None,
            "total_questions": self.total_questions,
            "correct_count": self.correct_count,
            "score": float(self.score or 0),
            "status": self.status,
            "start_time": self.start_time.isoformat() + "Z" if self.start_time else None,
            "end_time": self.end_time.isoformat() + "Z" if self.end_time else None,
            "duration_seconds": self.duration_seconds(),
        }
        if include_answers:
            data["answers"] = [a.to_dict() for a in self.answers]
        return data
