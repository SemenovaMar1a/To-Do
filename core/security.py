from datetime import datetime, timedelta, timezone
import jwt
from passlib.context import CryptContext
from core.config import SECRET_KEY, ALGORITHM

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    """Проверяет, совпадает ли введённый пароль с его хэшированной версией """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """Принимает обычный пароль и возвращает его хэшированную версию"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """Создает JWT-токен с payload `data` и временем жизни `expires_delta` (по умолчанию 15 минут)"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt