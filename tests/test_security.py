from datetime import datetime, timedelta, timezone
import jwt
from core.config import ALGORITHM, SECRET_KEY
from core.security import create_access_token


def test_create_access_token():
    data = {"sub": "testuser"}
    token = create_access_token(data)

    decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    assert decoded["sub"] == "testuser"

def test_create_access_token_has_exp():
    data = {"sub": "testuser"}

    token = create_access_token(data)

    decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    assert "exp" in decoded

def test_create_access_token_custom_exp():
    data = {"sub": "testuser"}
    delta = timedelta(minutes=5)

    token = create_access_token(data, expires_delta=delta)
    decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    exp_time = datetime.fromtimestamp(decoded["exp"], tz=timezone.utc)
    now = datetime.now(timezone.utc)

    assert (exp_time - now) < timedelta(minutes=6)