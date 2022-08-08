import json
import logging
import locale
import os

from app.helpers import import_class

logger = logging.getLogger(__name__)

DATABASE_URL = "sqlite:///./db.sqlite3"

centrifugo_config = json.load(open("/centrifugo/config.json"))
CENTRIFUGO_API_KEY = centrifugo_config["api_key"]
CENTRIFUGO_SECRET = centrifugo_config["token_hmac_secret_key"]
CENTRIFUGO_API_URL = os.getenv("CENTRIFUGO_API_URL", "http://centrifugo:8000/api")

SECRET_KEY = os.getenv("SECRET_KEY", "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

PREPARE_PIPELINE = [
    "app.pipeline.lower.LowerCaseHandler",
    "app.pipeline.tokenize.WhiteSpaceHandler",
    "app.pipeline.stem.SnowballHandler",
    "app.pipeline.stopwords.RussianStopWordsHandler",
]

PIPELINE = []
for handler in PREPARE_PIPELINE:
    cls = import_class(handler)
    PIPELINE.append(cls)

logger.info("Pipeline initialized: %s", PIPELINE)
