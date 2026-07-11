"""
错题统计模块
提供错题列表、错题汇总、WordCloud数据、错题分布、最近错题等功能
"""

from .models import db, ExamRecord, AnswerRecord
from .routes import wrong_stats_bp


def init_app(app):
    """
    初始化 wrong_question_stats 模块到 Flask 应用
    
    调用方式（在 app.py 中）:
        from wrong_question_stats import init_app
        init_app(app)
    
    参数:
        app: Flask 应用实例
    """
    db.init_app(app)
    app.register_blueprint(wrong_stats_bp)

    with app.app_context():
        db.create_all()