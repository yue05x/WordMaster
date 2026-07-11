import random
import re
from datetime import datetime, timedelta

from flask import Blueprint, g, jsonify, request
from auth.decorators import login_required, teacher_required
from models import AnswerRecord, Exam, ExamQuestion, ExamRecord, Word, db

exam_bp = Blueprint("exam", __name__, url_prefix="/api/exams")

def parse_time(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)

def normalize(value):
    return re.sub(r"\s+", " ", (value or "").strip().lower())

def validate_exam_window(start_time, end_time, duration_minutes):
    if end_time <= start_time:
        return "结束时间必须晚于开始时间"
    if end_time - start_time < timedelta(minutes=duration_minutes):
        return f"考试开放时间不能少于个人限时 {duration_minutes} 分钟"
    return None

@exam_bp.get("")
@login_required
def list_exams():
    return jsonify({"code": 200, "data": [e.to_dict() for e in Exam.query.order_by(Exam.start_time.desc()).all()]})

@exam_bp.get("/<int:exam_id>")
@login_required
def exam_detail(exam_id):
    exam = db.session.get(Exam, exam_id)
    if not exam:
        return jsonify({"code": 404, "message": "考试不存在"}), 404
    return jsonify({"code": 200, "data": exam.to_dict(g.current_user.role == "teacher")})

@exam_bp.post("")
@teacher_required
def create_exam():
    data = request.get_json(silent=True) or {}
    try:
        title = (data.get("title") or "").strip()
        count = int(data.get("question_count", 10))
        start_time, end_time = parse_time(data["start_time"]), parse_time(data["end_time"])
        duration = int(data.get("duration_minutes", 30))
    except (KeyError, TypeError, ValueError):
        return jsonify({"code": 400, "message": "考试参数格式错误"}), 400
    words = Word.query.all()
    if not title or count < 1 or duration < 1:
        return jsonify({"code": 400, "message": "考试名称、时间或题数无效"}), 400
    window_error = validate_exam_window(start_time, end_time, duration)
    if window_error:
        return jsonify({"code": 400, "message": window_error}), 400
    if len(words) < count:
        return jsonify({"code": 400, "message": f"单词库只有 {len(words)} 个单词"}), 400
    exam = Exam(title=title, description=data.get("description", ""), creator_id=g.current_user.id,
                start_time=start_time, end_time=end_time, duration_minutes=duration)
    db.session.add(exam)
    db.session.flush()
    for index, word in enumerate(random.sample(words, count), 1):
        db.session.add(ExamQuestion(exam_id=exam.id, word_id=word.id, question_type="en_to_cn", base_order=index))
    db.session.commit()
    return jsonify({"code": 200, "message": "考试发布成功", "data": exam.to_dict(True)})

@exam_bp.put("/<int:exam_id>")
@teacher_required
def update_exam(exam_id):
    exam = db.session.get(Exam, exam_id)
    if not exam:
        return jsonify({"code": 404, "message": "考试不存在"}), 404
    if exam.attempts.count():
        return jsonify({"code": 400, "message": "已有学生进入考试，不能修改"}), 400
    data = request.get_json(silent=True) or {}
    try:
        if "start_time" in data:
            exam.start_time = parse_time(data["start_time"])
        if "end_time" in data:
            exam.end_time = parse_time(data["end_time"])
        if "duration_minutes" in data:
            exam.duration_minutes = int(data["duration_minutes"])
    except (TypeError, ValueError):
        return jsonify({"code": 400, "message": "考试参数格式错误"}), 400
    exam.title = (data.get("title") or exam.title).strip()
    exam.description = data.get("description", exam.description)
    if not exam.title or exam.duration_minutes < 1:
        return jsonify({"code": 400, "message": "考试名称或时间无效"}), 400
    window_error = validate_exam_window(exam.start_time, exam.end_time, exam.duration_minutes)
    if window_error:
        return jsonify({"code": 400, "message": window_error}), 400
    db.session.commit()
    return jsonify({"code": 200, "message": "考试修改成功", "data": exam.to_dict(True)})

@exam_bp.delete("/<int:exam_id>")
@teacher_required
def delete_exam(exam_id):
    exam = db.session.get(Exam, exam_id)
    if not exam:
        return jsonify({"code": 404, "message": "考试不存在"}), 404
    if exam.attempts.count():
        return jsonify({"code": 400, "message": "考试已有答题记录，不能删除"}), 400
    db.session.delete(exam)
    db.session.commit()
    return jsonify({"code": 200, "message": "考试删除成功"})

@exam_bp.post("/<int:exam_id>/start")
@login_required
def start_exam(exam_id):
    if g.current_user.role != "student":
        return jsonify({"code": 403, "message": "教师账号不能参加考试"}), 403
    exam = db.session.get(Exam, exam_id)
    if not exam:
        return jsonify({"code": 404, "message": "考试不存在"}), 404
    if exam.effective_status() != "running":
        return jsonify({"code": 400, "message": "考试尚未开始或已经结束"}), 400
    attempt = ExamRecord.query.filter_by(exam_id=exam.id, user_id=g.current_user.id).first()
    if attempt and attempt.status == "submitted":
        return jsonify({"code": 400, "message": "你已经提交过本场考试"}), 400
    if not attempt:
        attempt = ExamRecord(exam_id=exam.id, user_id=g.current_user.id, total_questions=len(exam.questions))
        db.session.add(attempt)
        db.session.commit()
    questions = list(exam.questions)
    random.Random(f"{exam.id}:{g.current_user.id}").shuffle(questions)
    payload = [{"question_id": q.id, "order": order, "prompt": q.word.word,
                "phonetic": q.word.phonetic, "question_type": q.question_type}
               for order, q in enumerate(questions, 1)]
    deadline = min(exam.end_time, attempt.start_time + timedelta(minutes=exam.duration_minutes))
    return jsonify({"code": 200, "data": {"attempt_id": attempt.id, "exam": exam.to_dict(),
                    "deadline": deadline.isoformat() + "Z", "questions": payload}})

@exam_bp.post("/attempts/<int:attempt_id>/submit")
@login_required
def submit_exam(attempt_id):
    attempt = ExamRecord.query.filter_by(id=attempt_id, user_id=g.current_user.id).first()
    if not attempt:
        return jsonify({"code": 404, "message": "答题记录不存在"}), 404
    if attempt.status == "submitted":
        return jsonify({"code": 400, "message": "试卷不可重复提交"}), 400
    deadline = min(attempt.exam.end_time, attempt.start_time + timedelta(minutes=attempt.exam.duration_minutes))
    if datetime.utcnow() > deadline + timedelta(seconds=30):
        return jsonify({"code": 400, "message": "考试已超时"}), 400
    try:
        submitted = {int(a["question_id"]): a.get("answer", "") for a in (request.json or {}).get("answers", [])}
    except (KeyError, TypeError, ValueError):
        return jsonify({"code": 400, "message": "答案格式错误"}), 400
    questions = {q.id: q for q in attempt.exam.questions}
    if set(submitted) != set(questions):
        return jsonify({"code": 400, "message": "提交题目与本场试卷不一致"}), 400
    ordered = list(attempt.exam.questions)
    random.Random(f"{attempt.exam_id}:{g.current_user.id}").shuffle(ordered)
    correct = 0
    for order, question in enumerate(ordered, 1):
        user_answer = submitted[question.id]
        accepted = [normalize(x) for x in re.split(r"[;；,，/]", question.word.meaning)]
        is_correct = normalize(user_answer) in accepted
        correct += int(is_correct)
        db.session.add(AnswerRecord(attempt_id=attempt.id, exam_question_id=question.id,
            word_id=question.word_id, user_answer=user_answer, correct_answer=question.word.meaning,
            question_type=question.question_type, is_correct=is_correct, question_order=order))
    attempt.correct_count, attempt.score = correct, round(correct / attempt.total_questions * 100, 2)
    attempt.status, attempt.end_time = "submitted", datetime.utcnow()
    db.session.commit()
    return jsonify({"code": 200, "message": "交卷成功", "data": attempt.to_dict(True)})

@exam_bp.get("/records")
@login_required
def records():
    query = ExamRecord.query.filter_by(status="submitted")
    if g.current_user.role != "teacher":
        query = query.filter_by(user_id=g.current_user.id)
    return jsonify({"code": 200, "data": [r.to_dict() for r in query.order_by(ExamRecord.end_time.desc()).all()]})

@exam_bp.get("/records/<int:record_id>")
@login_required
def record_detail(record_id):
    row = db.session.get(ExamRecord, record_id)
    if not row or (g.current_user.role != "teacher" and row.user_id != g.current_user.id):
        return jsonify({"code": 404, "message": "成绩不存在"}), 404
    return jsonify({"code": 200, "data": row.to_dict(True)})
