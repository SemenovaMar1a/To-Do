from sqlmodel import Field, SQLModel


class UserBase(SQLModel):
    """Базовая модель пользователя"""
    username: str = Field(max_length=50, index=True, unique=True)
    email: str = Field(max_length=100, unique=True)

class UserPublic(UserBase):
    """Модель пользователя для ответа"""
    id: int

class UserCreate(UserBase):
    """Модель для создания данных пользователя"""
    password: str = Field(...)

class UserUpdate(UserBase):
    """Модель для обновления данных пользователя"""
    username: str | None = None
    email: str | None = None
    hashed_password: str | None = None