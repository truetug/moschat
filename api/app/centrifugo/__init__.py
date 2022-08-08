import time

from app.settings.base import CENTRIFUGO_SECRET
from jose import jwt
from starlette.requests import Request


def get_centrifugo(request: Request):
    return request.state.centrifugo


def get_token(user_id: int):
    claims = {
        "sub": user_id,
        "exp": int(time.time()) + 24 * 3600,
    }
    token = jwt.encode(claims, CENTRIFUGO_SECRET, algorithm="HS256")
    return token
