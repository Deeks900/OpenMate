#This file will be containing registration and login end points 
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import models, schemas
from database import get_db
from auth import hash_password, verify_password, create_access_token

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
    return db_user

@router.post("/login")
def login(data: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == data.email).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}    