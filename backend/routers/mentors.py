from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from schemas import AvailabilityCreate, AvailabilityResponse, TimeSlotResponse, ProfileResponse
from models import Availability, TimeSlot, User, Profile, Booking
from auth import get_current_user
from datetime import datetime, timedelta
from sqlalchemy import and_
import re
from config import settings
import requests
import base64

#Standard Python module to send emails via SMTP.
import smtplib
#Helps construct rich emails (HTML + plain text)
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

router = APIRouter(prefix="/mentors", tags=["Mentors"])

#Zoom Meeting
CLIENT_ID = settings.CLIENT_ID
CLIENT_SECRET = settings.CLIENT_SECRET
# Email config
#Gmail SMTP server and port for sending emails.
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
#Credentials of the email account sending the messages.
EMAIL_USERNAME = settings.EMAIL_USERNAME
EMAIL_PASSWORD = settings.EMAIL_PASSWORD


def get_zoom_access_token():
    url = "https://zoom.us/oauth/token"

    # Base64 encoding for Basic auth
    auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
    headers = {
        "Authorization": "Basic " + base64.b64encode(auth_str.encode()).decode(),
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "grant_type": "account_credentials",
        "account_id": settings.ZOOM_ACCOUNT_ID
    }

    # MUST be data= not params=
    response = requests.post(url, data=data, headers=headers)

    if response.status_code != 200:
        print("\nZOOM TOKEN ERROR:", response.text)
        raise Exception("Failed to get access token")

    return response.json()["access_token"]
    
def create_zoom_meeting(start_time, duration_minutes, topic="OpenMate Session"):
    token = get_zoom_access_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    data = {
        "topic": topic,
        "type": 2,  # Scheduled meeting
        "start_time": start_time,  # ISO format: "2025-11-25T10:00:00Z"
        "duration": duration_minutes,
        "timezone": "Asia/Kolkata",
        "settings": {
            "host_video": True,
            "participant_video": True,
            "join_before_host": False
        }
    }

    response = requests.post(
        "https://api.zoom.us/v2/users/me/meetings",
        headers=headers,
        json=data
    )
    res_json = response.json()
    return res_json.get("join_url")



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

#This endpoit will be call to show all mentors 
@router.get('/mentors-list', response_model=list[ProfileResponse])
def get_all_mentors(db: Session = Depends(get_db)):
    #Through join solving N+1 query profile
    mentors = db.query(User).join(Profile).filter(User.role == "mentor").all()
    return [
        Profile(
           id = m.profile.id,
           user_id = m.id,
           user_name = m.name,
           bio = m.profile.bio if m.profile else "",
           expertise = m.profile.expertise if m.profile else "",
           public_slug = m.profile.public_slug if m.profile else "",
           photo_url = m.profile.photo_url if m.profile else "",
        ) for m in mentors
    ]

#This end point to show all available slots of a particular mentor 
@router.get('/slots/{mentor_id}')
def get_available_slots(mentor_id: int, date: str = Query(..., description="Date to get slots for in YYYY-MM-DD format"), db: Session = Depends(get_db)):
    slots = (db.query(TimeSlot)
            .filter(TimeSlot.mentor_id == mentor_id, TimeSlot.date == date, TimeSlot.is_booked==0)
            .all()
    )
    if not slots:
        return []

    return [
        f"{slot.start_time} - {slot.end_time}"
        for slot in slots
    ]    



def send_email(to_email, subject, body):
    #Creates an email object that can contain HTML + attachments
    msg = MIMEMultipart()
    msg['From'] = EMAIL_USERNAME
    msg['To'] = to_email
    msg['Subject'] = subject
    #Attach HTML content to the email.
    msg.attach(MIMEText(body, 'html'))
    #Connects to Gmail SMTP server.
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    #Secures the connection using TLS.
    server.starttls()
    
    #Authenticates the email account.
    server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
    server.send_message(msg)
    #Closes the connection.
    server.quit()       

#This end point will be used to book slot 
@router.post("/book-slot")
def book_slot(data: dict, db: Session = Depends(get_db), user=Depends(get_current_user)):
    mentor_id = data["mentor_id"]
    slot_text = data["slot"]
    date = data["date"]
    start, end = re.split(r"\s*[-–—]\s*", slot_text)

    # Validate mentor and mentee exist
    mentor = db.query(User).filter(User.id == mentor_id).first()
    if not mentor:
        raise HTTPException(status_code=400, detail="Mentor or mentee not found")

    #Grab this slot
    slot = db.query(TimeSlot).filter(
        TimeSlot.mentor_id == mentor_id,
        TimeSlot.start_time == start,
        TimeSlot.end_time == end,
        TimeSlot.is_booked == 0
    ).first()

    if not slot:
        raise HTTPException(status_code=404, detail="Slot not available")

    slot.is_booked = 1
    db.commit()

    start_dt = datetime.strptime(f"{date} {start}", "%Y-%m-%d %H:%M")
    end_dt = datetime.strptime(f"{date} {end}", "%Y-%m-%d %H:%M")
    duration = int((end_dt - start_dt).total_seconds() / 60)

    # Create Zoom meeting
    video_link = create_zoom_meeting(start_dt.isoformat(), duration, topic="OpenMate Session")

    # Create booking record
    booking = Booking(
        mentor_id=mentor_id,
        mentee_id=user.id,
        time=slot_text,
        date=date,
        video_link=video_link,
        slot_id=slot.id
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)

    # Send email to both mentor and mentee
    email_body = f"""
<p>Your session has been booked!</p>
<p>Mentor: {mentor.profile.user_name}</p>
<p>Mentee: {user.profile.user_name}</p>
<p>Slot: {slot_text} on {date}</p>
<p>Join via Zoom: <a href="{video_link}">{video_link}</a></p>
"""
   
    send_email(mentor.email, "New Session Booked", email_body)
    send_email(user.email, "Session Confirmation", email_body)

    return {"message": "Booking confirmed", "video_link": video_link}

def normalize_time_range(time_string: str):
    # Remove extra spaces
    cleaned = time_string.replace(" ", "")
    # Split by dash
    start, end = cleaned.split("-")
    return start, end

#This will be showing all bookings of a mentor
@router.get("/bookings")
def get_mentor_bookings(db: Session = Depends(get_db), user=Depends(get_current_user)):

    mentor_id = user.id

    # All booked slots for this mentor
    slots = db.query(TimeSlot).filter(
        TimeSlot.mentor_id == mentor_id,
        TimeSlot.is_booked == True
    ).all()

    print(f"slots sre {slots}")

    results = []

    for slot in slots:

        # Find the matching booking for this date + slot time
        bookingRow = db.query(Booking).filter(
            Booking.slot_id == slot.id
        ).first()

        video_link = None
        mentee_name = None
        mentee_email = None

        if bookingRow and bookingRow.mentee:
            mentee_name = bookingRow.mentee.profile.user_name
            mentee_email = bookingRow.mentee.email

        
        results.append({
            "booking_id": bookingRow.id if bookingRow else None,
            "date": bookingRow.slot.date if bookingRow else None,
            "start_time": bookingRow.slot.start_time if bookingRow else None,
            "end_time": bookingRow.slot.end_time if bookingRow else None,
            "slot": f"{bookingRow.slot.start_time} - {bookingRow.slot.end_time}" if bookingRow else None,
            "mentor_id": bookingRow.slot.mentor_id if bookingRow else None,
            "video_link": bookingRow.video_link if bookingRow else None,
            "mentee_name": bookingRow.mentee.name if bookingRow else None,
            "mentee_email": bookingRow.mentee.email if bookingRow else None
        })

    return results
