from typing import Optional
from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from database import SessionDep
from dependencies import get_current_user
from models.tasks import Task
from models.users import User
from schemas.tasks import TaskCreate, TaskPublic, TaskUpdate
from schemas.users import Role


router = APIRouter(prefix="/task", tags=["tasks"])
templates = Jinja2Templates(directory="templates")

@router.post("/", response_model=TaskPublic)
def create_task(
    task: TaskCreate, 
    session: SessionDep, 
    current_user: User = Depends(get_current_user)):
    """Создание задачи (автоматически привязываем к текущему пользователю) с JSON-ответом"""
    db_task = Task.model_validate(task)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task

@router.patch("/{task_id}", response_model=TaskPublic)
def update_task(
    task_id: int, 
    task: TaskUpdate, 
    session: SessionDep, 
    current_user: User = Depends(get_current_user)):
    """Обновление задачи (только своё для USER, любое для ADMIN) с JSON-ответом"""
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

@router.delete("/delete_task/{task_id}")
def delete_task(
    task_id: int, 
    session: SessionDep,
    current_user: User = Depends(get_current_user)):
    """Удаление задачи по ID(только своё для USER, любое для ADMIN) с JSON-ответом"""
    task_db = session.get(Task, task_id)
    if not task_db:
        raise HTTPException(status_code=404, detail="Задача для удаления не найдена")

    if current_user.role != Role.ADMIN and task_db.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Нет прав на удаление")

    session.delete(task_db)
    session.commit()
    return {"ok": True}

@router.get("/create_form")
def create_task_form(
    request: Request, 
    current_user: User = Depends(get_current_user)):
    """Добавление новой задачи с HTML-ответом"""
    return templates.TemplateResponse("creating_a_task.html", {
        "request": request, 
        "user": current_user})

@router.post("/create_form")
def create_task_form(
    session: SessionDep,
    current_user: User = Depends(get_current_user),
    title: str = Form(...),
    description: str = Form(...)):
    """Создание задачи с HTML-ответом"""
    db_task = Task(
        title=title,
        description=description,
        user_id=current_user.id
    )
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return RedirectResponse("/user/me/tasks", status_code=302)

@router.post("/delete/{task_id}", name="delete_task")
def delete_task(
    task_id: int, 
    session: SessionDep,
    current_user: User = Depends(get_current_user)):
    """Удаление задачи по ID с HTML-ответом"""
    task = session.get(Task, task_id)
    if not task or (current_user.role != Role.ADMIN and task.user_id != current_user.id):
        raise HTTPException(status_code=404, detail="Задача не найдена или нет доступа")

    session.delete(task)
    session.commit()
    return RedirectResponse(url="/user/me/tasks", status_code=303)

@router.post("/complete/{task_id}", name="complete_task")
def complete_task(task_id: int, session: SessionDep, current_user: User = Depends(get_current_user)):
    """Выполнение задачи по ID с HTML-ответом"""
    task = session.get(Task, task_id)
    if not task or (current_user.role != Role.ADMIN and task.user_id != current_user.id):
        raise HTTPException(status_code=404, detail="Задача не найдена или нет доступа")

    task.is_completed = True
    session.commit()
    return RedirectResponse(url="/user/me/tasks", status_code=303)


@router.post("/editing/{task_id}")
def update_task(
    task_id: int,
    session: SessionDep, 
    current_user: User = Depends(get_current_user),
    title: str = Form(...),
    description: str = Form(...),
    is_completed: Optional[str] = Form(None)):
    """Обновление задачи с HTML-ответом"""
    task_db = session.get(Task, task_id)

    if not task_db or (current_user.role != Role.ADMIN and task_db.user_id != current_user.id):
        raise HTTPException(status_code=404, detail="Задача не найдена или нет доступа")
    
    task_db.title = title
    task_db.description = description
    task_db.is_completed = is_completed == "true"

    session.commit()
    return RedirectResponse(url="/user/me/tasks", status_code=303)

@router.get("/editing/{task_id}")
def edit_task_form(
    request: Request,
    task_id: int, 
    session: SessionDep, 
    current_user: User = Depends(get_current_user)):
    """Обновление задачи с HTML-ответом"""
    task = session.get(Task, task_id)
    if not task or (current_user.role != Role.ADMIN and task.user_id != current_user.id):
        raise HTTPException(status_code=404, detail="Задача не найдена или нет доступа")

    return templates.TemplateResponse("edit_task.html", {
        "request": request,
        "task": task
    })