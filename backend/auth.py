from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import models
from database import get_db
from config import settings
#fastapi.security is a helper module provided by FastAPI that makes it super easy to implement authentication and authorization.
from fastapi.security import OAuth2PasswordBearer
#Jose is a Python Library to deal with JWT Tokens
from jose import JWTError, jwt, ExpiredSignatureError
#Passlib is a password hashing library for Python 2 & 3
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status

#bcrypt is a one way encryption hash algorithm that is you can't obtain a password if you have hashed value only password can be changed to hash 
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

#This is present in fastAPI to grab the Authorization token from request headers internally.Now we explicitly don't need to write requests.header.get
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

#This function is needed so that in db we never store plain passowrds 
def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    plain_password = plain_password.strip()
    hashed_password = hashed_password.strip()
    check = pwd_context.verify(plain_password, hashed_password)
    return check

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "token_type": "bearer"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

#In fastAPI Depends is used for Dependency Injection that is will fetch the values first and then will supply them as argumets to the function
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    print("I came in get_current_user")
    try:
        print("token is {}".format(token))
        print("RAW TOKEN BYTES:", repr(token))
        print("SECRET KEY USED:", settings.SECRET_KEY)
        print("ALGORITHM:", settings.ALGORITHM)
        #options={"verify_exp": False}
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        print("payload is {}".format(payload))
        #Get the user Id from the Payload of the JWT Token
        user_id: str = payload.get("sub")
        print(f"user is {user_id}")
        if user_id is None:
            raise credentials_exception
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except JWTError:
        raise credentials_exception

    user = db.query(models.User).filter(models.User.id == user_id).first()
    #user = db.query(models.User).filter(models.User.email == user_email).first()

    if user is None:
        raise credentials_exception
    return user

    