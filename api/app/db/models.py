from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, func, JSON
from sqlalchemy.orm import relationship

from . import Base


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    is_active = Column(Boolean, default=True)

    history = relationship("History")

    @property
    def username(self):
        return self.email

    @property
    def perms(self):
        result = []
        if self.id:
            result.append("can_use_weather")

        return result


class History(Base):
    __tablename__ = "history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", back_populates="history", lazy="joined")
    message = Column(JSON)
    created_at = Column(DateTime, server_default=func.now())
