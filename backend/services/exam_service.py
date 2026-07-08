import random
import re
from datetime import datetime

from flask import current_app

from models import AnswerRecord, ExamRecord, Word, db
from services.question_types import (
    CHOICE_TYPES,
    CN_TO_EN_TYPES,
    EN_TO_CN_TYPES,
    QUESTION_TYPES,
)


def normalize_answer(text: str) -> str:
    if not text:
        return ""
    text = text.strip().lower()
    text = re.sub(r"\s+", " ", text)
    return text


def is_meaning_correct(user_answer: str, correct_meaning: str) -> bool:
    user_norm = normalize_answer(user_answer)
    correct_norm = normalize_answer(correct_meaning)
    if not user_norm:
        return False
    if user_norm == correct_norm:
        return True
    parts = re.split(r"[;；,，/]", correct_meaning)
    for part in parts:
        if normalize_answer(part) == user_norm:
            return True
    return False


def is_word_correct(user_answer: str, correct_word: str) -> bool:
    return normalize_answer(user_answer) == normalize_answer(correct_word)


def is_question_correct(user_answer: str, word: Word, question_type: str) -> bool:
    if question_type in EN_TO_CN_TYPES:
        return is_meaning_correct(user_answer, word.meaning)
    if question_type in CN_TO_EN_TYPES:
        return is_word_correct(user_answer, word.word)
    return False


def get_correct_answer(word: Word, question_type: str) -> str:
    if question_type in EN_TO_CN_TYPES:
        return word.meaning
    return word.word


def get_prompt(word: Word, question_type: str) -> str:
    if question_type in EN_TO_CN_TYPES:
        return word.word
    return word.meaning


def build_choice_options(correct: str, pool: list[str], option_count: int = 4) -> list[str]:
    candidates = [item for item in pool if item != correct]
    if len(candidates) < option_count - 1:
        return [correct]
    distractors = random.sample(candidates, option_count - 1)
    options = distractors + [correct]
    random.shuffle(options)
    return options


def build_question(word: Word, question_type: str, all_words: list[Word]) -> dict:
    prompt = get_prompt(word, question_type)
    question = {
        "word_id": word.id,
        "question_type": question_type,
        "question_type_label": QUESTION_TYPES[question_type],
        "prompt": prompt,
        "phonetic": word.phonetic if question_type in EN_TO_CN_TYPES else None,
        "level": word.level,
        "options": None,
    }

    if question_type in CHOICE_TYPES:
        if question_type in EN_TO_CN_TYPES:
            pool = [item.meaning for item in all_words if item.id != word.id]
            question["options"] = build_choice_options(word.meaning, pool)
        else:
            pool = [item.word for item in all_words if item.id != word.id]
            question["options"] = build_choice_options(word.word, pool)

    return question


def grade_exam(exam: ExamRecord, answers: list[dict]) -> dict:
    word_ids = [item["word_id"] for item in answers]
    words = {w.id: w for w in Word.query.filter(Word.id.in_(word_ids)).all()}

    correct_count = 0
    answer_records = []

    for index, item in enumerate(answers):
        word_id = item["word_id"]
        user_answer = item.get("user_answer", "")
        question_type = item.get("question_type", "en_to_cn")
        word = words.get(word_id)
        if not word:
            continue

        correct = is_question_correct(user_answer, word, question_type)
        if correct:
            correct_count += 1

        answer_records.append(
            AnswerRecord(
                exam_id=exam.id,
                user_id=exam.user_id,
                word_id=word_id,
                user_answer=user_answer,
                question_type=question_type,
                is_correct=1 if correct else 0,
                question_order=index + 1,
            )
        )

    total = exam.total_questions
    score = round(correct_count / total * 100, 2) if total > 0 else 0

    for record in answer_records:
        db.session.add(record)

    exam.correct_count = correct_count
    exam.score = score
    exam.status = "submitted"
    exam.end_time = datetime.utcnow()

    answer_details = []
    for record in answer_records:
        word = words.get(record.word_id)
        question_type = record.question_type or "en_to_cn"
        answer_details.append(
            {
                "word_id": record.word_id,
                "word": word.word if word else None,
                "correct_meaning": word.meaning if word else None,
                "question_type": question_type,
                "question_type_label": QUESTION_TYPES.get(question_type, question_type),
                "prompt": get_prompt(word, question_type) if word else None,
                "correct_answer": get_correct_answer(word, question_type) if word else None,
                "user_answer": record.user_answer,
                "is_correct": bool(record.is_correct),
                "question_order": record.question_order,
            }
        )

    return {
        "correct_count": correct_count,
        "total_questions": total,
        "score": score,
        "start_time": exam.start_time.isoformat() if exam.start_time else None,
        "end_time": exam.end_time.isoformat() if exam.end_time else None,
        "duration_seconds": exam.duration_seconds(),
        "answers": answer_details,
    }


def generate_exam_questions(user_id: int, question_count: int | None = None) -> tuple[ExamRecord, list[dict]]:
    count = question_count or current_app.config["DEFAULT_EXAM_QUESTION_COUNT"]
    type_keys = list(QUESTION_TYPES.keys())
    total_words = Word.query.count()

    if total_words == 0:
        raise ValueError("单词库为空，请联系管理员导入单词数据")
    if total_words < 4:
        raise ValueError("单词库至少需要4个单词才能生成选择题")
    if total_words < count:
        raise ValueError(f"单词库至少需要{count}个单词才能生成{count}道题")
    if count % len(type_keys) != 0:
        raise ValueError(f"题目数量必须能被题型数量({len(type_keys)})整除")

    per_type = count // len(type_keys)
    all_words = Word.query.all()
    selected_words = random.sample(all_words, count)

    exam = ExamRecord(
        user_id=user_id,
        total_questions=count,
        status="in_progress",
    )
    db.session.add(exam)
    db.session.flush()

    questions = []
    for type_index, question_type in enumerate(type_keys):
        start = type_index * per_type
        type_words = selected_words[start : start + per_type]
        random.shuffle(type_words)
        for word in type_words:
            questions.append(build_question(word, question_type, all_words))

    return exam, questions
