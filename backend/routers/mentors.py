from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from schemas import AvailabilityCreate, AvailabilityResponse, TimeSlotResponse
from models import Availability, TimeSlot
from auth import get_current_user
from datetime import datetime, timedelta
from sqlalchemy import and_

router = APIRouter(prefix="/mentors", tags=["Mentors"])

#This function will be generating slots within the availability time depending upon slot duration submitted
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
    # Convert start/end to datetime for easy comparison
    new_start_dt = datetime.strptime(f"{data.date} {data.start_time}", "%Y-%m-%d %H:%M")
    new_end_dt = datetime.strptime(f"{data.date} {data.end_time}", "%Y-%m-%d %H:%M")

    # Check for any overlapping availability for the same mentor on the same date
    overlapping = db.query(Availability).filter(
        Availability.mentor_id == user.id,
        Availability.date == data.date,
        # Overlap condition: new_start < existing_end AND new_end > existing_start
        and_(
            new_start_dt.time() < Availability.end_time,
            new_end_dt.time() > Availability.start_time
        )
    ).first()

    if overlapping:
        raise HTTPException(status_code=400, detail="This time range overlaps with existing availability")
    
    slot = Availability(
        mentor_id=user.id,
        date=data.date,
        start_time=data.start_time,
        end_time=data.end_time,
        slot_duration=data.slot_duration or 30
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

@router.get("/my-availability", response_model=list[AvailabilityResponse])
def get_my_availability(db: Session = Depends(get_db), user=Depends(get_current_user)):
    """
    Fetch all availabilities of the logged-in mentor.
    """
    if user.role != "mentor":
        raise HTTPException(status_code=403, detail="Only mentors can view this")

    availabilities = db.query(Availability).filter(Availability.mentor_id == user.id).all()
    return availabilities

@router.get("/availability/{id}/slots", response_model=list[TimeSlotResponse])
def get_slots_by_availability_id(id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if user.role != "mentor":
        raise HTTPException(status_code=403, detail="Only mentors can view this")

    slots = db.query(TimeSlot).filter(
        TimeSlot.availability_id == id,
        TimeSlot.mentor_id == user.id
    ).all()
    
    print("i am giving slots")
    return slots

@router.delete("/slots/{slot_id}")
def delete_slot(slot_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):

    # Ensure only mentor can delete
    if user.role != "mentor":
        raise HTTPException(status_code=403, detail="Only mentors can delete slots")

    # Fetch slot
    slot = db.query(TimeSlot).filter(
        TimeSlot.id == slot_id,
        TimeSlot.mentor_id == user.id
    ).first()

    if not slot:
        raise HTTPException(status_code=404, detail="Slot not found")

    availability_id = slot.availability_id

    # Delete slot
    db.delete(slot)
    db.commit()

    # Check if availability now has ZERO remaining slots
    remaining_slots = db.query(TimeSlot).filter(
        TimeSlot.availability_id == availability_id
    ).count()

    if remaining_slots == 0:
        availability = db.query(Availability).filter(
            Availability.id == availability_id,
            Availability.mentor_id == user.id
        ).first()

        if availability:
            db.delete(availability)
            db.commit()

    return {"message": "Slot deleted successfully"}
