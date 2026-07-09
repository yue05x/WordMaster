"""
历史成绩查询模块
提供历史成绩查询、考试详情、错题统计、成绩总览等功能
"""

from .models import db, ExamRecord, AnswerRecord
from .routes import history_scores_bp


def init_app(app):
    """
    初始化 history_scores 模块到 Flask 应用
    
    调用方式（在 app.py 中）:
        from history_scores import init_app
        init_app(app)
    
    参数:
        app: Flask 应用实例
    """
    # 初始化数据库
    db.init_app(app)

    # 注册蓝图
    app.register_blueprint(history_scores_bp)

    # 创建数据库表（如果不存在）
    with app.app_context():
        db.create_all()