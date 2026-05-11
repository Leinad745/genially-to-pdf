from app.config import SLIDES_DIRECTORY
from app.db.models import Task
from app.services.pdf import convert_to_pdf
from app.services.scraper import capture_slides
from app.utils.directory import remove_directory_recursively
from app.utils.task_status import TaskStatus


def run_task(task_id: str) -> None:
    task = Task.get_or_none(Task.task_id == task_id)
    if task is None:
        return
    task.update_status(
        status=TaskStatus.CAPTURING_SLIDES,
        current_step="Starting environment & browser",
        progress=10,
    )
    slides_directory = f"{SLIDES_DIRECTORY}/{task_id}"
    try:
        remove_directory_recursively(slides_directory)
        capture_slides(task_id, task.url, slides_directory)
        convert_to_pdf(task_id, slides_directory)
    except Exception as error:
        task.update_status(
            status=TaskStatus.ERROR,
            current_step="Task failed",
            error_message=str(error),
        )
    finally:
        remove_directory_recursively(slides_directory)
