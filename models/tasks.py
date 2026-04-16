from datetime import datetime
from sqlmodel import Column, Field, ForeignKey, func

from schemas.tasks import TaskBase


class Task(TaskBase, table=True):
    """Модель здачи базы данных"""
    __tablename__ = "tasks"
    id: int | None = Field(default=None, primary_key=True)
    is_completed: bool = Field(default=False)
    created_at: datetime = Field(
        sa_column_kwargs={"server_default": func.now()},
        nullable=False
    )
    user_id: int = Field(
        foreign_key="users.id",
    )
    

