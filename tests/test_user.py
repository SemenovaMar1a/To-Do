from unittest.mock import MagicMock
from core.security import create_access_token, get_password_hash
from database import get_session
from dependencies import get_current_user
from conftest import session, client, user
from models.users import User
from main import app
from schemas.users import Role

def test_user_me_page_get(client):
    fake_user = MagicMock()
    fake_user.id = 1

    app.dependency_overrides[get_current_user] = lambda: fake_user

    response = client.get("/user/me-page")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

    app.dependency_overrides.clear()

def test_user_me_page_get_tasks(client):
    fake_user = MagicMock()
    fake_user.id = 1

    fake_task = MagicMock()
    fake_task.title = "Test Task"
    fake_session = MagicMock()

    fake_session.exec.return_value.all.return_value = [fake_task]

    app.dependency_overrides[get_current_user] = lambda: fake_user
    app.dependency_overrides[get_session] = lambda: fake_session

    response = client.get("/user/me-page")
    assert response.status_code == 200
    assert "<title>Мой профиль</title>" in response.text
    assert "Test Task" in response.text

    app.dependency_overrides.clear()

def test_user_me_page_get_integration(user, client):
    token = create_access_token({"sub": str(user.username)})

    response = client.get("/user/me-page", headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

def test_user_me_page_get_integration_error_401(client):
    response = client.get("/user/me-page", headers={"Authorization": "Bearer WRONGTOKEN"})
    assert response.status_code == 401

def test_edit_user_form_post(client):
    fake_user = MagicMock()
    fake_user.id = 1
    fake_user.role = Role.USER

    fake_session = MagicMock()
    
    form_data = {
        "username": "TestUpdate",
        "email": "test@example.com",
        "password": "testpassword",
    }

    app.dependency_overrides[get_current_user] = lambda: fake_user
    app.dependency_overrides[get_session] = lambda: fake_session

    response = client.post(f"/user/editing/{fake_user.id}", data=form_data, follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/login"

    fake_session.commit.assert_called_once()

    app.dependency_overrides.clear()

def test_edit_user_form_post_no_user_error404(client):
    fake_user = MagicMock()
    fake_user.id = 1
    fake_user.role = Role.USER

    fake_session = MagicMock()
    
    form_data = {
        "username": "TestUpdate",
        "email": "test@example.com",
        "password": "testpassword",
    }

    app.dependency_overrides[get_current_user] = lambda: None
    app.dependency_overrides[get_session] = lambda: fake_session

    response = client.post(f"/user/editing/{fake_user.id}", data=form_data, follow_redirects=False)
    assert response.status_code == 404

    app.dependency_overrides.clear()

def test_edit_user_form_post_no_access_error404(client):
    fake_user1 = MagicMock()
    fake_user1.id = 1

    fake_user2 = MagicMock()
    fake_user2.id = 2
    fake_user2.role = Role.USER

    fake_session = MagicMock()
    
    form_data = {
        "username": "TestUpdate",
        "email": "test@example.com",
        "password": "testpassword",
    }

    app.dependency_overrides[get_current_user] = lambda: fake_user2
    app.dependency_overrides[get_session] = lambda: fake_session

    response = client.post(f"/user/editing/{fake_user1.id}", data=form_data, follow_redirects=False)
    assert response.status_code == 404

    app.dependency_overrides.clear()

def test_edit_user_form_post_access_admin(client):
    fake_user = MagicMock()
    fake_user.id = 1
    fake_user.role = Role.ADMIN

    fake_session = MagicMock()
    
    form_data = {
        "username": "TestUpdate",
        "email": "test@example.com",
        "password": "testpassword",
    }

    app.dependency_overrides[get_current_user] = lambda: fake_user
    app.dependency_overrides[get_session] = lambda: fake_session

    response = client.post(f"/user/editing/{fake_user.id}", data=form_data, follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/login"

    fake_session.commit.assert_called_once()

    app.dependency_overrides.clear()

def test_edit_user_form_post_integration(client, user, session):
    token = create_access_token({"sub": str(user.username)})

    form_data ={
        "username": "Alice",
        "email": "test@example.com",
        "password": get_password_hash("testpassword"),
    }

    response = client.post(f"/user/editing/{user.id}", headers={"Authorization": f"Bearer {token}"}, data=form_data, follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "/login"
    
    session.refresh(user)
    assert user.username == "Alice"

def test_edit_user_form_get(client):
    fake_user = MagicMock()
    fake_user.id = 1

    app.dependency_overrides[get_current_user] = lambda: fake_user

    response = client.get(f"/user/editing/{fake_user.id}")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

def test_edit_user_form_get_integration(client, user):
    token = create_access_token({"sub": str(user.username)})

    response = client.get(f"/user/editing/{user.id}", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

def test_delete_user_post(client):
    fake_user = MagicMock()
    fake_user.id = 1
    fake_user.role = Role.USER

    fake_session = MagicMock()

    app.dependency_overrides[get_current_user] = lambda: fake_user
    app.dependency_overrides[get_session] = lambda: fake_session

    response = client.post(f"/user/delete/{fake_user.id}", follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "/login"

    fake_session.delete.assert_called_once_with(fake_user)
    fake_session.commit.assert_called_once()

def test_delete_user_post_integration(client, user, session):
    token = create_access_token({"sub": str(user.username)})

    response = client.post(f"/user/delete/{user.id}", headers={"Authorization": f"Bearer {token}"}, follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "/login"

    delete_user = session.get(User, user.id)
    assert delete_user is None



