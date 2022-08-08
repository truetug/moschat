import logging

from app.schemas import Message
from sqlalchemy.orm import Session

from . import BaseService

logger = logging.getLogger(__name__)


class SimpleService(BaseService):
    async def process(self, session: Session, *args) -> Message:
        logger.debug("Service processing: %s %s", self.__class__.__name__, args)

        return Message(
            type="message",
            sender="bot",
            message=" ".join(args),
        )
