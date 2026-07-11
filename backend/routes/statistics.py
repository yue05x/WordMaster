from datetime import datetime, timedelta
from flask import Blueprint, g, jsonify, request
from sqlalchemy import func
from auth.decorators import login_required
from models import AnswerRecord, ExamRecord, User, Word, db

statistics_bp = Blueprint("statistics", __name__, url_prefix="/api/statistics")

def attempts_query():
    query = ExamRecord.query.filter_by(status="submitted")
    return query if g.current_user.role == "teacher" else query.filter_by(user_id=g.current_user.id)

@statistics_bp.get("/overview")
@login_required
def overview():
    rows = attempts_query().all()
    scores = [float(row.score or 0) for row in rows]
    return jsonify({"code": 200, "data": {"exam_count": len(rows),
        "average_score": round(sum(scores) / len(scores), 2) if scores else 0,
        "highest_score": max(scores) if scores else 0,
        "lowest_score": min(scores) if scores else 0}})

@statistics_bp.get("/wordcloud")
@login_required
def wordcloud():
    days = max(1, min(request.args.get("days", 7, type=int), 365))
    attempt_ids = attempts_query().filter(ExamRecord.end_time >= datetime.utcnow() - timedelta(days=days)).with_entities(ExamRecord.id)
    rows = (db.session.query(Word.word, Word.meaning, func.count(AnswerRecord.id).label("weight"))
        .join(AnswerRecord, AnswerRecord.word_id == Word.id)
        .filter(AnswerRecord.attempt_id.in_(attempt_ids), AnswerRecord.is_correct.is_(False))
        .group_by(Word.id).order_by(func.count(AnswerRecord.id).desc()).limit(60).all())
    return jsonify({"code": 200, "data": [{"word": w, "meaning": m, "weight": n} for w, m, n in rows]})


@statistics_bp.get("/trend")
@login_required
def trend():
    rows = attempts_query().order_by(ExamRecord.end_time.desc()).limit(12).all()
    rows.reverse()
    return jsonify({"code": 200, "data": [
        {"id": row.id, "exam": row.exam.title, "student": row.user.nickname or row.user.username,
         "score": float(row.score or 0), "date": row.end_time.isoformat() + "Z"}
        for row in rows
    ]})


@statistics_bp.get("/leaderboard")
@login_required
def leaderboard():
    rows = (db.session.query(
            User.id, User.nickname, User.username,
            func.avg(ExamRecord.score).label("average_score"),
            func.max(ExamRecord.score).label("highest_score"),
            func.count(ExamRecord.id).label("exam_count"))
        .join(ExamRecord, ExamRecord.user_id == User.id)
        .filter(ExamRecord.status == "submitted", User.role == "student")
        .group_by(User.id)
        .order_by(func.avg(ExamRecord.score).desc(), func.max(ExamRecord.score).desc())
        .limit(10).all())
    return jsonify({"code": 200, "data": [
        {"rank": index, "student": nickname or username,
         "average_score": round(float(average or 0), 2),
         "highest_score": float(highest or 0), "exam_count": count}
        for index, (_, nickname, username, average, highest, count) in enumerate(rows, 1)
    ]})
