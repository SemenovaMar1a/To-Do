from typing import Annotated
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlmodel import SQLModel, Field, create_engine, Session, select

class HeroBase(SQLModel):
    """Базовая модель героя"""
    name: str = Field(index=True)
    age: int | None = Field(default=None, index=True)

class Hero(HeroBase, table=True):
    """Модель базы данных"""
    id: int | None = Field(default=None, primary_key=True)
    secret_name: str

class HeroPublic(HeroBase):
    """Модель героя для пользователей"""
    id: int

class HeroCreate(HeroBase):
    """Модель для создания данных героя"""
    secret_name: str

class HeroUpdate(HeroBase):
    """Модель для обновления данных героя"""
    name: str | None = None
    age: int | None = None
    secret_name: str | None = None

"""Соединение с базой данных"""
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def create_db_and_tables():
    """Создание таблиц"""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Создание сессий для каждого запроса"""
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI()

@app.on_event("startup")
def on_startup():
    """Временный роут для создания таблиц (в будущем сделать миграции)"""
    create_db_and_tables()

@app.post("/heroes/", response_model=HeroPublic)
def create_hero(hero: HeroCreate, session: SessionDep):
    """Создание героя"""
    db_hero = Hero.model_validate(hero)
    session.add(db_hero)
    session.commit()
    session.refresh(db_hero)
    return db_hero

@app.get("/heroes/", response_model=list[HeroPublic])
def read_heroes(session: SessionDep, offset: int = 0, limit: Annotated[int, Query(le=100)] = 100,) -> list[Hero]:
    """Чтение данных о героях"""
    heroes = session.exec(select(Hero).offset(offset).limit(limit)).all()
    return heroes

@app.post("/heroes/{hero_id}", response_model=HeroPublic)
def read_hero(hero_id: int, session: SessionDep):
    """Получение одного героя по ID"""
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Герой не найден")
    return hero

@app.patch("/heroes/{hero_id}", response_model=HeroPublic)
def update_hero(hero_id: int, hero: HeroUpdate, session: SessionDep):
    """Обновления данных героя"""
    hero_db = session.get(Hero, hero_id)
    if not hero_db:
        raise HTTPException(status_code=404, detail="Герой не найден")
    
    hero_data = hero.model_dump(exclude_unset=True)
    print("Received data:", hero_data)  # Логируем входные данные

    hero_db.sqlmodel_update(hero_data)
    session.add(hero_db)
    session.commit()
    session.refresh(hero_db)
    return hero_db

@app.delete("/heroes/{hero_id}")
def delete_hero(hero_id: int, session: SessionDep):
    """Удаление героя по ID"""
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Герой для удаления не найден")
    session.delete(hero)
    session.commit()
    return {"ok": True}
