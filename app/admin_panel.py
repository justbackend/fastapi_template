from datetime import timedelta
from typing import Optional

from fastapi import HTTPException, status
from jose import jwt, JWTError
from sqladmin.authentication import AuthenticationBackend
from sqlalchemy.orm import Session
from sqlalchemy.testing.pickleable import User
from starlette.requests import Request

from app.user.models.user import User
from app.user.routes.login import pwd_context, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, \
    ALGORITHM
from app.user.schemas.tokens import TokenData
from database import get_db
from .config import Settings as settings


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request, db: Session = next(get_db())) -> bool:
        form = await request.form()
        username, password = form["username"], form["password"]
        user = db.query(User).where(User.username == username).first()
        if user:
            is_validate_password = pwd_context.verify(password, user.password_hash)
        else:
            return False

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        db.query(User).filter(User.id == user.id).update({
            User.token: access_token
        })
        db.commit()
        request.session.update({"token": access_token})
        return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")

        if not token:
            return False

        user = await get_current_user(request)
        if user:
            return True
        return False


async def get_current_user(token, db: Session = next(get_db())):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: Optional[str] = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = db.query(User).where(User.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    return user

authentication_backend = AdminAuth(secret_key=settings.SECRET_KEY)

