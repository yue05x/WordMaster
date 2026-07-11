import os
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "wordmaster-dev-secret-key")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///wordmaster.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_EXPIRATION = timedelta(hours=24)
    DEFAULT_EXAM_QUESTION_COUNT = int(os.getenv("DEFAULT_EXAM_QUESTION_COUNT", "20"))
    EXAM_DURATION_MINUTES = int(os.getenv("EXAM_DURATION_MINUTES", "30"))
