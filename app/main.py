from fastapi import FastAPI
from .database import Base, engine
from app.utils.middlewares import handle_integrity_errors
from .user.routes import login, users
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(BaseHTTPMiddleware, dispatch=handle_integrity_errors)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],)

app.include_router(login.login_router)
app.include_router(users.user_router)
