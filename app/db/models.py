from typing import Optional

from peewee import *
from datetime import datetime
from app.db import db
from app.utils.task_status import TaskStatus


class BaseModel(Model):
    class Meta:
        database = db


class Task(BaseModel):
    task_id = UUIDField(primary_key=True)
    url = CharField()
    percentage = IntegerField(default=0)
    status = CharField(default=TaskStatus.QUEUED)
    current_step = CharField(null=True, default="Waiting in queue")
    started_at = DateTimeField(default=datetime.now)
    finished_at = DateTimeField(null=True)
    error_message = TextField(null=True)
    download_link = CharField(null=True)

    @property
    def status_enum(self) -> TaskStatus:
        return TaskStatus(self.status)

    def to_dict(self) -> dict:
        return {
            "task_id": str(self.task_id),
            "url": self.url,
            "queue_position": self.queue_position(),
            "percentage": self.percentage,
            "status": self.status_enum.value,
            "current_step": self.current_step,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "error_message": self.error_message,
            "download_link": self.download_link
        }
    

    def update_status(self, status: Optional[TaskStatus], progress: Optional[int] = None, current_step: Optional[str] = None, error_message: Optional[str] = None, download_link: Optional[str] = None) -> None:
        if status is not None:
            self.status = status
        if progress is not None:
            self.percentage = progress
        if current_step is not None:
            self.current_step = current_step
        if error_message is not None:
            self.error_message = error_message
        if status == TaskStatus.FINISHED:
            self.finished_at = datetime.now()
            self.percentage = 100
        if status == TaskStatus.ERROR:
            self.current_step = "Task failed"
            self.finished_at = datetime.now()
        if download_link is not None:
            self.download_link = download_link

        self.save()

    def queue_position(self) -> int | None:
        if self.status != TaskStatus.QUEUED:
            return None
        return (
            Task
            .select()
            .where(
                Task.status == TaskStatus.QUEUED,
                Task.started_at < self.started_at,
            )
            .count()
            + 1
        )
