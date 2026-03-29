from unittest.mock import MagicMock
import pytest
from sqlmodel import select
from core.security import create_access_token
from database import get_session
from dependencies import get_current_user
from models.tasks import Task
from schemas.users import Role
from tests.conftest import client, test_user
from main import app
from models.tasks import Task


@pytest.fixture
def test_task(session, test_user):
    task = Task(
        title="TestTitle",
        description="TestDescription",
        user_id=test_user.id,
    )
    session.add(task)
    session.commit()
    session.refresh(task)

    yield task

def test_create_task_form_get(client):
    fake_user = MagicMock()

    app.dependency_overrides[get_current_user] = lambda: fake_user

    response = client.get("/task/create_form")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

    app.dependency_overrides.clear()

def test_create_task_form_get_integration(client, test_user):
    token = create_access_token({"sub": str(test_user.username)})

    response = client.get("/task/create_form", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

def test_create_task_form_get_integration_error_401(client):
    response = client.get("/task/create_form", headers={"Authorization": "Bearer WRONGTOKEN"})

    assert response.status_code == 401

def test_create_task_form_post(client):
    fake_user = MagicMock()
    fake_user.id = 1

    fake_session = MagicMock()

    form_data = {
        "title": "TestTitle",
        "description": "TestDescription",
    }

    app.dependency_overrides[get_current_user] = lambda: fake_user
    app.dependency_overrides[get_session] = lambda: fake_session

    response = client.post("/task/create_form", data=form_data, follow_redirects=False)

    assert response.status_code == 302
    assert response.headers["location"] == "/user/me-page"

    fake_session.add.assert_called_once()
    fake_session.commit.assert_called_once()
    fake_session.refresh.assert_called_once()

    app.dependency_overrides.clear()

def test_create_task_form_post_integration(client, test_task, test_user, session):
    token = create_access_token({"sub": str(test_user.username)})

    form_data = {
        "title": "TestTitle",
        "description": "TestDescription",
    }

    response = client.post("/task/create_form", headers={"Authorization": f"Bearer {token}"}, data=form_data, follow_redirects=False)

    assert response.status_code == 302
    assert response.headers["location"] == "/user/me-page"

    new_task = session.exec(select(Task).where(Task.title == "TestTitle")).first()

    assert new_task is not None
    assert new_task.user_id == test_user.id

def test_delete_task_post(client):
    test_task = MagicMock()
    test_task.id = 1
    test_task.user_id = 1

    test_user = MagicMock()
    test_user.id = 1
    test_user.role = Role.USER

    fake_session = MagicMock()

    fake_session.get.return_value = test_task
    
    app.dependency_overrides[get_current_user] = lambda: test_user
    app.dependency_overrides[get_session] = lambda: fake_session

    response = client.post(f"/task/delete/{test_task.id}", follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "/user/me-page"

    fake_session.delete.assert_called_once_with(test_task)
    fake_session.commit.assert_called_once()

    app.dependency_overrides.clear()

def test_delete_task_post_integration(client, test_user, session, test_task):
    token = create_access_token({"sub": str(test_user.username)})

    response = client.post(f"/task/delete/{test_task.id}", headers={"Authorization": f"Bearer {token}"}, follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "/user/me-page"

    delete_task = session.get(Task, test_task.id)
    assert delete_task is None

def test_delete_task_post_no_task_error404(client):
    test_task = MagicMock()
    test_task.id = 1
    test_task.user_id = 1

    test_user = MagicMock()
    test_user.id = 1
    test_user.role = Role.USER

    fake_session = MagicMock()

    fake_session.get.return_value = None
    
    app.dependency_overrides[get_current_user] = lambda: test_user
    app.dependency_overrides[get_session] = lambda: fake_session

    response = client.post(f"/task/delete/{test_task.id}", follow_redirects=False)

    assert response.status_code == 404

    app.dependency_overrides.clear()

def test_delete_task_post_no_access_error404(client):
    test_task = MagicMock()
    test_task.id = 1
    test_task.user_id = 1

    test_user = MagicMock()
    test_user.id = 2
    test_user.role = Role.USER

    fake_session = MagicMock()

    fake_session.get.return_value = test_task
    
    app.dependency_overrides[get_current_user] = lambda: test_user
    app.dependency_overrides[get_session] = lambda: fake_session

    response = client.post(f"/task/delete/{test_task.id}", follow_redirects=False)

    assert response.status_code == 404

    app.dependency_overrides.clear()

def test_delete_task_post_access_admin(client):
    test_task = MagicMock()
    test_task.id = 1
    test_task.user_id = 1

    test_user = MagicMock()
    test_user.id = 1
    test_user.role = Role.ADMIN

    fake_session = MagicMock()

    fake_session.get.return_value = test_task
    
    app.dependency_overrides[get_current_user] = lambda: test_user
    app.dependency_overrides[get_session] = lambda: fake_session

    response = client.post(f"/task/delete/{test_task.id}", follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "/user/me-page"

    fake_session.delete.assert_called_once_with(test_task)
    fake_session.commit.assert_called_once()

    app.dependency_overrides.clear()

def test_delete_task_post_integration_error_401(client, test_task):
    response = client.post(f"/task/delete/{test_task.id}", headers={"Authorization": "Bearer WRONGTOKEN"})

    assert response.status_code == 401

def test_complete_task(client):
    test_task = MagicMock()
    test_task.id = 1
    test_task.user_id = 1
    test_task.is_completed = True 

    test_user = MagicMock()
    test_user.id = 1
    test_user.role = Role.USER

    fake_session = MagicMock()
    fake_session.get.return_value = test_task

    app.dependency_overrides[get_current_user] = lambda: test_user
    app.dependency_overrides[get_session] = lambda: fake_session

    response = client.post(f"/task/complete/{test_task.id}", follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "/user/me-page"

    fake_session.commit.assert_called_once()

    assert test_task.is_completed is True

    app.dependency_overrides.clear()

def test_complete_task_integration(client, test_task, test_user, session):
    token = create_access_token({"sub": str(test_user.username)})

    response = client.post(f"/task/complete/{test_task.id}",headers={"Authorization": f"Bearer {token}"}, follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "/user/me-page"

    task = session.get(Task, test_task.id)
    assert task.is_completed is True

    

