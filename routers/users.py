from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import select
from passlib.context import CryptContext # type: ignore
from database import SessionDep
from dependencies import check_admin, get_current_user
from models.tasks import Task
from models.users import User
from schemas.tasks import TaskPublic
from schemas.users import Role, UserCreate, UserPublic



router = APIRouter(prefix="/user", tags=["users"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/registration", response_model=UserPublic)
def create_user(user: UserCreate, session: SessionDep):
    """Создание пользователя"""

    is_first_user = session.exec(select(User)).first() is None

    hashed_password = pwd_context.hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        role=Role.ADMIN if is_first_user else Role.USER)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

@router.get("/", response_model=list[UserPublic])
def read_users(
    session: SessionDep, 
    _: User = Depends(check_admin), 
    offset: int = 0, 
    limit: Annotated[int, Query(le=100)] = 100,) -> list[User]:
    """Чтение данных о пользователях (только для админов)"""
    users = session.exec(select(User).offset(offset).limit(limit)).all()
    return users

@router.get("/me", response_model=UserPublic)
def read_users_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user

@router.get("/users/me/items/", response_model=list[TaskPublic])
async def read_own_items(
    session: SessionDep, 
    current_user: Annotated[User, Depends(get_current_user)], 
    offset: int = 0, limit: Annotated[int, Query(le=100)] = 100):
    tasks = session.exec(select(Task)
                         .where(Task.user_id == current_user.id)
                         .offset(offset)
                         .limit(limit)).all()
    return tasks

@router.post("/{task_id}", response_model=TaskPublic)
def read_task(
    task_id: int, 
    session: SessionDep,
    current_user: User = Depends(get_current_user)):
    """Получение одной задачи по ID(только своё для USER, любое для ADMIN)"""
    task_db = session.get(Task, task_id)
    if not task_db:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    if current_user.role != Role.ADMIN and task_db.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Нет прав на получение данных")
    return task_db