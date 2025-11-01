#Load Environment Variables cleanly 
from pydantic_settings import BaseSettings

#BaseSettings -> Base class for settings in pydantic, allowing values to be overridden by environment variables.
class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    DATABASE_URL: str
    
    #This class Pydantic expects so that it can know from which file it needs to load values in the class members above
    class Config:
        env_file = ".env"

settings = Settings()
