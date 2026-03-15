from pydantic import BaseModel


class TaskStatusResponse(BaseModel):
    task_id: str
    url: str
    queue_position: int | None
    percentage: int
    status: str
    current_step: str
    started_at: str
    finished_at: str | None
    error_message: str | None
    download_link: str | None


class StatsResponse(BaseModel):
    total_tasks: int
    today_tasks: int
    completed_tasks: int
    failed_tasks: int


class SuccessResponse(BaseModel):
    detail: str


class ErrorResponse(BaseModel):
    detail: str
