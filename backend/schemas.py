#This file will be defining schemas to do data type validation in Fast API Calls.Invalid and Missing inputs will be blocked before actually reaching Database. 
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

#When someone sends a data to create a new user then do these data type validations
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str  # "mentor" or "mentee"

#When someone needs the details of a given user 
class UserOut(BaseModel):
    id: int
    name: str
    email: str
    role: str
    created_at: datetime
    #This is important because we are using SQLAlchemy so basically returned results from db will be object so we are telling it to access results using dot notation instead of expecting a dictionary of values like user.name should be done instead of user['name']
    class Config:
        orm_mode = True

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str    

# --- BOOKING ---
class BookingCreate(BaseModel):
    slot_id: int   # instead of mentor_id/date/time

class BookingResponse(BaseModel):
    id: int
    mentor_id: int
    mentee_id: int
    date: str
    time: str
    booking_time: datetime

    class Config:
        orm_mode = True


# --- AVAILABILITY ---
class AvailabilityCreate(BaseModel):
    date: str
    start_time: str
    end_time: str
    slot_duration: Optional[int] = 30

class AvailabilityResponse(BaseModel):
    id: int
    mentor_id: int
    date: str
    start_time: str
    end_time: str
    slot_duration: int

    class Config:
        orm_mode = True  

class TimeSlotResponse(BaseModel):
    id: int
    date: str
    start_time: str
    end_time: str
    is_booked: bool

    class Config:
        orm_mode = True
