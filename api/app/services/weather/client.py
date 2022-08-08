import logging

import httpx
from pydantic.schema import datetime

from app.services.exceptions import ServiceValidationError
from app.settings.services import WEATHER_API_KEY

logger = logging.getLogger(__name__)


class Client:
    host = "weatherapi-com.p.rapidapi.com"

    def __init__(self):
        headers = {
            "X-RapidAPI-Key": WEATHER_API_KEY,
            "X-RapidAPI-Host": self.host,
        }

        self.client = httpx.AsyncClient(
            headers=headers,
        )

    async def get_history(self, city: str, dt: datetime):
        print("REQUEST", city, dt.strftime("%Y-%m-%d"))
        response = await self.client.get(
            url="https://weatherapi-com.p.rapidapi.com/history.json",
            params = {"q": city, "dt": dt.strftime("%Y-%m-%d")},
        )

        print("RESPONSE", response.status_code, response.content)
        return response
