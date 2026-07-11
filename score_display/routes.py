"""
成绩展示模块 - API 路由
提供考试详情展示、成绩趋势、成绩总览等接口
"""

from flask import Blueprint, request, jsonify
from sqlalchemy import func
from .models import db, ExamRecord, AnswerRecord

score_display_bp = Blueprint('score_display', __name__, url_prefix='/api/score_display')


@score_display_bp.route('/exam/<int:exam_id>', methods=['GET'])
def get_exam_result(exam_id):
    """
    单次考试成绩展示接口
    
    返回:
        - 考试成绩概览（分数、正确率、用时等）
        - 正确题目列表
        - 错误题目列表（含正确答案和用户答案对比）
    """
    exam = ExamRecord.query.get(exam_id)
    if not exam:
        return jsonify({'code': 404, 'message': '考试记录不存在'}), 404

    # 获取所有答题记录
    answers = AnswerRecord.query.filter_by(exam_id=exam_id).all()

    correct_list = []
    wrong_list = []

    for a in answers:
        item = {
            'id': a.id,
            'word_id': a.word_id,
            'word_text': a.word_text,
            'correct_answer': a.correct_answer,
            'user_answer': a.user_answer
        }
        if a.is_correct:
            correct_list.append(item)
        else:
            wrong_list.append(item)

    return jsonify({
        'code': 200,
        'message': '查询成功',
        'data': {
            'exam': exam.to_dict(),
            'correct_list': correct_list,
            'wrong_list': wrong_list,
            'correct_count': len(correct_list),
            'wrong_count': len(wrong_list)
        }
    })


@score_display_bp.route('/trend', methods=['GET'])
def get_score_trend():
    """
    成绩趋势接口（用于折线图展示）
    
    请求参数:
        user_id   (int): 用户ID（必填）
        limit     (int): 最近N场考试，默认10
    
    返回:
        按时间排序的历次考试成绩数据，适合前端绑定折线图
        包含：考试时间、分数、正确率、题目数
    """
    user_id = request.args.get('user_id', type=int)
    if not user_id:
        return jsonify({'code': 400, 'message': '缺少参数: user_id'}), 400

    limit = request.args.get('limit', 10, type=int)

    records = ExamRecord.query \
        .filter_by(user_id=user_id) \
        .order_by(ExamRecord.exam_date.asc()) \
        .limit(limit) \
        .all()

    trend_data = []
    for r in records:
        trend_data.append({
            'exam_id': r.id,
            'exam_date': r.exam_date.strftime('%Y-%m-%d %H:%M:%S') if r.exam_date else None,
            'score': r.score,
            'accuracy': round(r.correct_count / r.total_questions * 100, 2) if r.total_questions > 0 else 0,
            'total_questions': r.total_questions,
            'correct_count': r.correct_count,
            'wrong_count': r.wrong_count,
            'duration': r.duration
        })

    # 计算进步情况
    improvement = None
    if len(trend_data) >= 2:
        first_score = trend_data[0]['score']
        last_score = trend_data[-1]['score']
        improvement = {
            'first_score': first_score,
            'last_score': last_score,
            'change': round(last_score - first_score, 2),
            'improved': last_score > first_score
        }

    return jsonify({
        'code': 200,
        'message': '查询成功',
        'data': {
            'trend': trend_data,
            'total_exams': len(trend_data),
            'improvement': improvement
        }
    })


@score_display_bp.route('/overview', methods=['GET'])
def get_score_overview():
    """
    成绩总览接口（用于成绩展示页面顶部统计卡片）
    
    请求参数:
        user_id (int): 用户ID（必填）
    
    返回:
        - 考试总次数、累计答题数
        - 平均分、最高分、最低分
        - 总正确率
        - 最近一次考试成绩
        - 分数段分布（0-60, 60-80, 80-90, 90-100）
    """
    user_id = request.args.get('user_id', type=int)
    if not user_id:
        return jsonify({'code': 400, 'message': '缺少参数: user_id'}), 400

    records = ExamRecord.query \
        .filter_by(user_id=user_id) \
        .order_by(ExamRecord.exam_date.desc()) \
        .all()

    if not records:
        return jsonify({
            'code': 200,
            'message': '暂无考试记录',
            'data': {
                'total_exams': 0,
                'total_questions': 0,
                'avg_score': 0,
                'max_score': 0,
                'min_score': 0,
                'total_accuracy': 0,
                'latest_exam': None,
                'score_distribution': {'0-60': 0, '60-80': 0, '80-90': 0, '90-100': 0}
            }
        })

    total_exams = len(records)
    total_questions = sum(r.total_questions for r in records)
    total_correct = sum(r.correct_count for r in records)
    scores = [r.score for r in records]

    # 分数段分布
    distribution = {'0-60': 0, '60-80': 0, '80-90': 0, '90-100': 0}
    for s in scores:
        if s < 60:
            distribution['0-60'] += 1
        elif s < 80:
            distribution['60-80'] += 1
        elif s < 90:
            distribution['80-90'] += 1
        else:
            distribution['90-100'] += 1

    # 最近一次考试
    latest = records[0].to_dict()

    return jsonify({
        'code': 200,
        'message': '查询成功',
        'data': {
            'total_exams': total_exams,
            'total_questions': total_questions,
            'total_correct': total_correct,
            'avg_score': round(sum(scores) / total_exams, 2),
            'max_score': max(scores),
            'min_score': min(scores),
            'total_accuracy': round(total_correct / total_questions * 100, 2) if total_questions > 0 else 0,
            'latest_exam': latest,
            'score_distribution': distribution
        }
    })


@score_display_bp.route('/comparison', methods=['GET'])
def get_score_comparison():
    """
    成绩对比接口
    
    请求参数:
        user_id   (int): 用户ID（必填）
        exam_ids  (str): 要对比的考试ID列表，逗号分隔，如 "1,2,3"
    
    返回:
        多场考试的详细对比数据
    """
    user_id = request.args.get('user_id', type=int)
    exam_ids_str = request.args.get('exam_ids', type=str)

    if not user_id:
        return jsonify({'code': 400, 'message': '缺少参数: user_id'}), 400

    # 如果指定了 exam_ids，则对比指定考试；否则对比最近3场
    if exam_ids_str:
        try:
            exam_ids = [int(x.strip()) for x in exam_ids_str.split(',')]
        except ValueError:
            return jsonify({'code': 400, 'message': 'exam_ids 格式错误，应为逗号分隔的数字'}), 400
    else:
        recent = ExamRecord.query \
            .filter_by(user_id=user_id) \
            .order_by(ExamRecord.exam_date.desc()) \
            .limit(3).all()
        exam_ids = [r.id for r in recent]

    exams = ExamRecord.query.filter(
        ExamRecord.id.in_(exam_ids),
        ExamRecord.user_id == user_id
    ).order_by(ExamRecord.exam_date.asc()).all()

    comparison = []
    for exam in exams:
        comparison.append(exam.to_dict())

    return jsonify({
        'code': 200,
        'message': '查询成功',
        'data': {
            'comparison': comparison,
            'count': len(comparison)
        }
    })