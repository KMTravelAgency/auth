from fastapi import Depends, FastAPI, HTTPException, Request
from sqlalchemy.orm import Session
import base64
import binascii

from sql_app import crud, models, schemas
from sql_app.database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

#Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/login")
def login(request: Request, db: Session = Depends(get_db)):
    auth = request.headers['Authorization']
    if  not auth:
        return "missing credentials", 401
    
    try:
        scheme, credentials = auth.split()
        if scheme.lower() != 'basic':
            return
        decoded = base64.b64decode(credentials).decode("ascii")
    except (ValueError, UnicodeDecodeError, binascii.Error) as exc:
            raise print('Invalid basic auth credentials')
    username, _, password = decoded.partition(":")
    
    # DB check for username and password
    result = crud.get_user_by_email(db, username)

    print(result.email)
    
    if username != result.email or password != result.password:
        return "invalid credentails", 401
    else:
        return result, "You have been verified"

    

@app.post("/validate")
def validate():
    pass