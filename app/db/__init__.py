import peewee
from app.config import DB_PATH

db = peewee.SqliteDatabase(DB_PATH)


def init_db() -> None:
    db.connect(reuse_if_open=True)
    from app.db.models import Task

    db.create_tables([Task])


def close_db() -> None:
    if not db.is_closed():
        db.close()
