import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.centrifugo.middleware import CentrifugoMiddleware
from app.db.middleware import DBMiddleware
from app.api.base import router as base_router
from app.api.messages import router as messages_router


logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(DBMiddleware)
app.add_middleware(CentrifugoMiddleware)

app.include_router(base_router)
app.include_router(messages_router)
