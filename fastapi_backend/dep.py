# encoding: utf-8
from models import SessionLocal
import auth
from fastapi import Header
from typing import Optional


# Depend db session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_access_token(Authorization: Optional[str] = Header(None)):
    return auth.get_access_token_from_Authorization(Authorization)
