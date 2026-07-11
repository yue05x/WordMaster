SAMPLE_WORDS = [
    ("apple", "苹果"), ("banana", "香蕉"), ("orange", "橙子"), ("grape", "葡萄"),
    ("water", "水"), ("teacher", "教师"), ("student", "学生"), ("school", "学校"),
    ("ability", "能力"), ("accept", "接受"), ("access", "访问"), ("achieve", "实现"),
    ("accurate", "准确的"), ("abstract", "抽象的"), ("academic", "学术的"),
    ("account", "账户"), ("adapt", "适应"), ("admire", "钦佩"), ("admit", "承认"),
    ("complete", "完成"),
]

def seed_sample_words():
    from models import Word, db
    if Word.query.count():
        return
    for word, meaning in SAMPLE_WORDS:
        db.session.add(Word(word=word, meaning=meaning, level="CET4"))
    db.session.commit()
