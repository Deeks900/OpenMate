from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine
from routers import users

app = FastAPI(title="OpenMate Backend")

# Create DB tables
Base.metadata.create_all(bind=engine)

# Allow frontend requests (Angular)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users.router)

@app.get("/")
def home():
    return {"message": "Welcome to OpenMate API 🚀"}