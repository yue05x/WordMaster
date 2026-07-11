"""
WordCloud 字符云展示模块 - API 路由
提供错题词云、全部词汇词云、词云配置等接口
"""

from flask import Blueprint, request, jsonify
from sqlalchemy import func
from .models import db, ExamRecord, AnswerRecord

wordcloud_bp = Blueprint('wordcloud', __name__, url_prefix='/api/wordcloud')


@wordcloud_bp.route('/wrong', methods=['GET'])
def get_wrong_wordcloud():
    """
    错题词云数据接口（核心功能）
    
    根据用户错题情况生成 WordCloud 数据，错误越多的单词权重越大，字体越大。
    数据格式直接兼容 WordCloud2.js
    
    请求参数:
        user_id  (int): 用户ID（必填）
        top_n    (int): 返回词数上限，默认50
        min_weight(int): 最小权重过滤，只返回错误次数 >= min_weight 的词，默认1
    
    返回格式:
        [['word', weight], ['word', weight], ...]
        示例: [['apple', 5], ['banana', 3], ['cherry', 2]]
    """
    user_id = request.args.get('user_id', type=int)
    if not user_id:
        return jsonify({'code': 400, 'message': '缺少参数: user_id'}), 400

    top_n = request.args.get('top_n', 50, type=int)
    min_weight = request.args.get('min_weight', 1, type=int)

    exam_ids = db.session.query(ExamRecord.id).filter_by(user_id=user_id).subquery()

    results = db.session.query(
        AnswerRecord.word_text,
        func.count(AnswerRecord.id).label('weight')
    ).filter(
        AnswerRecord.exam_id.in_(exam_ids),
        AnswerRecord.is_correct == False
    ).group_by(
        AnswerRecord.word_text
    ).having(
        func.count(AnswerRecord.id) >= min_weight
    ).order_by(
        func.count(AnswerRecord.id).desc()
    ).limit(top_n).all()

    wordcloud_data = [[row.word_text, row.weight] for row in results]

    if not wordcloud_data:
        return jsonify({
            'code': 200,
            'message': '暂无错题数据',
            'data': {
                'wordcloud': [],
                'total_words': 0,
                'wordcloud_ready': False
            }
        })

    # 计算权重范围，供前端调色使用
    weights = [w[1] for w in wordcloud_data]
    weight_range = {'min': min(weights), 'max': max(weights)}

    return jsonify({
        'code': 200,
        'message': '查询成功',
        'data': {
            'wordcloud': wordcloud_data,
            'total_words': len(wordcloud_data),
            'weight_range': weight_range,
            'wordcloud_ready': True
        }
    })


@wordcloud_bp.route('/vocabulary', methods=['GET'])
def get_vocabulary_wordcloud():
    """
    全部已考词汇词云数据接口
    
    展示用户所有接触过的单词，权重 = 出现总次数（含正确和错误），
    出现越频繁的单词字体越大。
    
    请求参数:
        user_id  (int): 用户ID（必填）
        top_n    (int): 返回词数上限，默认50
        only_wrong(bool): 是否仅展示错题，默认 false
    
    返回格式:
        [['word', weight], ['word', weight], ...]
    """
    user_id = request.args.get('user_id', type=int)
    if not user_id:
        return jsonify({'code': 400, 'message': '缺少参数: user_id'}), 400

    top_n = request.args.get('top_n', 50, type=int)
    only_wrong = request.args.get('only_wrong', 'false').lower() == 'true'

    exam_ids = db.session.query(ExamRecord.id).filter_by(user_id=user_id).subquery()

    query = db.session.query(
        AnswerRecord.word_text,
        func.count(AnswerRecord.id).label('weight')
    ).filter(
        AnswerRecord.exam_id.in_(exam_ids)
    )

    if only_wrong:
        query = query.filter(AnswerRecord.is_correct == False)

    results = query.group_by(
        AnswerRecord.word_text
    ).order_by(
        func.count(AnswerRecord.id).desc()
    ).limit(top_n).all()

    wordcloud_data = [[row.word_text, row.weight] for row in results]

    if not wordcloud_data:
        return jsonify({
            'code': 200,
            'message': '暂无词汇数据',
            'data': {
                'wordcloud': [],
                'total_words': 0,
                'wordcloud_ready': False
            }
        })

    weights = [w[1] for w in wordcloud_data]
    weight_range = {'min': min(weights), 'max': max(weights)}

    return jsonify({
        'code': 200,
        'message': '查询成功',
        'data': {
            'wordcloud': wordcloud_data,
            'total_words': len(wordcloud_data),
            'weight_range': weight_range,
            'wordcloud_ready': True
        }
    })


@wordcloud_bp.route('/config', methods=['GET'])
def get_wordcloud_config():
    """
    词云配置建议接口
    
    返回建议的 WordCloud2.js 配置参数，前端可直接使用或在此基础上调整。
    
    请求参数:
        user_id (int): 用户ID（必填）
    
    返回:
        建议的颜色方案、字体大小范围、旋转角度等配置
    """
    user_id = request.args.get('user_id', type=int)
    if not user_id:
        return jsonify({'code': 400, 'message': '缺少参数: user_id'}), 400

    # 统计总错题数和错题种类数，据此给出配置建议
    exam_ids = db.session.query(ExamRecord.id).filter_by(user_id=user_id).subquery()
    total_wrong = db.session.query(func.count(AnswerRecord.id)).filter(
        AnswerRecord.exam_id.in_(exam_ids),
        AnswerRecord.is_correct == False
    ).scalar() or 0

    wrong_types = db.session.query(
        AnswerRecord.word_text
    ).filter(
        AnswerRecord.exam_id.in_(exam_ids),
        AnswerRecord.is_correct == False
    ).group_by(AnswerRecord.word_text).count()

    config = {
        # WordCloud2.js 基本配置建议
        'suggested_config': {
            'gridSize': 12,                          # 词间距
            'sizeRange': [14, 60],                   # 字号范围 [最小, 最大]
            'rotationRange': [-45, 45],              # 旋转角度范围
            'shape': 'circle',                       # 形状: circle / cardioid / diamond / triangle / pentagon / star
            'backgroundColor': '#ffffff',            # 背景色
            'color': 'random-dark',                  # 配色方案: random-dark / random-light / 自定义颜色数组
            'weightFactor': 2,                       # 权重倍数
            'shuffle': False,                        # 是否打乱
            'minSize': 14,                           # 最小字号
            'drawOutOfBound': False,                 # 是否允许超出边界
            'ellipticity': 0.65,                     # 椭圆度
        },
        'suggested_colors': [                        # 建议配色（根据错题数量）
            '#e74c3c', '#e67e22', '#f1c40f', '#2ecc71',
            '#3498db', '#9b59b6', '#1abc9c', '#34495e',
            '#e91e63', '#00bcd4', '#ff5722', '#795548'
        ],
        'data_summary': {
            'total_wrong_answers': total_wrong,
            'wrong_word_types': wrong_types,
            'has_enough_data': total_wrong >= 5       # 错题 >= 5 个才有较好的词云效果
        }
    }

    return jsonify({
        'code': 200,
        'message': '查询成功',
        'data': config
    })


@wordcloud_bp.route('/search', methods=['GET'])
def search_wordcloud_word():
    """
    词云单词搜索接口
    
    支持在词云中搜索特定单词的详细信息
    
    请求参数:
        user_id   (int): 用户ID（必填）
        keyword   (str): 搜索关键词（支持模糊匹配）
    
    返回:
        匹配的单词及其错误详情
    """
    user_id = request.args.get('user_id', type=int)
    keyword = request.args.get('keyword', type=str)

    if not user_id:
        return jsonify({'code': 400, 'message': '缺少参数: user_id'}), 400
    if not keyword:
        return jsonify({'code': 400, 'message': '缺少参数: keyword'}), 400

    exam_ids = db.session.query(ExamRecord.id).filter_by(user_id=user_id).subquery()

    # 模糊搜索错题单词
    results = db.session.query(
        AnswerRecord.word_text,
        AnswerRecord.correct_answer,
        func.count(AnswerRecord.id).label('wrong_count'),
        func.group_concat(AnswerRecord.user_answer.distinct()).label('wrong_answers')
    ).filter(
        AnswerRecord.exam_id.in_(exam_ids),
        AnswerRecord.is_correct == False,
        AnswerRecord.word_text.like(f'%{keyword}%')
    ).group_by(
        AnswerRecord.word_text,
        AnswerRecord.correct_answer
    ).order_by(
        func.count(AnswerRecord.id).desc()
    ).all()

    search_results = []
    for row in results:
        wrong_answers_list = row.wrong_answers.split(',') if row.wrong_answers else []
        search_results.append({
            'word': row.word_text,
            'correct_answer': row.correct_answer,
            'wrong_count': row.wrong_count,
            'common_wrong_answers': list(set(wrong_answers_list))
        })

    return jsonify({
        'code': 200,
        'message': '查询成功',
        'data': {
            'keyword': keyword,
            'results': search_results,
            'total': len(search_results)
        }
    })