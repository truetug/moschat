import logging

import dateparser
from app.schemas import Message
from app.services import BaseService
from app.services.exceptions import ServiceValidationError
from app.services.currencies.client import Client
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class CurrenciesService(BaseService):
    async def process(self, session: Session, *args):
        logging.debug("Service processing: %s %s", self.__class__.__name__, args)

        try:
            ticker_from, ticker_to, dt = args
            ticker_from, ticker_to = ticker_from.upper(), ticker_to.upper()
            dt = dateparser.parse(dt)
        except Exception as exc:
            raise ServiceValidationError(
                f"Неверные параметры: {exc} ({', '.join(args)})",
            )

        try:
            client = Client()
            response = await client.get_history(dt)
            logger.debug("Service response: %s %s", response.status_code, response.text)
        except Exception as exc:
            logger.exception("Something went wrong")
            raise ServiceValidationError(str(exc))

        if response.status_code != 200:
            raise ServiceValidationError(
                f"{response.status_code} `{response.text}`"
            )

        rates = response.json()["response"]["rates"]

        price_from = rates.get(ticker_from)
        price_to = rates.get(ticker_to)
        if not all((price_from, price_from)):
            raise ServiceValidationError(
                "Валюта указана неверно, доступные варианты: "
                f"{', '.join(rates.keys())}"
            )

        text = (
            f"{dt.strftime('%d.%m.%Y')} `1 {ticker_to}` можно было купить за "
            f"`{round(price_from / price_to, 2)} {ticker_from}`"
        )

        return Message(
            message=text,
        )
