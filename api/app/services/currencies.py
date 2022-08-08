from sqlalchemy.orm import Session

from . import BaseService


class CurrenciesService(BaseService):
    async def process(self, session: Session, *args):
        pass
