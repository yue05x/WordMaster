from datetime import datetime, timedelta
from flask import Blueprint, g, jsonify, request
from sqlalchemy import func
from auth.decorators import login_required
from models import AnswerRecord, ExamRecord, Word, db

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
