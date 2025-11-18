from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from database import get_db
from auth import get_current_user
from models import Profile
from schemas import ProfileUpdate, ProfileResponse

router = APIRouter(prefix="/profile", tags=["Profile"])

@router.put("/update", response_model=ProfileResponse)
def update_profile(data: ProfileUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    print(f"Update profile function is running.")
    if user.role != "mentor":
        raise HTTPException(status_code=403, detail="Only mentors can update profile")

    profile = db.query(Profile).filter(Profile.user_id == user.id).first()

    profile.bio = data.bio
    profile.expertise = data.expertise
    if data.photo_url:
        profile.photo_url = data.photo_url
    
    print(f"Profile Object is {profile}")
    db.commit()
    db.refresh(profile)
    print("Final profile onject is {profile}")

    return profile

@router.post("/upload-photo")
def upload_photo(file: UploadFile = File(...), db: Session = Depends(get_db), user=Depends(get_current_user)):

    result = upload(file.file, folder="mentor_profiles")

    profile = db.query(Profile).filter(Profile.user_id == user.id).first()
    if not profile:
        profile = Profile(user_id=user.id)

    profile.photo_url = result["secure_url"]

    db.add(profile)
    db.commit()
    db.refresh(profile)

    return {"photo_url": profile.photo_url}

#Return the profile of the current user 
@router.get("/me", response_model=ProfileResponse)
def get_my_profile(db: Session = Depends(get_db), user=Depends(get_current_user)):
    profile = db.query(Profile).filter(Profile.user_id == user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile
