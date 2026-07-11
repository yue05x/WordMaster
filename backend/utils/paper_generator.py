import random
from models import Word, db


def generate_paper(count=10):
    """
    生成一套试卷（题目列表）
    每个题目包含：单词、四个选项（释义）、正确选项索引
    """
    # 获取所有单词
    all_words = Word.query.all()
    if len(all_words) < count:
        raise ValueError(f"单词库数量不足，当前仅有 {len(all_words)} 个单词，无法生成 {count} 道题")

    # 随机选择 count 个单词作为题目
    selected = random.sample(all_words, count)
    questions = []

    # 为每个题目生成干扰项
    for word_obj in selected:
        # 正确释义
        correct_def = word_obj.definition

        # 从所有单词中随机选3个不同的释义作为干扰项（排除自身）
        other_defs = [w.definition for w in all_words if w.id != word_obj.id]
        # 若干扰项不足3个，用占位符填充（实际上单词库一般足够）
        if len(other_defs) < 3:
            distractors = other_defs + ['未知'] * (3 - len(other_defs))
        else:
            distractors = random.sample(other_defs, 3)

        # 组合成4个选项
        options = [correct_def] + distractors
        # 打乱选项顺序，并记录正确索引
        random.shuffle(options)
        correct_index = options.index(correct_def)

        questions.append({
            'id': word_obj.id,
            'word': word_obj.word,
            'options': options,
            'correct': correct_index  # 供后续判卷使用（不会返回给前端）
        })

    return questions