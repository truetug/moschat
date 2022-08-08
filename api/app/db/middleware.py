from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp, Scope, Receive, Send

from . import SessionLocal


class DBMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = Response(
            "Internal server error",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

        try:
            request.state.db = SessionLocal()
        finally:
            request.state.db.close()

        response = await call_next(request)
        return response

