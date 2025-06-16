from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import select

from core.security import get_password_hash
from database import SessionDep
from models.users import User
from schemas.users import Role


router = APIRouter(tags=["registration"])
templates = Jinja2Templates(directory="templates")

"""Страница регистрации"""
@router.get("/registration")
def create_user_form(request: Request):
    """Получение страницы регистрации"""
    return templates.TemplateResponse("registration.html", {"request": request})

@router.post("/registration")
def create_user_form(
    request: Request,
    session: SessionDep,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...)
):
    """Добавление нового пользователя"""
    is_first_user = session.exec(select(User)).first() is None
    db_user = User(
        username=username,
        email=email,
        hashed_password=get_password_hash(password),
        role=Role.ADMIN if is_first_user else Role.USER
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    
    # После регистрации — перенаправляем на логин
    return RedirectResponse("/login", status_code=302)