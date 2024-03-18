from fastapi import FastAPI
from database import Base, engine
from routes import login, users
from starlette.middleware.base import BaseHTTPMiddleware
from middlewares import unit_of_work_middleware

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.add_middleware(BaseHTTPMiddleware, dispatch=unit_of_work_middleware)

app.include_router(login.login_router)
app.include_router(users.users_router)
