from unittest.mock import MagicMock

from sqlmodel import select

from database import get_session
from models.users import User
from tests.conftest import client, session
from main import app


def test_create_user_form_get(client):
    response = client.get("/registration")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

def test_create_user_form_post(client):
    test_new_user = MagicMock()

    fake_session = MagicMock()

    app.dependency_overrides[get_session] = lambda: fake_session

    data_form = {
        "username": "TestName",
        "email": "test@example.com",
        "password": "testpassword",
    }

    response = client.post("/registration", data=data_form, follow_redirects=False)

    fake_session.add.assert_called_once()
    fake_session.commit.assert_called_once()
    fake_session.refresh.assert_called_once()

    assert response.status_code == 302
    assert response.headers["location"] == "/login"

    app.dependency_overrides.clear()

def test_create_user_form_post_integration(client, session):
    data_form = {
        "username": "TestName",
        "email": "test@example.com",
        "password": "testpassword",
    }

    response = client.post("/registration", data=data_form, follow_redirects=False)

    new_user = session.exec(select(User).where(User.username == "TestName")).first()

    assert response.status_code == 302
    assert response.headers["location"] == "/login"

    assert new_user is not None




