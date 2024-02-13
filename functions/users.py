from models.users import Users
from routes.login import get_password_hash


def register(form, db):
    new_user = Users(
        username=form.username,
        password_hash=get_password_hash(form.password_hash),
    )
    db.add(new_user)
    db.commit()