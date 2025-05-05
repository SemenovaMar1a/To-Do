from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt import InvalidTokenError
from core.config import ALGORITHM, SECRET_KEY
from database import SessionDep
from schemas.token import TokenData
from services.user import get_user


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(session: SessionDep, token: Annotated[str, Depends(oauth2_scheme)]):
    """Получение авторизованного пользователя"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
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