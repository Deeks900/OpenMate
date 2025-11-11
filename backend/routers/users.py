#This file will be containing registration and login end points 
from fastapi import APIRouter, Depends, HTTPException, status, Response, Cookie, Response 
from sqlalchemy.orm import Session
import models, schemas
from database import get_db
from auth import hash_password, verify_password, create_access_token
from datetime import timedelta


#tags will be helpful in grouping in Swagger Docs
router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=schemas.UserOut)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = hash_password(user.password)
    db_user = models.User(
        name=user.name,
        email=user.email,
        password_hash=hashed_pw,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    #Make python object in sync with DB row inserted just now
    db.refresh(db_user)

    #Now if the user is a mentor we will be creating a profile of the user 
    if db_user.role == "mentor":
        # Generate public slug (unique link) => name-use-lowercase-with-dashes
        slug = db_user.name.lower().replace(" ", "-") + f"{db_user.id}"

        new_profile = models.Profile(
            user_id=db_user.id,
            bio="",
            expertise="",
            public_slug=slug,
            photo_url=None
        )
        db.add(new_profile)
        db.commit()

    return db_user

@router.post("/login", response_model=schemas.TokenResponse)
def login(data: schemas.LoginRequest, response: Response, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == data.email).first()
    print(f"User is {user.name} and password is {user.password_hash} and entered password is {data.password}")
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    print("user id is {}".format(str(user.id)))
    #Access token will be short lived 
    access_token = create_access_token({
        "sub": str(user.id),       
        "role": user.role          
    })
    #Refresh token will be long lived 
    refresh_token = create_access_token({ "sub": str(user.id) }, expires_delta=timedelta(days=7))
   
    # Set refresh token as HttpOnly cookie (can't be read by JS).But browser will be attaching it with every http request
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True, #So that JS can't read it
        secure=False, #In production I will be keeping it as true so that it will be sent over https only   
        #it will NOT be sent in most cross-site requests, such as when another website tries to make a request to your server on behalf of the user.This helps prevent CSRF attacks (Cross-Site Request Forgery).  
        samesite="Lax",
        max_age=7*24*60*60 #7 days is the life 
    )

    return {"access_token": access_token, "token_type": "bearer", "role": user.role}    

#Refresh End Point
@router.post("/refresh", response_model=schemas.TokenResponse)
def refresh_token(refresh_token: str = Cookie(None), db: Session = Depends(get_db)):
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Missing refresh token")

    try:
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    access_token = create_access_token({"sub": str(user.id), "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}  