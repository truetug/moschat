from app.helpers import _custom_json_serializer
from app.settings.base import DATABASE_URL
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from starlette.requests import Request

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args.update({"check_same_thread": False})

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    json_serializer=_custom_json_serializer,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()

Base.metadata.create_all(bind=engine)


def get_session(request: Request):
    return request.state.db
