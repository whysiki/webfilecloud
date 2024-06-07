# encoding: utf-8

from models import SessionLocal

# Depend db session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
        

