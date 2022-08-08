import asyncio
import json
import logging
from random import randint
from typing import Optional

from cent import Client
from fastapi import Depends, APIRouter
from markdown import markdown
from sqlalchemy.orm import Session
from starlette import status
from starlette.background import BackgroundTasks
from starlette.requests import Request
from starlette.responses import Response

from app.centrifugo import get_centrifugo
from app.db import get_session
from app.db.models import User
from app.db.services import create_history_item
from app.helpers import import_class
from app.schemas import Message, HistoryItemCreate
from app.services.auth.helpers import get_current_active_user
from app.services.exceptions import ServiceValidationError
from app.settings.base import PIPELINE


logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/messages")
async def post_message(
    request: Request,
    background_tasks: BackgroundTasks,
    broker: Client = Depends(get_centrifugo),
    user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    data = await request.json()
    value = data.get("text", "")

    channel = f"chats:{user.username}"
    msg = Message(sender="user", message=value)
    obj = HistoryItemCreate(user_id="1", message=msg)
    create_history_item(request.state.db, obj)
    background_tasks.add_task(publish_task, broker, channel, msg)

    query = prepare(value)
    if not query:
        return Response(status_code=status.HTTP_400_BAD_REQUEST)
    elif query[0].startswith("\\"):
        # command
        msg = await handle_command(session, user, *query)
    else:
        # text intent
        msg = Message(sender="bot", message="И не говорите... 🙄")

    if user.id:
        obj = HistoryItemCreate(user_id=user.id, message=msg)

    create_history_item(request.state.db, obj)
    background_tasks.add_task(publish_task, broker, channel, msg, 0)
    return {"info": "message sent"}


def prepare(value):
    for cls in PIPELINE:
        value = cls().process(value)

    return value


async def handle_command(session: Session, user: User, cmd_name: str, *args) -> Optional[Message]:
    from app.settings.services import SERVICE_DB
    print("HANDLE", cmd_name, args)

    cmd = SERVICE_DB.get(cmd_name[1:])
    if not cmd or not cmd.get("enabled", False):
        result = Message(
            message=f"Извините, но команда `{cmd_name}` пока не поддерживается",
        )
    elif cmd.get("perms") and cmd.get("perms") not in user.perms:
        result = Message(
            message=f"У вас нет доступа для выполнения команды `{cmd_name}`",
        )
    else:
        cls = import_class(cmd["cls"])
        try:
            result = await cls().process(session, *args)
        except ServiceValidationError as exc:
            result = Message(message=f"Ошибка: {str(exc)}")
        except Exception as exc:
            result = Message(message=f"Ошибка сервера: {str(exc)}")

    print("RESULT", result)
    return result


async def publish_task(
    broker: Client,
    channel: str,
    msg: Message,
    delay: int = 0,
):
    msg.message = markdown(msg.message)
    body = json.loads(msg.json())
    print("MSG", channel, body)

    if delay:
        await asyncio.sleep(delay)

    try:
        has_presence = broker.presence(channel)
    except Exception:
        has_presence = True

    if has_presence:
        broker.publish(channel, body)
        logger.info(f"Message sent: %s", msg)
