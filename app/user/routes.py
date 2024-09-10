from datetime import timedelta

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from app.auth import create_access_token, verify_password, SessionDep
from app.user.models import User

from app.user.schemas import UserCreate
from fastapi import HTTPException

from app.user.views import register

user_router = APIRouter(
    prefix='/user'
)


@user_router.post("/register")
async def register_endpoint(form: UserCreate, db: SessionDep):
    access_token = register(form, db)
    return {"access_token": access_token, "token_type": "bearer"}


@user_router.post('/login')
def login_for_access_token(db: SessionDep, form: OAuth2PasswordRequestForm = Depends()):
    user = db.query(User).filter(User.username == form.username).first()
    if not user or not verify_password(form.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.id})

    return {"access_token": access_token, "token_type": "bearer"}

