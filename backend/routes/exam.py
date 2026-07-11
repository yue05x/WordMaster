from datetime import datetime

from flask import Blueprint, current_app, g, jsonify, request

from auth.decorators import login_required
from models import ExamRecord, db
from services.exam_service import generate_exam_questions, grade_exam

exam_bp = Blueprint("exam", __name__, url_prefix="/api/exam")


@exam_bp.route("/start", methods=["POST"])
@login_required
def start_exam():
    data = request.get_json(silent=True) or {}
    question_count = data.get("question_count")

    if question_count is not None:
        try:
            question_count = int(question_count)
            if question_count < 1 or question_count > 100:
                return jsonify({"code": 400, "message": "题目数量应在1-100之间"}), 400
        except (TypeError, ValueError):
            return jsonify({"code": 400, "message": "题目数量格式无效"}), 400

    try:
        exam, questions = generate_exam_questions(g.current_user.id, question_count)
        db.session.commit()
    except ValueError as e:
        db.session.rollback()
        return jsonify({"code": 400, "message": str(e)}), 400

    duration_minutes = current_app.config["EXAM_DURATION_MINUTES"]
    return jsonify(
        {
            "code": 200,
            "message": "考试已开始",
            "data": {
                "exam_id": exam.id,
                "total_questions": exam.total_questions,
                "questions": questions,
                "start_time": exam.start_time.isoformat() if exam.start_time else None,
                "duration_minutes": duration_minutes,
            },
        }
    )


@exam_bp.route("/submit", methods=["POST"])
@login_required
def submit_exam():
    data = request.get_json(silent=True) or {}
    exam_id = data.get("exam_id")
    answers = data.get("answers") or []

    if not exam_id:
        return jsonify({"code": 400, "message": "缺少考试ID"}), 400
    if not answers:
        return jsonify({"code": 400, "message": "请提交答案"}), 400

    exam = ExamRecord.query.filter_by(id=exam_id, user_id=g.current_user.id).first()
    if not exam:
        return jsonify({"code": 404, "message": "考试记录不存在"}), 404
    if exam.status == "submitted":
        return jsonify({"code": 400, "message": "该考试已提交，不可重复提交"}), 400
    if len(answers) != exam.total_questions:
        return jsonify({"code": 400, "message": "答案数量与题目数量不匹配"}), 400

    duration_minutes = current_app.config["EXAM_DURATION_MINUTES"]
    if exam.start_time:
        elapsed_seconds = (datetime.utcnow() - exam.start_time).total_seconds()
        if elapsed_seconds > duration_minutes * 60 + 30:
            return jsonify({"code": 400, "message": "考试已超时，请重新开始考试"}), 400

    result = grade_exam(exam, answers)
    db.session.commit()

    return jsonify(
        {
            "code": 200,
            "message": "提交成功",
            "data": {
                "exam_id": exam.id,
                "correct_count": result["correct_count"],
                "total_questions": result["total_questions"],
                "score": result["score"],
                "start_time": result["start_time"],
                "end_time": result["end_time"],
                "duration_seconds": result["duration_seconds"],
                "answers": result["answers"],
            },
        }
    )


@exam_bp.route("/records", methods=["GET"])
@login_required
def get_exam_records():
    records = (
        ExamRecord.query.filter_by(user_id=g.current_user.id, status="submitted")
        .order_by(ExamRecord.end_time.desc())
        .all()
    )
    return jsonify({"code": 200, "data": [r.to_dict() for r in records]})


@exam_bp.route("/<int:exam_id>", methods=["GET"])
@login_required
def get_exam_detail(exam_id):
    exam = ExamRecord.query.filter_by(id=exam_id, user_id=g.current_user.id).first()
    if not exam:
        return jsonify({"code": 404, "message": "考试记录不存在"}), 404

    return jsonify({"code": 200, "data": exam.to_dict(include_answers=True)})
