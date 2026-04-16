from datetime import datetime
from sqlmodel import Field, SQLModel


class TaskBase(SQLModel):
    """Базовая модель задачи"""
    title: str = Field(max_length=100, index=True)
    description: str | None = Field(default=None)

class TaskPublic(TaskBase):
    """Модель задачи для ответа"""
    id: int
    is_completed: bool
    created_at: datetime  

class TaskCreate(TaskBase):
    """Модель для создания данных задачи"""
    user_id: int = Field(..., foreign_key="users.id", ondelete="CASCADE")

class TaskUpdate(TaskBase):
    """Модель для обновления данных задачи"""
    title: str | None = None
    description: str | None = None
    is_completed: bool | None = None