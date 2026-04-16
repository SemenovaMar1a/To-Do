from sqlmodel import select
from core.security import verify_password
from database import SessionDep
from models.users import User


def get_user(db, username: str):
    """Получение пользователя из бд"""
    stmt = select(User).where(User.username == username)
    return db.scalars(stmt).first()

def authenticate_user(session: SessionDep, username: str, password: str):
    """Проверка на существование пользователя и совместимость пароля"""
    user = get_user(session, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

