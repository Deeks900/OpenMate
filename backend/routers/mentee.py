from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from models import User, Booking
from auth import get_current_user
from datetime import datetime, timedelta
from sqlalchemy import and_
import re
from config import settings

router = APIRouter(prefix="/mentee", tags=["Mentee"])

@router.get("/bookings")
def get_mentee_bookings(db: Session = Depends(get_db), user=Depends(get_current_user)):
    print("I am called")
    mentee_id = user.id
    
    today = datetime.today().strftime("%Y-%m-%d")

    bookings = (
        db.query(Booking)
        .filter(Booking.mentee_id == mentee_id)
        .filter(Booking.date >= today)
        .order_by(Booking.date.asc())
        .all()
    )

    result = []

    for b in bookings:
        mentor = db.query(User).filter(User.id == b.mentor_id).first()

        result.append({
            "booking_id": b.id,
            "date": b.date,
            "time": b.time,
            "mentor_name": mentor.profile.user_name if mentor else "",
            "mentor_email": mentor.email if mentor else "",
            "video_link": b.video_link
        })

    return result
