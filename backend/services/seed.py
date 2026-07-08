SAMPLE_WORDS = [
    ("abandon", "放弃；遗弃", "/əˈbændən/", "CET4"),
    ("ability", "能力；才能", "/əˈbɪləti/", "CET4"),
    ("absolute", "绝对的；完全的", "/ˈæbsəluːt/", "CET4"),
    ("abstract", "抽象的；摘要", "/ˈæbstrækt/", "CET4"),
    ("academic", "学术的；学院的", "/ˌækəˈdemɪk/", "CET4"),
    ("accept", "接受；承认", "/əkˈsept/", "CET4"),
    ("access", "通道；访问", "/ˈækses/", "CET4"),
    ("accident", "事故；意外", "/ˈæksɪdənt/", "CET4"),
    ("accompany", "陪伴；伴随", "/əˈkʌmpəni/", "CET4"),
    ("accomplish", "完成；实现", "/əˈkɑːmplɪʃ/", "CET4"),
    ("account", "账户；说明", "/əˈkaʊnt/", "CET4"),
    ("accurate", "准确的；精确的", "/ˈækjərət/", "CET4"),
    ("achieve", "实现；达到", "/əˈtʃiːv/", "CET4"),
    ("acquire", "获得；取得", "/əˈkwaɪər/", "CET4"),
    ("adapt", "适应；改编", "/əˈdæpt/", "CET4"),
    ("adequate", "足够的；适当的", "/ˈædɪkwət/", "CET4"),
    ("adjust", "调整；适应", "/əˈdʒʌst/", "CET4"),
    ("administration", "管理；行政", "/ədˌmɪnɪˈstreɪʃn/", "CET6"),
    ("admire", "钦佩；欣赏", "/ədˈmaɪər/", "CET4"),
    ("admit", "承认；准许进入", "/ədˈmɪt/", "CET4"),
]


def seed_sample_words():
    from models import Word, db

    if Word.query.count() > 0:
        return

    for word, meaning, phonetic, level in SAMPLE_WORDS:
        db.session.add(Word(word=word, meaning=meaning, phonetic=phonetic, level=level))
    db.session.commit()
