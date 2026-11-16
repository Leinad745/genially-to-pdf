from urllib.parse import urlparse

from fastapi import HTTPException, Request, status
from pydantic import BaseModel, HttpUrl, field_validator

from app.config import ALLOWED_ORIGINS, DEV_MODE
from app.db.models import Task


class TaskCreateRequest(BaseModel):
    url: HttpUrl

    @field_validator("url")
    def validate_genially_url(cls, url):
        if not str(url).startswith("https://view.genially.com/"):
            raise ValueError("Invalid Genially URL")
        return url


def check_origin(request: Request) -> None:
    if DEV_MODE:
        return
    origin = request.headers.get("origin") or request.headers.get("referer")
    if origin is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    # same-origin request: the frontend served by this backend. Comparing the
    # Origin/Referer host with the Host header works behind a reverse proxy that
    # forwards Host, without hard-coding the deployment domain.
    host = request.headers.get("host")
    if host and urlparse(origin).netloc == host:
        return
    # explicitly configured external origins (ALLOWED_ORIGINS env var)
    if any(origin.startswith(o) for o in ALLOWED_ORIGINS):
        return
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")


def get_task_or_404(task_id: str) -> Task:
    task = Task.get_or_none(Task.task_id == task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    return task
