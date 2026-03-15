import datetime
import os
import uuid

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import FileResponse

from app.db.models import Task
from app.limiter import limiter
from app.schemas.response_models import (ErrorResponse, StatsResponse,
                                         SuccessResponse, TaskStatusResponse)
from app.services.tasks.huey_manager import queue_task
from app.utils.task_status import TaskStatus
from app.utils.validate_request import (TaskCreateRequest, check_origin,
                                        get_task_or_404)

tasks_router = APIRouter()


@tasks_router.post("/create-task", status_code=status.HTTP_201_CREATED, response_model=TaskStatusResponse, responses={400: {"model": ErrorResponse}, 403: {"model": ErrorResponse}})
@limiter.limit("3/minute")
def create_task(
    request: Request,
    request_data: TaskCreateRequest,
):

    # check referer/origin from actual HTTP request
    check_origin(request)
    try:
        url = str(request_data.url)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))

    task_id = uuid.uuid4()
    task = Task.create(url=url, task_id=task_id)
    queue_task(task_id=str(task_id))
    return task.to_response()


@tasks_router.get("/tasks", status_code=status.HTTP_200_OK, response_model=StatsResponse, responses={403: {"model": ErrorResponse}})
@limiter.limit("10/minute")
def get_processed_tasks(request: Request):
    check_origin(request)
    total_tasks = Task.select().count()
    today_tasks = Task.select().where(Task.started_at >= datetime.datetime.now() -
                                      datetime.timedelta(days=1)).count()
    completed_tasks = Task.select().where(Task.status == TaskStatus.FINISHED).count()
    failed_tasks = Task.select().where(Task.status == TaskStatus.ERROR).count()

    return StatsResponse(
        total_tasks=total_tasks,
        today_tasks=today_tasks,
        completed_tasks=completed_tasks,
        failed_tasks=failed_tasks
    )


@tasks_router.get("/task/{task_id}", status_code=status.HTTP_200_OK, response_model=TaskStatusResponse, responses={403: {"model": ErrorResponse}, 404: {"model": ErrorResponse}})
@limiter.limit("30/minute")
def get_task_status(request: Request, task_id: str):
    check_origin(request)
    task = get_task_or_404(task_id)
    return task.to_response()


@tasks_router.delete("/task/{task_id}", status_code=status.HTTP_200_OK, response_model=SuccessResponse, responses={403: {"model": ErrorResponse}, 404: {"model": ErrorResponse}})
@limiter.limit("5/minute")
def delete_task(request: Request, task_id: str):
    check_origin(request)
    task = get_task_or_404(task_id)
    task.delete_instance()
    return SuccessResponse(detail="Task deleted successfully")


@tasks_router.get("/download/{task_id}", status_code=status.HTTP_200_OK, responses={403: {"model": ErrorResponse}, 404: {"model": ErrorResponse}})
@limiter.limit("5/minute")
def download_task(request: Request, task_id: str):
    check_origin(request)
    task = get_task_or_404(task_id)
    if task.status_enum != TaskStatus.FINISHED or not task.download_link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not finished yet")
    if os.path.exists(str(task.download_link)):
        return FileResponse(str(task.download_link), filename=f"genially_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.pdf", media_type='application/pdf')
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail="File not found")
