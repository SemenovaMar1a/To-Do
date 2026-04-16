import os
from typing import Annotated
from dotenv import load_dotenv
from fastapi import Depends
from sqlmodel import SQLModel, Session, create_engine

load_dotenv()

"""Соединение с базой данных"""
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(SQLALCHEMY_DATABASE_URL)

def create_db_and_tables():
    """Создание таблиц"""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Создание сессий для каждого запроса"""
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]