from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .user import User  # noqa: E402, F401
from .word import Word  # noqa: E402, F401
from .exam_record import ExamRecord  # noqa: E402, F401
from .answer_record import AnswerRecord  # noqa: E402, F401
