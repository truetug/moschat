import logging
from datetime import datetime

from app.schemas import Message
from app.settings.services import SERVICE_DB

from . import BaseService

logger = logging.getLogger(__name__)


class HelpService(BaseService):
    async def process(self, *args) -> Message:
        logger.debug("Service processing: %s %s", self.__class__.__name__, args)

        text = "\n".join([
            f"* **\\{k}** {v['description']}"
            for k, v in SERVICE_DB.items()
        ])

        text = (
            "Доступные команды\n\n"
            f"{text}"
        )

        return Message(
            type="message",
            sender="bot",
            message=text,
            datetime=datetime.utcnow(),
        )
