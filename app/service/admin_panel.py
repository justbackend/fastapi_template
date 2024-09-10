from datetime import timedelta

from sqladmin import ModelView
from sqladmin.authentication import AuthenticationBackend
from sqlalchemy.orm import Session

from starlette.requests import Request

from app.auth import verify_password, decode_access_token, credentials_exception, create_access_token, \
    ACCESS_TOKEN_EXPIRE_MINUTES
from app.user.models import User
from app.database import get_db
from app.config import Settings as settings


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request, db: Session = next(get_db())) -> bool:
        form = await request.form()
        username, password = form["username"], form["password"]
        user = db.query(User).where(User.username == username).first()
        if user:
            verify_password(password, user.password)
        else:
            return False

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.id}, expires_delta=access_token_expires
        )
        request.session.update({"token": access_token})
        return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")

        if not token:
            return False

        user = await current_user(token)
        if user:
            return True
        return False


def current_user(token: str, db: Session = next(get_db())):

    user_id = decode_access_token(token)
    if user_id is None:
        raise credentials_exception
    user = db.query(User).filter(User.id==user_id).first()
    if user is None:
        raise credentials_exception
    return user


class UserAdmin(ModelView, model=User):
    column_list = "__all__"


def admin_panel_apply(admin):
    admin.add_view(UserAdmin)


authentication_backend = AdminAuth(secret_key="09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7")



