from fastapi import FastAPI
from routers import auth, registration, tasks, users

app = FastAPI()    

app.include_router(tasks.router)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(registration.router)






    



