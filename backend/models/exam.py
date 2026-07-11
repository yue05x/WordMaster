from datetime import datetime

from . import db


class Exam(db.Model):
    __tablename__ = "exam"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(500), default="")
    creator_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False, default=30)
    status = db.Column(db.String(20), nullable=False, default="published")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    creator = db.relationship("User", foreign_keys=[creator_id])
    questions = db.relationship(
        "ExamQuestion", back_populates="exam", order_by="ExamQuestion.base_order",
        cascade="all, delete-orphan"
    )
    attempts = db.relationship("ExamRecord", back_populates="exam", lazy="dynamic")

    def effective_status(self):
        now = datetime.utcnow()
        if self.status == "draft":
            return "draft"
        if now < self.start_time:
            return "upcoming"
        if now > self.end_time:
            return "finished"
        return "running"

    def to_dict(self, include_questions=False):
        data = {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "creator_id": self.creator_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "duration_minutes": self.duration_minutes,
            "status": self.effective_status(),
            "question_count": len(self.questions),
        }
        if include_questions:
            data["questions"] = [q.to_dict() for q in self.questions]
        return data


class ExamQuestion(db.Model):
    __tablename__ = "exam_question"
    __table_args__ = (db.UniqueConstraint("exam_id", "word_id", name="uq_exam_word"),)

    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, db.ForeignKey("exam.id"), nullable=False, index=True)
    word_id = db.Column(db.Integer, db.ForeignKey("word.id"), nullable=False)
    question_type = db.Column(db.String(30), nullable=False, default="en_to_cn")
    base_order = db.Column(db.Integer, nullable=False)

    exam = db.relationship("Exam", back_populates="questions")
    word = db.relationship("Word")

    def to_dict(self):
        return {
            "id": self.id,
            "word_id": self.word_id,
            "question_type": self.question_type,
            "base_order": self.base_order,
            "word": self.word.word,
            "meaning": self.word.meaning,
        }
