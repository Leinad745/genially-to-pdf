import os
from app.db.models import Task
from app.utils.task_status import TaskStatus
from app.config import PRESENTATION_DIRECTORY
from PyPDF2 import PdfMerger


def convert_to_pdf(task_id: str, slides_directory: str) -> None:
    task = None
    if task_id:
        try:
            task = Task.get_or_none(Task.task_id == task_id)
        except:
            pass
    if task is None:
        return

    task.update_status(
        status=TaskStatus.CONVERTING_TO_PDF,
        current_step="Converting to PDF from screenshots",
    )

    slides_pdf = []
    for filename in sorted(os.listdir(slides_directory), key=lambda x: int(x[:-4])):
        if not filename.endswith(".pdf"):
            continue
        slides_pdf.append(os.path.join(slides_directory, filename))
    if not slides_pdf:
        task.update_status(
            status=TaskStatus.ERROR,
            error_message="No screenshots found in the slides directory",
        )
        return

    merger = PdfMerger()

    output_path = f"{PRESENTATION_DIRECTORY}/presentation_{task_id}.pdf"

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    for slide in slides_pdf:
        merger.append(slide)

    merger.write(output_path)

    task.update_status(
        TaskStatus.FINISHED,
        current_step="PDF ready to download",
        download_link=output_path,
    )
