from flask import Blueprint, jsonify, request
from auth.decorators import login_required, teacher_required
from models import Word, db

words_bp = Blueprint("words", __name__, url_prefix="/api/words")

@words_bp.get("")
@login_required
def list_words():
    keyword = (request.args.get("q") or "").strip()
    query = Word.query
    if keyword:
        query = query.filter(Word.word.ilike(f"%{keyword}%"))
    return jsonify({"code": 200, "data": [w.to_dict() for w in query.order_by(Word.word).limit(200)]})

@words_bp.post("")
@teacher_required
def create_word():
    data = request.get_json(silent=True) or {}
    word, meaning = (data.get("word") or "").strip().lower(), (data.get("meaning") or "").strip()
    if not word or not meaning:
        return jsonify({"code": 400, "message": "单词和释义不能为空"}), 400
    if Word.query.filter_by(word=word).first():
        return jsonify({"code": 400, "message": "单词已存在"}), 400
    item = Word(word=word, meaning=meaning, phonetic=data.get("phonetic"), level=data.get("level", "CET4"))
    db.session.add(item)
    db.session.commit()
    return jsonify({"code": 200, "message": "添加成功", "data": item.to_dict()})
