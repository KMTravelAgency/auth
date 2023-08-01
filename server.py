from fastapi import Depends, FastAPI, HTTPException, Request
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from dotenv import load_dotenv
import base64, datetime, os
import binascii

from sql_app import crud, models, schemas
from sql_app.database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

load_dotenv()

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

    if result is not None:    
        if username != result.email or password != result.password:
            return "invalid credentials", 401
        else:
            return createJWT(username, os.environ.get("SECRET_KEY"), True)
    return "invalid credentials", 401

    

@app.post("/validate")
def validate(request: Request, ):
    encoded_JWT = request.headers['Authorization']

    if not encoded_JWT:
        return "missing credentials", 401
    
    encoded_JWT = encoded_JWT.split(" ")[1]
    print(encoded_JWT)
    try:
        decoded = jwt.decode(
            encoded_JWT, os.environ.get("SECRET_KEY"), algorithms=os.getenv("ALGORITHM") 
        )
    except:
        return "not authorized", 403
    
    return decoded, 200

def createJWT(username, secret, authz):
    return jwt.encode(
        {
            "username": username,
            "exp": datetime.datetime.now(tz=datetime.timezone.utc)
            + datetime.timedelta(days=1),
            "iat": datetime.datetime.utcnow(),
            "admin": authz,
        },
        secret,
        algorithm=os.getenv("ALGORITHM"),
    )