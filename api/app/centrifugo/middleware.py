from app.settings.base import CENTRIFUGO_API_KEY, CENTRIFUGO_API_URL
from cent import Client
from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class CentrifugoMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            request.state.centrifugo = Client(
                address=CENTRIFUGO_API_URL,
                api_key=CENTRIFUGO_API_KEY,
                timeout=3,
            )
        finally:
            pass

        response = await call_next(request)
        return response
