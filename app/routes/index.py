import os

from fastapi import APIRouter
from fastapi.responses import FileResponse, HTMLResponse

from app.config import STATIC_DIR

index_router = APIRouter()


@index_router.get("/", include_in_schema=False)
def index():
    """Serve the web frontend. Public so the browser can load the page;
    the API routes it calls are still protected by check_origin."""
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file, media_type="text/html")
    return HTMLResponse(
        "<h1>Frontend not found</h1><p>See <a href='/docs'>/docs</a>.</p>",
        status_code=404,
    )
