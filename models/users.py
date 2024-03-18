from database import Base
from sqlalchemy import Column, String, Integer


class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(30), nullable=True, unique=True)
    password_hash = Column(String(255), nullable=False)
    token = Column(String(255), nullable=True)