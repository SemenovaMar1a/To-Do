from fastapi import FastAPI, Request
from routers import auth, registration, tasks, users
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")
app = FastAPI()    

app.include_router(tasks.router)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(registration.router)

@app.get("/")
async def read_main(request: Request):
    return templates.TemplateResponse("main.html", {"request": request})









    

