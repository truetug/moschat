import asyncio
import json
import logging
from typing import Optional

from app.centrifugo import get_centrifugo
from app.db import get_session
from app.db.models import User
from app.db.services import create_history_item
from app.helpers import import_class
from app.schemas import HistoryItemCreate, Message
from app.services.auth.helpers import get_current_active_user
from app.services.exceptions import ServiceValidationError
from app.settings.base import PIPELINE
from cent import Client
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette import status
from starlette.background import BackgroundTasks
from starlette.requests import Request
from starlette.responses import Response

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
    logging.debug("Command handling: %s %s", cmd_name, args)

    from app.settings.services import SERVICE_DB
    cmd = SERVICE_DB.get(cmd_name[1:])
    if not cmd:
        result = Message(
            message=(
                f"Извините, но команда `{cmd_name}` "
                f"пока не поддерживается"
            ),
        )
    elif not cmd.get("enabled", False):
        result = Message(
            message=(
                f"Извините, но команда `{cmd_name}` "
                f"временно отключена"
            ),
        )
    elif cmd.get("perms") and cmd.get("perms") not in user.perms:
        result = Message(
            message=(
                f"Извините, но для выполнения команды `{cmd_name}` "
                f"у вас не достаточно прав доступа"
            ),
        )
    else:
        cls = import_class(cmd["cls"])
        try:
            result = await cls().process(session, *args)
        except ServiceValidationError as exc:
            result = Message(message=f"Ошибка: {str(exc)}")
        except Exception as exc:
            result = Message(message=f"Ошибка сервера: {str(exc)}")

    logging.debug("Command result: %s", result)
    return result


async def publish_task(
    broker: Client,
    channel: str,
    msg: Message,
    delay: int = 0,
):
    body = json.loads(msg.json())
    logging.debug("Message ready: %s %s", channel, body)

    if delay:
        await asyncio.sleep(delay)

    try:
        has_presence = broker.presence(channel)
    except Exception:
        has_presence = True

    if has_presence:
        broker.publish(channel, body)
        logger.debug(f"Message sent: %s %s", channel, msg)
