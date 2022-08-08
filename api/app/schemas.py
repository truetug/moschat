from typing import List, Union, Any, Dict, Optional

import orjson
from markdown import markdown
from pydantic import BaseModel, Field, validator
from pydantic.schema import datetime


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Union[str, None] = None


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    email: str
    is_active: bool

    class Config:
        orm_mode = True

    @property
    def username(self):
        return self.email

    @property
    def perms(self):
        if self.id != -1:
            return ["can_use_weather"]


class Message(BaseModel):
    type: str = Field(default="message")
    sender: str = Field(default="bot")
    message: str
    data: Optional[Union[str, Dict[str, Any]]]
    created_at: datetime = Field(default=datetime.utcnow())

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson.dumps
        arbitrary_types_allowed = True

    # @validator('message')
    # def markdown_message(cls, value):
    #     return markdown(value)


class HistoryItemBase(BaseModel):
    user_id: int
    message: Message


class HistoryItemCreate(HistoryItemBase):
    ...


class HistoryItem(HistoryItemBase):
    created_at: datetime

    class Config:
        orm_mode = True
        json_loads = orjson.loads
        json_dumps = orjson.dumps
        arbitrary_types_allowed = True


class MeResponse(BaseModel):
    user_id: str = Field(alias="userId")
    token: str
    history: List[HistoryItem]