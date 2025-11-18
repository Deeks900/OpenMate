from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine
from routers import users, mentors, bookings, profile

app = FastAPI(title="OpenMate Backend")

# Create DB tables
Base.metadata.create_all(bind=engine)

# Allow frontend requests (Angular)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  # NO "*"
    allow_credentials=True,  
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users.router)
app.include_router(mentors.router)
app.include_router(bookings.router)
app.include_router(profile.router)

@app.get("/")
def home():
    return {"message": "Welcome to OpenMate API 🚀"}