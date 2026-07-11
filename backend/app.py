from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from models import db
from routes.exam import exam_bp
from routes.statistics import statistics_bp
from routes.user import user_bp
from routes.words import words_bp
from services.seed import regrade_existing_answers, seed_sample_words

def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    db.init_app(app)
    app.register_blueprint(user_bp)
    app.register_blueprint(words_bp)
    app.register_blueprint(exam_bp)
    app.register_blueprint(statistics_bp)

    @app.get("/api/health")
    def health():
        return jsonify({"code": 200, "message": "WordMaster API is running"})

    with app.app_context():
        db.create_all()
        seed_sample_words()
        regrade_existing_answers()
    return app

if __name__ == "__main__":
    create_app().run(host="0.0.0.0", port=5000, debug=True)
