import logging

import dateparser
from app.schemas import Message
from app.services import BaseService
from app.services.exceptions import ServiceValidationError
from app.services.weather.client import Client
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class WeatherService(BaseService):
    async def process(self, session: Session, *args):
        logger.debug("Service processing: %s %s", self.__class__.__name__, args)

        try:
            city, dt = args
            dt = dateparser.parse(dt)
        except Exception as exc:
            raise ServiceValidationError(
                f"Неверные параметры: {exc} ({', '.join(args)})",
            )

        try:
            client = Client()
            response = await client.get_history(city, dt)
            logger.debug("Service response: %s %s", response.status_code, response.text)
        except Exception as exc:
            logger.exception("Something went wrong: %s", exc)
            raise ServiceValidationError(str(exc))

        if response.status_code != 200:
            raise ServiceValidationError(
                f"{response.status_code} `{response.text}`"
            )

        text = "\n".join([
            f"* **{k}**: {v}" if k != "condition" else f"<img src=\"{v['icon']}\"/>"
            for k, v in response.json()["forecast"]["forecastday"][0]["day"].items()
        ])

        return Message(
            message=text,
        )
