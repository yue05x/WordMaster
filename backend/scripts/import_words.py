import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app import create_app
from models import db, Word

app = create_app()
with app.app_context():
    # 清空旧数据（可选）
    # db.session.query(Word).delete()

    with open('../data/words.json', 'r', encoding='utf-8') as f:
        words_data = json.load(f)

    count = 0
    for item in words_data:
        word = item['word']
        definition = item['definition']
        # 避免重复插入
        if not Word.query.filter_by(word=word).first():
            new_word = Word(word=word, definition=definition)
            db.session.add(new_word)
            count += 1
    db.session.commit()
    print(f"成功导入 {count} 个单词")