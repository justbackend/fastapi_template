from fastapi import HTTPException

from app.auth import get_password_hash, create_access_token
from app.user.models.user import User


def register(form, db):
    user = db.query(User).filter(User.username == form.username).first()

    if user:
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed_password = get_password_hash(form.password)
    user = User(username=form.username, password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)

    access_token = create_access_token({'id': user.id})
    return access_token
