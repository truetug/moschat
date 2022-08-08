import logging

from app.api.messages import publish_task
from app.centrifugo import get_centrifugo, get_token
from app.db import get_session
from app.db.models import User
from app.db.services import get_history_items
from app.schemas import MeResponse, Message
from app.services.auth.helpers import get_current_active_user
from cent import Client
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette.background import BackgroundTasks
from starlette.requests import Request

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/")
async def home():
    return {}


@router.get("/me", response_model=MeResponse)
async def me(
    request: Request,
    background_tasks: BackgroundTasks,
    broker: Client = Depends(get_centrifugo),
    session: Session = Depends(get_session),
    user: User = Depends(get_current_active_user),
):
    history = get_history_items(session, user_id=user.id, limit=10)
    user_id = user.username

    channel = f"chats:{user.username}"
    msg = Message(message="Привет, для справки можешь вызвать помощь: `\help`")
    background_tasks.add_task(publish_task, broker, channel, msg, 1)

    return {
        "token": get_token(user_id),
        "userId": user_id,
        "history": history,
    }
