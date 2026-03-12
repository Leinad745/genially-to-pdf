

from fastapi import APIRouter, Request, status
from fastapi.responses import RedirectResponse

from app.limiter import limiter
from app.utils.validate_request import check_origin


index_router = APIRouter()

@index_router.get("/", status_code=status.HTTP_303_SEE_OTHER)
@limiter.limit("15/minute")
def index(request: Request):
    check_origin(request)
    return RedirectResponse(url="/docs", status_code=303)