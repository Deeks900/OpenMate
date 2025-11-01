#This file is defiining the Database Tables
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from datetime import datetime
from database import Base
from sqlalchemy.orm import relationship

#Due to ORM each class is bascially table schema in db
#User Table in DB 
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="mentee")  # mentee or mentor
    created_at = Column(DateTime, default=datetime.utcnow)

    # relationships one to one with Profile Table
    profile = relationship("Profile", back_populates="user", uselist=False)

#Profile Table in DB 
class Profile(Base):
    __tablename__ = "profiles"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    bio = Column(Text)
    expertise = Column(String)
    public_slug = Column(String, unique=True)
    photo_url = Column(String, nullable=True)
 
    #SQLAlchemy Specific 
    user = relationship("User", back_populates="profile")
