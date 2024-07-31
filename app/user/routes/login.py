from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm.session import Session
from app.database import get_db

from app.user.models.user import User
from app.user.schemas.tokens import TokenData, Token
from app.user.schemas.users import UserCreate
from app.config import settings
session = Session()


SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.JWT_EXPIRE


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

login_router = APIRouter(tags=['Login and Refresh token'])


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# async def get_current_user_socket(websocket: WebSocket, db: Session = Depends(get_db)):
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     try:
#         token = websocket.query_params.get("token")
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         username: Optional[str] = payload.get("sub")
#         if username is None:
#             raise credentials_exception
#         token_data = TokenData(username=username)
#     except JWTError:
#         raise credentials_exception
#     user = db.query(Users).where(Users.username == token_data.username).first()
#     if user is None:
#         raise credentials_exception
#     return user


def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
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


def token_has_expired(token: str) -> bool:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        expiration_time = datetime.fromtimestamp(payload.get("exp"))
        current_time = datetime.utcnow()
        return current_time > expiration_time
    except jwt.JWTError:
        return False


@login_router.post("/refresh_token", response_model=Token)
async def refresh_token(
    db: Session = Depends(get_db),
    token: str = None
):
    user = db.query(User).where(User.token == token).first()
    if user is None:
        raise HTTPException(
            status_code=400,
            detail="Token error",
        )

    if not token_has_expired(token):
        raise HTTPException(
            status_code=400,
            detail="Token has not expired",
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    db.query(User).filter(User.id == user.id).update({
        User.token: access_token
    })

    return {
        'id': user.id,
        "access_token": access_token,
        "token_type": "bearer"
    }
