from pydantic import BaseModel


class CreateUser(BaseModel):
    username: str
    password_hash: str


class UpdateUser(BaseModel):
    id: str
    username: str
    password_hash: str


class UserCurrent(BaseModel):
    id: int
    username: str
    password: str
