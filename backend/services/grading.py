import re


def normalize_answer(value):
    return re.sub(r"\s+", " ", (value or "").strip().lower())


def accepted_meanings(meaning):
    return {
        normalize_answer(item)
        for item in re.split(r"[;；,，/、]", meaning or "")
        if normalize_answer(item)
    }


def is_meaning_correct(user_answer, meaning):
    return normalize_answer(user_answer) in accepted_meanings(meaning)
