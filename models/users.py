from sqlmodel import Field
from schemas.users import UserBase


class User(UserBase, table=True):
    """Модель таблицы пользователя базы данных"""
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str