from fastapi import FastAPI
from database import Base, engine
from routes import login, users


Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(login.login_router)
app.include_router(users.users_router)
