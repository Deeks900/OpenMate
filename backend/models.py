#Go to this https://sqliteonline.com/ and upload your openmate.db to run SQL Queries 
#This file is defiining the Database Tables
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, DateTime
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

    #relationship with Booking Table
    bookings_as_mentor = relationship("Booking", back_populates="mentor", foreign_keys="[Booking.mentor_id]")
    bookings_as_mentee = relationship("Booking", back_populates="mentee", foreign_keys="[Booking.mentee_id]")

    #relationship one to many with Availability Model
    availability = relationship("Availability", back_populates="mentor",cascade="all, delete")


#Profile Table in DB 
class Profile(Base):
    __tablename__ = "profiles"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    bio = Column(Text)
    expertise = Column(String)
    public_slug = Column(String, unique=True)
    photo_url = Column(String, nullable=True)
 
    #SQLAlchemy Specific 
    user = relationship("User", back_populates="profile")

class Availability(Base):
    __tablename__ = "availability"

    id = Column(Integer, primary_key=True, index=True)
    mentor_id = Column(Integer, ForeignKey("users.id"))
    date = Column(String)
    start_time = Column(String)
    end_time = Column(String)
    slot_duration = Column(Integer, default=30)

    #Relationship Many to one with User Model 
    mentor = relationship("User", back_populates="availability")
    #When the parent object is deleted, automatically delete the related child objects as well.
    slots = relationship("TimeSlot", back_populates="availability", cascade="all, delete")

#This table in db will be having all info about booking of the mentors 
class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    mentor_id = Column(Integer, ForeignKey("users.id"))
    mentee_id = Column(Integer, ForeignKey("users.id"))
    date = Column(String)
    time = Column(String)
    booking_time = Column(DateTime, default=datetime.utcnow)  
    status = Column(String, default="confirmed")
    
    #Relationship
    #This basically works like that when you will do Booking.mentor.name then internally it will be like Joining Users and Booking table on user.id == mentor-id and this back populates is used so books_as_mentor and mentor could be in sync
    mentor = relationship("User", back_populates="bookings_as_mentor", foreign_keys=[mentor_id])
    mentee = relationship("User", back_populates="bookings_as_mentee", foreign_keys=[mentee_id])


#This model is needed so that time slots can be configurable    
class TimeSlot(Base):
    __tablename__ = "time_slots"

    id = Column(Integer, primary_key=True, index=True)
    availability_id = Column(Integer, ForeignKey("availability.id"))
    mentor_id = Column(Integer, ForeignKey("users.id"))
    date = Column(String)
    start_time = Column(String)
    end_time = Column(String)
    is_booked = Column(Boolean, default=False)

    availability = relationship("Availability", back_populates="slots")    