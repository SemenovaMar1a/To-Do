from fastapi.testclient import TestClient
import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, create_engine, Session
from core.security import get_password_hash
from database import get_session
from main import app
from models.users import User
from schemas.users import Role

TEST_DATABASE_URL = "sqlite://"

test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool,)

@pytest.fixture()
def create_test_db(session):
    SQLModel.metadata.create_all(session.get_bind())
    yield
    SQLModel.metadata.drop_all(session.get_bind())


@pytest.fixture(scope="function")
def session():
    connection = test_engine.connect()
    transaction = connection.begin()

    SQLModel.metadata.create_all(connection)  # создаём таблицы на этом соединении

    session = Session(bind=connection)
    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(session):
    def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()

@pytest.fixture
def test_user(session):
    user = User(
        username="TestName",
        email="test@example.com",
        hashed_password=get_password_hash("testpassword"),
        role = Role.USER,
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    yield user

