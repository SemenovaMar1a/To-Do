from unittest.mock import MagicMock, patch
import pytest
from database import get_session
from main import app
from starlette.requests import Request
from starlette.datastructures import Headers, MutableHeaders
from unittest.mock import AsyncMock

from routers.auth import OAuth2PasswordBearerWithCookie


def test_login_for_access_token_post(client):
    fake_user = MagicMock()
    fake_user.username = "test"

    with patch("routers.auth.authenticate_user") as mock_auth:
        mock_auth.return_value = fake_user

        response = client.post("/token", data={"username": "test", "password": "123"},)

        assert response.status_code == 200

def test_login_for_access_token_integration(client, test_user):
    response = client.post("/token", data={"username": test_user.username, "password": "testpassword", "grant_type": "password"},)
    
    assert response.status_code == 200
    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_for_access_token_error401(client):
    response = client.post("/token", data={"username": "testuser", "password": "wrong",},)

    assert response.status_code == 401
    assert response.json()["detail"] == "Неверное имя пользователя или пароль"

@pytest.mark.asyncio
async def test_token_from_header():
    headers = Headers({"Authorization": "Bearer mytoken"})
    request = Request({"type": "http", "headers": headers.raw})

    oauth = OAuth2PasswordBearerWithCookie(tokenUrl="token")
    # патчим super().__call__, чтобы он возвращал то, что мы ожидаем
    with patch("fastapi.security.oauth2.OAuth2PasswordBearer.__call__", new=AsyncMock(return_value="header_token"),):
        token = await oauth(request)

    assert token == "header_token"

@pytest.mark.asyncio
async def test_token_from_cookie():
    headers = [(b"cookie", b"access_token=Bearer cookietoken")]
    scope = {"type": "http", "headers": headers}
    request = Request(scope)

    oauth = OAuth2PasswordBearerWithCookie(tokenUrl="token")

    token = await oauth(request)
    assert token == "cookietoken"

@pytest.mark.asyncio
async def test_no_token():
    # пустой request
    scope = {"type": "http", "headers": [], "cookies": {}}
    request = Request(scope)

    oauth = OAuth2PasswordBearerWithCookie(tokenUrl="token")
    
    with patch("fastapi.security.oauth2.OAuth2PasswordBearer.__call__", new=AsyncMock(return_value="fallbacktoken"),):
        token = await oauth(request)

    assert token == "fallbacktoken"

def test_login_get(client):
    response = client.get("/login")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

def test_login_form(client):
    fake_session = MagicMock()
    app.dependency_overrides[get_session] = lambda: fake_session

    with patch("routers.auth.authenticate_user") as mock_auth:
        test_user = MagicMock()
        test_user.username = "TestName"
        mock_auth.return_value = test_user

        response = client.post("/login",data={"username": "TestName", "password": "TestPassword"}, follow_redirects=False)

        assert response.status_code == 302
        assert response.headers["location"] == "/user/me-page"
        mock_auth.assert_called_once_with(fake_session, "TestName", "TestPassword")

def test_login_form_integration(client, test_user):
    response = client.post("/login", data={"username": test_user.username, "password": "testpassword"}, follow_redirects=False)

    assert response.status_code == 302
    assert response.headers["location"] == "/user/me-page"

def test_login_form_error(client):
    with patch("routers.auth.authenticate_user") as mock_auth:
        mock_auth.return_value = None

        response = client.post("/login", data={"username": "test", "password": "wrong"})

        assert response.status_code == 200
        assert "Неверный логин или пароль" in response.text
        