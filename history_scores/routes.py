"""
历史成绩查询模块 - API 路由
提供历史成绩查询、考试详情、错题统计等接口
"""

from flask import Blueprint, request, jsonify
from .models import db, ExamRecord, AnswerRecord

history_scores_bp = Blueprint('history_scores', __name__, url_prefix='/api/history')


@history_scores_bp.route('/scores', methods=['GET'])
def get_history_scores():
    """
    历史成绩查询接口
    
    请求参数:
        user_id (int): 用户ID（必填）
        page (int): 页码，默认1
        page_size (int): 每页条数，默认10
    
    返回:
        用户的所有历史考试成绩，按考试时间倒序排列，支持分页
    """
    user_id = request.args.get('user_id', type=int)
    if not user_id:
        return jsonify({'code': 400, 'message': '缺少参数: user_id'}), 400

    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)

    # 分页查询，按考试时间倒序
    pagination = ExamRecord.query \
        .filter_by(user_id=user_id) \
        .order_by(ExamRecord.exam_date.desc()) \
        .paginate(page=page, per_page=page_size, error_out=False)

    records = [r.to_dict() for r in pagination.items]

    return jsonify({
        'code': 200,
        'message': '查询成功',
        'data': {
            'records': records,
            'total': pagination.total,
            'page': pagination.page,
            'page_size': pagination.page_size,
            'total_pages': pagination.pages
        }
    })


@history_scores_bp.route('/scores/<int:exam_id>', methods=['GET'])
def get_exam_detail(exam_id):
    """
    单次考试详情查询接口
    
    路径参数:
        exam_id (int): 考试记录ID
    
    返回:
        该次考试的详细信息，包括考试成绩和所有答题记录
    """
    exam = ExamRecord.query.get(exam_id)
    if not exam:
        return jsonify({'code': 404, 'message': '考试记录不存在'}), 404

    answers = AnswerRecord.query.filter_by(exam_id=exam_id).all()

    return jsonify({
        'code': 200,
        'message': '查询成功',
        'data': {
            'exam': exam.to_dict(),
            'answers': [a.to_dict() for a in answers]
        }
    })


@history_scores_bp.route('/wrong_stats', methods=['GET'])
def get_wrong_stats():
    """
    错题统计接口（用于 WordCloud 字符云展示）
    
    请求参数:
        user_id (int): 用户ID（必填）
    
    返回:
        用户所有错题单词及出现次数统计，按错误次数降序排列
    """
    user_id = request.args.get('user_id', type=int)
    if not user_id:
        return jsonify({'code': 400, 'message': '缺少参数: user_id'}), 400

    # 查询该用户所有考试记录ID
    exam_ids = db.session.query(ExamRecord.id).filter_by(user_id=user_id).subquery()

    # 统计每个错题单词的错误次数
    results = db.session.query(
        AnswerRecord.word_text,
        AnswerRecord.correct_answer,
        db.func.count(AnswerRecord.id).label('wrong_count')
    ).filter(
        AnswerRecord.exam_id.in_(exam_ids),
        AnswerRecord.is_correct == False
    ).group_by(
        AnswerRecord.word_text,
        AnswerRecord.correct_answer
    ).order_by(
        db.func.count(AnswerRecord.id).desc()
    ).all()

    wrong_stats = [
        {
            'word': row.word_text,
            'correct_answer': row.correct_answer,
            'wrong_count': row.wrong_count
        }
        for row in results
    ]

    return jsonify({
        'code': 200,
        'message': '查询成功',
        'data': {
            'wrong_stats': wrong_stats,
            'total_wrong_types': len(wrong_stats)
        }
    })


@history_scores_bp.route('/overview', methods=['GET'])
def get_score_overview():
    """
    成绩总览接口
    
    请求参数:
        user_id (int): 用户ID（必填）
    
    返回:
        用户成绩总览，包括考试总次数、平均分、最高分、最低分、总正确率等
    """
    user_id = request.args.get('user_id', type=int)
    if not user_id:
        return jsonify({'code': 400, 'message': '缺少参数: user_id'}), 400

    records = ExamRecord.query.filter_by(user_id=user_id).all()

    if not records:
        return jsonify({
            'code': 200,
            'message': '暂无考试记录',
            'data': {
                'total_exams': 0,
                'avg_score': 0,
                'max_score': 0,
                'min_score': 0,
                'total_accuracy': 0,
                'total_questions_done': 0,
                'total_correct': 0
            }
        })

    total_exams = len(records)
    scores = [r.score for r in records]
    total_questions = sum(r.total_questions for r in records)
    total_correct = sum(r.correct_count for r in records)

    return jsonify({
        'code': 200,
        'message': '查询成功',
        'data': {
            'total_exams': total_exams,
            'avg_score': round(sum(scores) / total_exams, 2),
            'max_score': max(scores),
            'min_score': min(scores),
            'total_accuracy': round(total_correct / total_questions * 100, 2) if total_questions > 0 else 0,
            'total_questions_done': total_questions,
            'total_correct': total_correct
        }
    })