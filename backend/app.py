from flask import Flask
from flask_cors import CORS
from config import Config
from models import db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    CORS(app)  # 允许跨域

    # 注册蓝图
    from backend.routes.words import words_bp
    from backend.routes.paper import paper_bp
    app.register_blueprint(words_bp, url_prefix='/api')
    app.register_blueprint(paper_bp, url_prefix='/api')

    return app


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()  # 自动创建表（若未创建）
    app.run(debug=True, host='0.0.0.0', port=5000)