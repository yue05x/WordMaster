"""Create idempotent demonstration exams and results in the configured database."""
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import create_app
from auth.decorators import hash_password
from models import AnswerRecord, Exam, ExamQuestion, ExamRecord, User, Word, db


DEMO_STUDENTS = [
    ("demo_alice", "林晓雨"), ("demo_bob", "陈子轩"),
    ("demo_carol", "周思涵"), ("demo_david", "王浩然"),
]


def ensure_user(username, nickname, role="student"):
    user = User.query.filter_by(username=username).first()
    if not user:
        user = User(username=username, nickname=nickname, role=role,
                    password=hash_password("123456"))
        db.session.add(user)
        db.session.flush()
    return user


def ensure_exam(title, creator, start, end, count=12, duration=30):
    exam = Exam.query.filter_by(title=title).first()
    if exam:
        return exam
    exam = Exam(title=title, description="WordMaster 演示数据", creator_id=creator.id,
                start_time=start, end_time=end, duration_minutes=duration)
    db.session.add(exam)
    db.session.flush()
    words = Word.query.order_by(Word.id).limit(count).all()
    for order, word in enumerate(words, 1):
        db.session.add(ExamQuestion(exam_id=exam.id, word_id=word.id,
                                    question_type="en_to_cn", base_order=order))
    db.session.flush()
    return exam


def ensure_result(exam, student, target_score, days_ago):
    if ExamRecord.query.filter_by(exam_id=exam.id, user_id=student.id).first():
        return
    questions = list(exam.questions)
    correct_target = round(len(questions) * target_score / 100)
    end_time = datetime.utcnow() - timedelta(days=days_ago)
    attempt = ExamRecord(exam_id=exam.id, user_id=student.id,
                         total_questions=len(questions), correct_count=correct_target,
                         score=round(correct_target / len(questions) * 100, 2),
                         status="submitted", start_time=end_time - timedelta(minutes=18),
                         end_time=end_time)
    db.session.add(attempt)
    db.session.flush()
    shuffled = questions[:]
    random.Random(f"demo:{exam.id}:{student.id}").shuffle(shuffled)
    for order, question in enumerate(shuffled, 1):
        correct = order <= correct_target
        db.session.add(AnswerRecord(
            attempt_id=attempt.id, exam_question_id=question.id, word_id=question.word_id,
            user_answer=question.word.meaning.split("；")[0] if correct else "未掌握",
            correct_answer=question.word.meaning, question_type="en_to_cn",
            is_correct=correct, question_order=order))


def seed_demo():
    teacher = ensure_user("demo_teacher", "张老师", "teacher")
    students = [ensure_user(username, nickname) for username, nickname in DEMO_STUDENTS]
    now = datetime.utcnow()
    history = [
        ensure_exam("CET4 基础词汇摸底", teacher, now - timedelta(days=16), now - timedelta(days=15)),
        ensure_exam("第二周核心词汇测试", teacher, now - timedelta(days=9), now - timedelta(days=8)),
        ensure_exam("本周多义词专项训练", teacher, now - timedelta(days=3), now - timedelta(days=2)),
    ]
    ensure_exam("今日英语单词挑战", teacher, now - timedelta(hours=1), now + timedelta(hours=5), 15, 25)
    ensure_exam("下周综合能力测试", teacher, now + timedelta(days=2), now + timedelta(days=3), 20, 40)
    score_matrix = [[68, 78, 88], [75, 83, 92], [58, 72, 82], [82, 86, 95]]
    for student, scores in zip(students, score_matrix):
        for index, (exam, score) in enumerate(zip(history, scores)):
            ensure_result(exam, student, score, 15 - index * 6)
    db.session.commit()


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        seed_demo()
        print("Demo data ready: password for demo accounts is 123456")
