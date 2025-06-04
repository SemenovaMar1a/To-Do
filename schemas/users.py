from enum import Enum
from sqlmodel import Field, SQLModel

class Role(str, Enum):
    USER = "user"
    ADMIN = "admin"

class UserBase(SQLModel):
    """Базовая модель пользователя"""
    username: str = Field(max_length=50, index=True, unique=True)
    email: str = Field(max_length=100, unique=True)
    role: Role = Field(default=Role.USER)

class UserPublic(UserBase):
    """Модель пользователя для ответа"""
    id: int

class UserCreate(UserBase):
    """Модель для создания данных пользователя"""
    password: str = Field(...)
    role: Role

class UserUpdate(UserBase):
    """Модель для обновления данных пользователя"""
    username: str | None = None
    email: str | None = None
    hashed_password: str | None = None