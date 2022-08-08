from datetime import datetime

from . import BaseService
from app.schemas import Message
from app.settings.services import SERVICE_DB


class HelpService(BaseService):
    async def process(self, *args) -> Message:
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
