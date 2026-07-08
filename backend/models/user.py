from datetime import datetime

from . import db


class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    nickname = db.Column(db.String(50))
    email = db.Column(db.String(100))
    status = db.Column(db.SmallInteger, default=1)
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    update_time = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    exam_records = db.relationship("ExamRecord", back_populates="user", lazy="dynamic")

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "nickname": self.nickname or self.username,
            "email": self.email,
            "create_time": self.create_time.isoformat() if self.create_time else None,
        }
