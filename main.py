from fastapi import FastAPI
from database import create_db_and_tables
from routers import auth, tasks, users

app = FastAPI()    

app.include_router(tasks.router)
app.include_router(users.router)
app.include_router(auth.router)

@app.on_event("startup")
def on_startup():
    """Временный роут для создания таблиц (в будущем сделать миграции)"""
    create_db_and_tables()







    



