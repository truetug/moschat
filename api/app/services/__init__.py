from sqlalchemy.orm import Session

from app.schemas import Message


class BaseService:
    abstract = True

    async def process(self, session: Session, *args) -> Message:
        raise NotImplemented
