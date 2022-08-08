import logging

import dateparser
from sqlalchemy.orm import Session

from app.services import BaseService
from app.schemas import Message
from app.services.exceptions import ServiceValidationError
from app.services.weather.client import Client


logger = logging.getLogger(__name__)


class WeatherService(BaseService):
    name = "weather"

    async def process(self, session: Session, *args):
        try:
            city, dt = args
            dt = dateparser.parse(dt)
        except Exception as exc:
            raise ServiceValidationError(f"Неверные параметры: {exc} ({', '.join(args)})")

        try:
            client = Client()
            response = await client.get_history(city, dt)
            print("SERVICE", response)
        except Exception as exc:
            print("EXCEPTION", exc)
            logger.exception("Something went wrong")
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
