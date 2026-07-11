from flask import Flask, jsonify
from flask_cors import CORS

from config import Config
from models import db
from routes.exam import exam_bp
from routes.paper import paper_bp
from routes.user import user_bp
from routes.words import words_bp
from services.migrate import migrate_db
from services.seed import seed_sample_words


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    db.init_app(app)
    app.register_blueprint(user_bp)
    app.register_blueprint(words_bp, url_prefix="/api")
    app.register_blueprint(paper_bp, url_prefix="/api")
    app.register_blueprint(exam_bp)

    @app.route("/api/health")
    def health():
        return jsonify({"code": 200, "message": "WordMaster API is running"})

    with app.app_context():
        db.create_all()
        migrate_db()
        seed_sample_words()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
