from huey import SqliteHuey
from huey import crontab

from .runner import run_task
from .cleanup import cleanup_files
from app.config import HUEY_DB_PATH

huey = SqliteHuey(filename=HUEY_DB_PATH)


@huey.task(retries=2)
def queue_task(task_id: str) -> None:
    run_task(task_id)


@huey.periodic_task(crontab(minute="*/1"))
def periodic_cleanup() -> None:
    cleanup_files()
