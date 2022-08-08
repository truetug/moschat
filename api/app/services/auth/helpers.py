from datetime import datetime, timedelta
from typing import Optional, Union

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from starlette import status
from starlette.requests import Request

from app.db import get_session
from app.db.models import User
from app.schemas import TokenData
from app.settings.base import SECRET_KEY, ALGORITHM

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return ctx.verify(plain_password, hashed_password)


def get_password_hash(password):
    return ctx.hash(password)


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_token(request: Request):
    print("HEADERS", request.headers)
    result = request.headers.get("Authorization", "")
    if result:
        result = result.split()[-1]

    return result


async def get_current_user(
    session: Session = Depends(get_session),
    token: Optional[str] = Depends(get_token),
) -> Optional[User]:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        print("PARSE TOKEN", token)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None

        data = TokenData(username=username)
    except JWTError:
        return None

    from app.db.services import get_user_by_username
    user = get_user_by_username(session, username=data.username)
    if user is None:
        return None

    return user


async def get_current_active_user(user: User = Depends(get_current_user)):
    if not user:
        ip = "127001"
        user = User(email=f"anonymous_{ip}", is_active=True)
    elif not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )

    print("USER", user.username)
    return user
