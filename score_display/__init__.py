"""
成绩展示模块
提供考试详情展示、成绩趋势、成绩总览、成绩对比等功能
"""

from .models import db, ExamRecord, AnswerRecord
from .routes import score_display_bp


def init_app(app):
    """
    初始化 score_display 模块到 Flask 应用
    
    调用方式（在 app.py 中）:
        from score_display import init_app
        init_app(app)
    
    参数:
        app: Flask 应用实例
    """
    db.init_app(app)
    app.register_blueprint(score_display_bp)

    with app.app_context():
        db.create_all()