# async def get_current_user(
#         session: SessionDep, 
#         token: Annotated[str, Depends(oauth2_scheme)]
#         ):
#     """Получение авторизованного пользователя"""
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Не удалось проверить учетные данные.",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
    
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         subject = payload.get("sub")
#         if subject is None:
#             raise credentials_exception
#         token_data = TokenData(username=subject)
#     except InvalidTokenError:
#         raise credentials_exception
#     user = get_user(session, username=token_data.username)
#     if user is None:
#         raise credentials_exception
#     return user

from unittest.mock import MagicMock

from database import get_session
from dependencies import get_current_user
from main import app

def test_get_current_user():
    fake_session = MagicMock()

    app.dependency_overrides[get_session] = lambda: fake_session
    
    gcu = get_current_user(fake_session)

    
