from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from starlette.responses import JSONResponse

from database import get_db
from models.users import Users
from routes.login import get_current_user

success_response = JSONResponse(
    status_code=200,
    content={'message': 'Operation completed successfully'}
)

CurrentUser = Annotated[Users, Depends(get_current_user)]
SessionDep = Annotated[Session, Depends(get_db)]