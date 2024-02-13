from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import database
from functions.users import register
from schemas.users import CreateUser
from fastapi import HTTPException

users_router = APIRouter(
    prefix='/users'
)


@users_router.post('/register')
async def register_user(form: CreateUser, db: Session = Depends(database)):
    register(form, db)
    return HTTPException(status_code=201, detail="Siz ro'yxatdan muvaffaqiyatli o'tdingiz")





