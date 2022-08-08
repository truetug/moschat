from app.schemas import Message
from sqlalchemy.orm import Session


class BaseService:
    abstract = True

    async def process(self, session: Session, *args) -> Message:
        raise NotImplemented
