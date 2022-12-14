import logging

import httpx
from app.settings.services import WEATHER_API_KEY
from pydantic.schema import datetime

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
        response = await self.client.get(
            url=f"https://{self.host}/history.json",
            params = {"q": city, "dt": dt.strftime("%Y-%m-%d")},
        )

        return response
