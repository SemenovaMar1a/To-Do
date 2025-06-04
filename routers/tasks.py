from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import select
from database import SessionDep
from dependencies import get_current_user
from models.tasks import Task
from models.users import User
from schemas.tasks import TaskCreate, TaskPublic, TaskUpdate
from schemas.users import Role


router = APIRouter(prefix="/task", tags=["tasks"])

@router.post("/", response_model=TaskPublic)
def create_task(
    task: TaskCreate, 
    session: SessionDep, 
    current_user: User = Depends(get_current_user)):
    """Создание задачи (автоматически привязываем к текущему пользователю)"""
    db_task = Task.model_validate(task)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task

# @router.get("/", response_model=list[TaskPublic])
# def read_tasks(session: SessionDep, filter=Depends(get_user_filter), offset: int = 0, limit: Annotated[int, Query(le=100)] = 100) -> list[Task]:
#     """Чтение задач (все для админа, только свои для пользователей)"""
#     query = select(Task)
#     if filter in not None:
#         query = query.where(filter)
#     tasks = session.exec(query.offset(offset).limit(limit)).all()
#     return tasks


# @router.post("/{task_id}", response_model=TaskPublic)
# def read_task(
#     task_id: int, 
#     session: SessionDep,
#     current_user: User = Depends(get_current_user)):
#     """Получение одной задачи по ID(только своё для USER, любое для ADMIN)"""
#     task = session.get(Task, task_id)
#     if not task:
#         raise HTTPException(status_code=404, detail="Задача не найдена")
#     if current_user.role != Role.ADMIN and task_db.user_id != current_user.id:
#         raise HTTPException(status_code=403, detail="Нет прав на получение данных")
#     return task

@router.patch("/{task_id}", response_model=TaskPublic)
def update_task(
    task_id: int, 
    task: TaskUpdate, 
    session: SessionDep, 
    current_user: User = Depends(get_current_user)):
    """Обновление задачи (только своё для USER, любое для ADMIN)"""
    task_db = session.get(Task, task_id)

    if not task_db:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    
    if current_user.role != Role.ADMIN and task_db.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Нет прав на изменение")
    
    task_data = task.model_dump(exclude_unset=True)
    task_db.sqlmodel_update(task_data)

    session.add(task_db)
    session.commit()
    session.refresh(task_db)
    return task_db

@router.delete("/{task_id}")
def delete_task(
    task_id: int, 
    session: SessionDep,
    current_user: User = Depends(get_current_user)):
    """Удаление задачи по ID(только своё для USER, любое для ADMIN)"""
    task_db = session.get(Task, task_id)
    if not task_db:
        raise HTTPException(status_code=404, detail="Задача для удаления не найдена")

    if current_user.role != Role.ADMIN and task_db.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Нет прав на удаление")

    session.delete(task_db)
    session.commit()
    return {"ok": True}