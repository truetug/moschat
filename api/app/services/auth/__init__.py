from sqlalchemy.orm import Session

from app.schemas import Message, HistoryItem
from app.services import BaseService
from app.services.auth.helpers import verify_password, create_access_token
from app.services.exceptions import ServiceValidationError


class AuthService(BaseService):
    async def process(self, session: Session, *args) -> Message:
        try:
            print("COMMAND ARGS", args)
            username, password = args
        except Exception:
            raise ServiceValidationError("Что-то не так с аргументами")

        from app.db.services import get_user_by_username
        user = get_user_by_username(session, username=username)
        if not user:
            raise ServiceValidationError("Неверное имя пользователя")

        if not verify_password(password, user.password):
            raise ServiceValidationError("Неверный пароль")

        from app.db.services import get_history_items
        history = get_history_items(session, user_id=user.id, limit=10)
        history = [HistoryItem.from_orm(x).dict() for x in history]
        history.reverse()

        return Message(
            type="auth",
            message=f"Вы успешно авторизованы как `{user.username}`",
            data={
                "user_id": user.username,
                "history": history,
                "access_token": create_access_token({
                    "sub": user.username,
                    "perms": user.perms,
                }),
            },
        )
