from fastapi import Depends, Request

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
# SQLALCHEMY_DATABASE_URL = 'mysql+pymysql://root@localhost:3306/chat'

engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def __with_db(request: Request):
    db = SessionLocal()

    request.state.db = db

    yield db


get_db = Depends(__with_db)
