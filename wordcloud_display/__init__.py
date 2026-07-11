"""
WordCloud 字符云展示模块
提供错题词云、词汇词云、词云配置建议、词云搜索等功能
"""

from .models import db, ExamRecord, AnswerRecord
from .routes import wordcloud_bp


def init_app(app):
    """
    初始化 wordcloud_display 模块到 Flask 应用
    
    调用方式（在 app.py 中）:
        from wordcloud_display import init_app
        init_app(app)
    
    参数:
        app: Flask 应用实例
    """
    db.init_app(app)
    app.register_blueprint(wordcloud_bp)

    with app.app_context():
        db.create_all()