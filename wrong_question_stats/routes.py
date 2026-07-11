"""
错题统计模块 - API 路由
提供错题列表、错题汇总、WordCloud数据、错题分布等接口
"""

from flask import Blueprint, request, jsonify
from sqlalchemy import func, extract
from .models import db, ExamRecord, AnswerRecord

wrong_stats_bp = Blueprint('wrong_stats', __name__, url_prefix='/api/wrong_stats')


@wrong_stats_bp.route('/list', methods=['GET'])
def get_wrong_list():
    """
    错题列表接口（分页）
    
    请求参数:
        user_id  (int): 用户ID（必填）
        page     (int): 页码，默认1
        page_size(int): 每页条数，默认20
    
    返回:
        用户所有错题记录，包含考试时间、单词、正确答案、用户答案等
    """
    user_id = request.args.get('user_id', type=int)
    if not user_id:
        return jsonify({'code': 400, 'message': '缺少参数: user_id'}), 400

    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 20, type=int)

    # 查询该用户所有错题，关联考试时间
    query = db.session.query(
        AnswerRecord,
        ExamRecord.exam_date
    ).join(
        ExamRecord, AnswerRecord.exam_id == ExamRecord.id
    ).filter(
        ExamRecord.user_id == user_id,
        AnswerRecord.is_correct == False
    ).order_by(
        ExamRecord.exam_date.desc()
    )

    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()

    wrong_list = []
    for answer, exam_date in items:
        wrong_list.append({
            'id': answer.id,
            'exam_id': answer.exam_id,
            'word_id': answer.word_id,
            'word_text': answer.word_text,
            'correct_answer': answer.correct_answer,
            'user_answer': answer.user_answer,
            'exam_date': exam_date.strftime('%Y-%m-%d %H:%M:%S') if exam_date else None
        })

    return jsonify({
        'code': 200,
        'message': '查询成功',
        'data': {
            'wrong_list': wrong_list,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size
        }
    })


@wrong_stats_bp.route('/summary', methods=['GET'])
def get_wrong_summary():
    """
    错题汇总统计接口
    
    请求参数:
        user_id (int): 用户ID（必填）
    
    返回:
        按单词分组的错题汇总，包含：
        - 每个单词的错误次数
        - 错误率（该单词错误次数/该单词出现总次数）
        - 最近一次错误时间
    """
    user_id = request.args.get('user_id', type=int)
    if not user_id:
        return jsonify({'code': 400, 'message': '缺少参数: user_id'}), 400

    # 子查询：该用户所有考试
    exam_ids = db.session.query(ExamRecord.id).filter_by(user_id=user_id).subquery()

    # 按单词分组统计
    results = db.session.query(
        AnswerRecord.word_text,
        AnswerRecord.correct_answer,
        func.count(AnswerRecord.id).label('wrong_count'),
        func.max(ExamRecord.exam_date).label('last_wrong_date')
    ).join(
        ExamRecord, AnswerRecord.exam_id == ExamRecord.id
    ).filter(
        AnswerRecord.exam_id.in_(exam_ids),
        AnswerRecord.is_correct == False
    ).group_by(
        AnswerRecord.word_text,
        AnswerRecord.correct_answer
    ).order_by(
        func.count(AnswerRecord.id).desc()
    ).all()

    summary = []
    for row in results:
        # 查询该单词总共出现的次数（含正确和错误）
        total_appear = db.session.query(func.count(AnswerRecord.id)).filter(
            AnswerRecord.exam_id.in_(exam_ids),
            AnswerRecord.word_text == row.word_text
        ).scalar()

        summary.append({
            'word': row.word_text,
            'correct_answer': row.correct_answer,
            'wrong_count': row.wrong_count,
            'total_appear': total_appear,
            'error_rate': round(row.wrong_count / total_appear * 100, 2) if total_appear else 0,
            'last_wrong_date': row.last_wrong_date.strftime('%Y-%m-%d %H:%M:%S') if row.last_wrong_date else None
        })

    return jsonify({
        'code': 200,
        'message': '查询成功',
        'data': {
            'summary': summary,
            'total_wrong_types': len(summary),
            'total_wrong_times': sum(s['wrong_count'] for s in summary)
        }
    })


@wrong_stats_bp.route('/wordcloud', methods=['GET'])
def get_wordcloud_data():
    """
    WordCloud 字符云数据接口
    
    请求参数:
        user_id (int): 用户ID（必填）
    
    返回:
        适合 WordCloud2.js 使用的数据格式：
        [['word', weight], ['word', weight], ...]
        权重 = 错误次数，出现越多字体越大
    """
    user_id = request.args.get('user_id', type=int)
    if not user_id:
        return jsonify({'code': 400, 'message': '缺少参数: user_id'}), 400

    exam_ids = db.session.query(ExamRecord.id).filter_by(user_id=user_id).subquery()

    results = db.session.query(
        AnswerRecord.word_text,
        func.count(AnswerRecord.id).label('weight')
    ).filter(
        AnswerRecord.exam_id.in_(exam_ids),
        AnswerRecord.is_correct == False
    ).group_by(
        AnswerRecord.word_text
    ).order_by(
        func.count(AnswerRecord.id).desc()
    ).all()

    # WordCloud2.js 格式: [['word', weight], ['word', weight], ...]
    wordcloud_data = [[row.word_text, row.weight] for row in results]

    return jsonify({
        'code': 200,
        'message': '查询成功',
        'data': {
            'wordcloud': wordcloud_data,
            'total_words': len(wordcloud_data)
        }
    })


@wrong_stats_bp.route('/distribution', methods=['GET'])
def get_wrong_distribution():
    """
    错题分布统计接口
    
    请求参数:
        user_id (int): 用户ID（必填）
    
    返回:
        按考试分组的错题分布，每场考试的错题数量和时间
    """
    user_id = request.args.get('user_id', type=int)
    if not user_id:
        return jsonify({'code': 400, 'message': '缺少参数: user_id'}), 400

    results = db.session.query(
        ExamRecord.id,
        ExamRecord.exam_date,
        ExamRecord.score,
        ExamRecord.total_questions,
        ExamRecord.wrong_count,
        func.group_concat(AnswerRecord.word_text).label('wrong_words')
    ).join(
        AnswerRecord, ExamRecord.id == AnswerRecord.exam_id
    ).filter(
        ExamRecord.user_id == user_id,
        AnswerRecord.is_correct == False
    ).group_by(
        ExamRecord.id
    ).order_by(
        ExamRecord.exam_date.desc()
    ).all()

    distribution = []
    for row in results:
        wrong_words = row.wrong_words.split(',') if row.wrong_words else []
        distribution.append({
            'exam_id': row.id,
            'exam_date': row.exam_date.strftime('%Y-%m-%d %H:%M:%S') if row.exam_date else None,
            'score': row.score,
            'total_questions': row.total_questions,
            'wrong_count': row.wrong_count,
            'wrong_words': wrong_words
        })

    return jsonify({
        'code': 200,
        'message': '查询成功',
        'data': {
            'distribution': distribution,
            'total_exams_with_wrong': len(distribution)
        }
    })


@wrong_stats_bp.route('/recent', methods=['GET'])
def get_recent_wrong():
    """
    最近错题接口（快速查看最近做错的题目）
    
    请求参数:
        user_id (int): 用户ID（必填）
        limit   (int): 返回条数，默认10
    
    返回:
        最近 N 道错题，按考试时间倒序
    """
    user_id = request.args.get('user_id', type=int)
    if not user_id:
        return jsonify({'code': 400, 'message': '缺少参数: user_id'}), 400

    limit = request.args.get('limit', 10, type=int)

    results = db.session.query(
        AnswerRecord,
        ExamRecord.exam_date
    ).join(
        ExamRecord, AnswerRecord.exam_id == ExamRecord.id
    ).filter(
        ExamRecord.user_id == user_id,
        AnswerRecord.is_correct == False
    ).order_by(
        ExamRecord.exam_date.desc()
    ).limit(limit).all()

    recent = []
    for answer, exam_date in results:
        recent.append({
            'id': answer.id,
            'exam_id': answer.exam_id,
            'word_text': answer.word_text,
            'correct_answer': answer.correct_answer,
            'user_answer': answer.user_answer,
            'exam_date': exam_date.strftime('%Y-%m-%d %H:%M:%S') if exam_date else None
        })

    return jsonify({
        'code': 200,
        'message': '查询成功',
        'data': {
            'recent_wrong': recent,
            'count': len(recent)
        }
    })