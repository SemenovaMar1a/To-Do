from typing import Annotated
from fastapi import APIRouter, Depends, Form, HTTPException, Query, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import select
from passlib.context import CryptContext
from core.security import get_password_hash
from database import SessionDep
from dependencies import check_admin, get_current_user
from models.tasks import Task
from models.users import User
from schemas.tasks import TaskPublic
from schemas.users import Role, UserCreate, UserPublic, UserUpdate



router = APIRouter(prefix="/user", tags=["users"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
templates = Jinja2Templates(directory="templates")

@router.post("/registration", response_model=UserPublic)
def create_user(session: SessionDep, user: UserCreate):
    """Регистрация пользователя с JSON-ответом"""

    is_first_user = session.exec(select(User)).first() is None

    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=get_password_hash(user.password),
        role=Role.ADMIN if is_first_user else Role.USER)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

@router.patch("/{user_id}", response_model=UserPublic)
def update_user(
    user_id: int, 
    user_update: UserUpdate,  # Рекомендуется отдельная схема для обновления
    session: SessionDep, 
    current_user: User = Depends(get_current_user)
):
    """Редактирование пользователя (только своё для USER, любое для ADMIN) с JSON-ответом"""
    user_db = session.get(User, user_id)

    if not user_db:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    if current_user.role != Role.ADMIN and user_db.id != current_user.id:
        raise HTTPException(status_code=403, detail="Нет прав на изменение")

    update_data = user_update.model_dump(exclude_unset=True)

    if "role" in update_data and current_user.role != Role.ADMIN:
        raise HTTPException(403, "Только ADMIN может менять роль")
    
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    for key, value in update_data.items():
        setattr(user_db, key, value)

    session.add(user_db)
    session.commit()
    session.refresh(user_db)
    return user_db

@router.delete("/delete_user/{user_id}")
def delete_user(
    user_id: int, 
    session: SessionDep,
    current_user: User = Depends(get_current_user)):
    """Удаление порофиль пользователя по ID(только своё для USER, любое для ADMIN) с JSON-ответом"""
    user_db = session.get(User, user_id)
    if not user_db:
        raise HTTPException(status_code=404, detail="Профиль для удаления не найдена")

    if current_user.role != Role.ADMIN and user_db.id != current_user.id:
        raise HTTPException(status_code=403, detail="Нет прав на удаление")

    session.delete(user_db)
    session.commit()
    return {"ok": True}


@router.get("/", response_model=list[UserPublic])
def read_users(
    session: SessionDep, 
    _: User = Depends(check_admin), 
    offset: int = 0, 
    limit: Annotated[int, Query(le=100)] = 100,) -> list[User]:
    """Чтение данных о пользователях (только для админов) с JSON-ответом"""
    users = session.exec(select(User).offset(offset).limit(limit)).all()
    return users

@router.get("/me", response_model=UserPublic)
def read_users_me(current_user: Annotated[User, Depends(get_current_user)]):
    """Получение профеля авторизованного пользователя с JSON-ответом"""
    return current_user

@router.get("/users/me/tasks/", response_model=list[TaskPublic])
async def read_own_tasks(
    session: SessionDep, 
    current_user: Annotated[User, Depends(get_current_user)], 
    offset: int = 0, limit: Annotated[int, Query(le=100)] = 100):
    """Получение всех записей авторизованного пользователя с JSON-ответом"""
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
    """Получение одной задачи по ID(только своё для USER, любое для ADMIN) с JSON-ответом"""
    task_db = session.get(Task, task_id)
    if not task_db:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    if current_user.role != Role.ADMIN and task_db.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Нет прав на получение данных")
    return task_db


@router.get("/me-page")
def me_page(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Получение страницы авторизованного пользователя"""
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "user": current_user
    })

@router.get("/me/tasks")
def my_tasks_page(
    request: Request,
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_user)],
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100
):
    """Получение задач конкретного пользователя с HTML-ответом"""
    tasks = session.exec(
        select(Task).where(Task.user_id == current_user.id).offset(offset).limit(limit)
    ).all()
    return templates.TemplateResponse("user_tasks.html", {
        "request": request,
        "tasks": tasks,
        "user": current_user
    })

@router.post("/editing/{user_id}")
def edit_user_form(
    user_id: int,
    session: SessionDep, 
    current_user: User = Depends(get_current_user),
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...)):
    """Редактирование пользователя с HTML-ответом"""
    user_db = session.get(User, user_id)

    if not user_db or (current_user.role != Role.ADMIN and user_db.id != current_user.id):
        raise HTTPException(status_code=404, detail="Пользователь не найден или нет доступа")
    
    user_db.username = username
    user_db.email = email
    if user_db.hashed_password == password:
        user_db.hashed_password = password
    else:
        user_db.hashed_password = get_password_hash(password)

    session.commit()
    return RedirectResponse(url="/login", status_code=303)

@router.get("/editing/{user_id}")
def edit_user_form(
    request: Request,
    user_id: int, 
    session: SessionDep, 
    current_user: User = Depends(get_current_user)):
    """Получение страницы для редактирования пользователя с HTML-ответом"""
    user = session.get(User, user_id)
    if not user or (current_user.role != Role.ADMIN and user.id != current_user.id):
        raise HTTPException(status_code=404, detail="Пользователь не найден или нет доступа")

    return templates.TemplateResponse("edit_user.html", {
        "request": request,
        "user": user
    })

@router.post("/delete/{user_id}")
def delete_user(
    user_id: int, 
    session: SessionDep,
    current_user: User = Depends(get_current_user)):
    """Удаление профиля по ID с HTML-ответом"""
    user = session.get(User, user_id)
    if not user or (current_user.role != Role.ADMIN and user.id != current_user.id):
        raise HTTPException(status_code=404, detail="Профиль не найден или нет доступа")

    session.delete(user)
    session.commit()
    return RedirectResponse(url="/login", status_code=303)