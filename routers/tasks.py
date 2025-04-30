from typing import Annotated
from fastapi import APIRouter, HTTPException, Query
from sqlmodel import select
from database import SessionDep
from models import Task
from schemas import TaskCreate, TaskPublic, TaskUpdate


router = APIRouter(prefix="/task", tags=["tasks"])

@router.post("/", response_model=TaskPublic)
def create_task(task: TaskCreate, session: SessionDep):
    """Создание задачи"""
    db_task = Task.model_validate(task)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task

@router.get("/", response_model=list[TaskPublic])
def read_tasks(session: SessionDep, offset: int = 0, limit: Annotated[int, Query(le=100)] = 100,) -> list[Task]:
    """Чтение данных о задаче"""
    tasks = session.exec(select(Task).offset(offset).limit(limit)).all()
    return tasks

@router.post("/{task_id}", response_model=TaskPublic)
def read_task(task_id: int, session: SessionDep):
    """Получение одной задачи по ID"""
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return task

@router.patch("/{task_id}", response_model=TaskPublic)
def update_task(task_id: int, task: TaskUpdate, session: SessionDep):
    """Обновления данных задачи"""
    task_db = session.get(Task, task_id)

    if not task_db:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    
    task_data = task.model_dump(exclude_unset=True)
    task_db.sqlmodel_update(task_data)

    session.add(task_db)
    session.commit()
    session.refresh(task_db)
    return task_db

@router.delete("/{task_id}")
def delete_task(task_id: int, session: SessionDep):
    """Удаление задачи по ID"""
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Задача для удаления не найдена")
    session.delete(task)
    session.commit()
    return {"ok": True}