from flask import Blueprint, request, jsonify
from backend.utils.paper_generator import generate_paper

paper_bp = Blueprint('paper', __name__)


@paper_bp.route('/paper', methods=['POST'])
def get_paper():
    data = request.get_json()
    count = data.get('count', 10)
    if not isinstance(count, int) or count <= 0:
        return jsonify({'error': 'count 必须为正整数'}), 400

    try:
        questions = generate_paper(count)
        # 生成一个临时的试卷ID（实际项目可存入数据库，这里简化）
        import uuid
        paper_id = str(uuid.uuid4())
        return jsonify({
            'paper_id': paper_id,
            'questions': questions
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 400