from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from core.config import ACCESS_TOKEN_EXPIRE_MINUTES
from core.security import create_access_token
from schemas.token import Token
from database import SessionDep
from services.user import authenticate_user


templates = Jinja2Templates(directory="templates")


router = APIRouter()

class OAuth2PasswordBearerWithCookie(OAuth2PasswordBearer):
    """Auth2 через пароль с куки"""
    async def __call__(self, request: Request) -> str:
        """Получить токен из заголовка или куки"""
        auth_header = request.headers.get("Authorization")
        if auth_header:
            return await super().__call__(request)

        token = request.cookies.get("access_token")
        if token:
            if token.startswith("Bearer "):
                token = token[len("Bearer "):]
            return token

        return await super().__call__(request)

@router.post("/token")
async def login_for_access_token(session: SessionDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    """Поток паролей OAuth2 для генерации токенов"""
    user = authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")

@router.get("/login")
def login_get(request: Request):
    """Отображает форму авторизации"""
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
async def login_form(
    request: Request,
    session: SessionDep,
    username: str = Form(...),
    password: str = Form(...),
):
    """Аунтификация и вывод токена"""
    user = authenticate_user(session, username, password)
    if not user:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Неверный логин или пароль"
        })

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    #Сохраняем токен в куку
    response = RedirectResponse("/user/me-page", status_code=302)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return response
