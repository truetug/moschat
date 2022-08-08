from app.schemas import HistoryItemCreate, UserCreate
from app.services.auth.helpers import get_password_hash
from sqlalchemy.orm import Session

from .models import History, User


def get_user(session: Session, user_id: int):
    return session.query(User).filter(User.id == user_id).first()


def get_user_by_username(session: Session, username: str):
    return session.query(User).filter(User.email == username).first()


def get_users(session: Session, skip: int = 0, limit: int = 100):
    return session.query(User).offset(skip).limit(limit).all()


def create_user(session: Session, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(email=user.email, password=hashed_password)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def create_history_item(session: Session, item: HistoryItemCreate):
    obj = History(user_id=item.user_id, message=item.message)
    session.add(obj)
    session.commit()
    session.refresh(obj)
    return obj


def get_history_items(
    session: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
):
    return (
        session.query(History)
        .filter(History.user_id == user_id)
        .order_by(History.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
