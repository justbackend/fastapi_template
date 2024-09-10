from app.database import Base
from sqlalchemy import Column, String, Integer


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(30), nullable=True, unique=True)
    password = Column(String(255), nullable=False)
