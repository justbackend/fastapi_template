from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    password: str


class UpdateUser(BaseModel):
    id: str
    username: str
    password: str


class UserCurrent(BaseModel):
    id: int
    username: str
    password: str
