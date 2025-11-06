from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from schemas import AvailabilityCreate, AvailabilityResponse, TimeSlotResponse
from models import Availability, TimeSlot
from auth import get_current_user
from datetime import datetime, timedelta

router = APIRouter(prefix="/mentors", tags=["Mentors"])


def generate_slots(start, end, duration):
    slots = []
    current = start
    while current < end:
        slot_end = current + timedelta(minutes=duration)
        if slot_end <= end:
            slots.append((current, slot_end))
        current = slot_end
    return slots


@router.post("/availability", response_model=AvailabilityResponse)
def add_availability(data: AvailabilityCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    slot = Availability(
        mentor_id=user.id,
        date=data.date,
        start_time=data.start_time,
        end_time=data.end_time,
        slot_duration=data.slot_duration
    )

    db.add(slot)
    db.flush()   # <-- temporary save, but not final commit
    db.refresh(slot)

    start_dt = datetime.strptime(f"{data.date} {data.start_time}", "%Y-%m-%d %H:%M")
    end_dt = datetime.strptime(f"{data.date} {data.end_time}", "%Y-%m-%d %H:%M")

    splitted_slots = generate_slots(start_dt, end_dt, data.slot_duration)

    for s_start, s_end in splitted_slots:
        ts = TimeSlot(
            availability_id=slot.id,
            mentor_id=user.id,
            date=data.date,
            start_time=s_start.strftime("%H:%M"),
            end_time=s_end.strftime("%H:%M")
        )
        db.add(ts)

    db.commit()

    return slot

#Getting all available dates 
@router.get("/availability/dates/{mentor_id}", response_model=list[str])
def get_available_dates(mentor_id: int, db: Session = Depends(get_db)):
    dates = db.query(TimeSlot.date)\
              .filter(TimeSlot.mentor_id == mentor_id, TimeSlot.is_booked == False)\
              .distinct()\
              .all()
    return [d[0] for d in dates]

#Getting all slots for a specific date 
@router.get("/availability/{mentor_id}/{date}", response_model=list[TimeSlotResponse])
def get_free_slots(mentor_id: int, date: str, db: Session = Depends(get_db)):
    slots = db.query(TimeSlot).filter(
        TimeSlot.mentor_id == mentor_id,
        TimeSlot.date == date,
        TimeSlot.is_booked == False
    ).all()

    return slots
