from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from database import get_db
from auth import get_current_user
from models import TimeSlot, Booking, User
from schemas import BookingCreate, BookingResponse

router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.post("/", response_model=BookingResponse)
def create_booking(data: BookingCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    """
    Mentee books a time slot.
    """

    slot = db.query(TimeSlot).filter(TimeSlot.id == data.slot_id).first()
    if not slot:
        raise HTTPException(status_code=404, detail="Time slot not found")

    if slot.is_booked:
        raise HTTPException(status_code=400, detail="Slot already booked")

    booking = Booking(
        mentor_id=slot.mentor_id,
        mentee_id=user.id,   # mentee is the logged in user
        date=slot.date,
        time=f"{slot.start_time}-{slot.end_time}",
        booking_time=datetime.utcnow()
    )

    slot.is_booked = True  # Mark slot as taken
    db.add(booking)
    db.commit()
    db.refresh(booking)

    return booking


@router.get("/my", response_model=list[BookingResponse])
def my_bookings(db: Session = Depends(get_db), user=Depends(get_current_user)):
    """
    Returns bookings made BY the current user (mentee).
    """
    return db.query(Booking).filter(Booking.mentee_id == user.id).all()


@router.get("/mentor", response_model=list[BookingResponse])
def mentor_bookings(db: Session = Depends(get_db), user=Depends(get_current_user)):
    """
    Returns bookings for the current mentor.
    """
    if user.role != "mentor":
        raise HTTPException(status_code=403, detail="Only mentors can access this")

    return db.query(Booking).filter(Booking.mentor_id == user.id).all()
