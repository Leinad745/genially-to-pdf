from fastapi import FastAPI
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.extension import _rate_limit_exceeded_handler

# shared limiter instance; importing this module anywhere gives access
limiter = Limiter(key_func=get_remote_address)


def init_limiter(app: FastAPI) -> None:
    """Attach limiter and handlers to the FastAPI app."""
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore
