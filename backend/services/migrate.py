from sqlalchemy import inspect, text

from models import db


def migrate_db():
    inspector = inspect(db.engine)
    if "answer_record" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("answer_record")}
    if "question_type" not in columns:
        with db.engine.begin() as connection:
            connection.execute(
                text("ALTER TABLE answer_record ADD COLUMN question_type VARCHAR(30) DEFAULT 'en_to_cn'")
            )
