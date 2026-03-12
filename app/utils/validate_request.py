
from app.db.models import Task
from fastapi import HTTPException
from pydantic import BaseModel, HttpUrl, field_validator
from fastapi import FastAPI, HTTPException, status, Request
from app.config import DEV_MODE, ALLOWED_ORIGINS


class TaskCreateRequest(BaseModel):
    url: HttpUrl

    @field_validator('url')
    def validate_genially_url(cls, url):
        if not str(url).startswith("https://view.genially.com/"):
            raise ValueError("Invalid Genially URL")
        return url

def check_origin(request: Request):
    if DEV_MODE:
        return
    origin = request.headers.get("origin") or request.headers.get("referer")
    if origin is None or not any(origin.startswith(o) for o in ALLOWED_ORIGINS):
        raise HTTPException(403, "Forbidden")


def get_task_or_404(task_id: str) -> Task:
    task = Task.get_or_none(Task.task_id == task_id)
    if not task:
        raise HTTPException(404, "Task not found")
    return task
