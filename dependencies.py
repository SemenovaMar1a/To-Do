from asyncio import Task
from typing import Annotated
from fastapi import Depends, HTTPException, status
import jwt
from jwt import InvalidTokenError
from core.config import ALGORITHM, SECRET_KEY
from database import SessionDep
from models.users import User
from routers.auth import OAuth2PasswordBearerWithCookie
from schemas.token import TokenData
from schemas.users import Role
from services.user import get_user


oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="token")

async def get_current_user(session: SessionDep, token: Annotated[str, Depends(oauth2_scheme)]):
    """Получение авторизованного пользователя"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось проверить учетные данные.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(session, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def check_admin(user: User = Depends(get_current_user)):
    """Проверяет, является ли пользователь админом"""
    if user.role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Требуются права администратора"
        )
    return user

async def get_user_filter(user: User = Depends(get_current_user)):
    """Возвращает фильтр для запросов: user_id для USER, None для ADMIN"""
    return Task.user_id == user.id if user.role == Role.USER else None