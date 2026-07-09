from flask import Blueprint, request, jsonify
from models import db, Word

words_bp = Blueprint('words', __name__)

@words_bp.route('/words', methods=['GET'])
def search_words():
    keyword = request.args.get('q', '')
    if keyword:
        words = Word.query.filter(Word.word.like(f'%{keyword}%')).all()
    else:
        words = Word.query.limit(20).all()
    return jsonify([w.to_dict() for w in words])