from sqlalchemy.orm import Session

from . import BaseService
from ..schemas import Message


class SimpleService(BaseService):
    async def process(self, session: Session, *args) -> Message:
        return Message(
            type="message",
            sender="bot",
            message=" ".join(args),
        )
