from datetime import datetime
from sqlmodel import Field, func

from schemas.tasks import TaskBase


class Task(TaskBase, table=True):
    """Модель здачи базы данных"""
    __tablename__ = "tasks"
    id: int | None = Field(default=None, primary_key=True)
    is_completed: bool | None = Field(default=False)
    created_at: datetime = Field(
        default_factory=datetime.now,
        sa_column_kwargs={"server_default": func.now()},  
        nullable=False,  
    )
    user_id: int = Field(foreign_key="users.id", ondelete="CASCADE")
    

