from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,  # Connection string: local SQLite file named openmate.db
    echo=True,  # Logs all SQL statements to console (useful for debugging),
    connect_args={"check_same_thread": False} #Needed in case of fast api
)

#Opening the connection with engine -- In this we have to write all SQL style queries
# with engine.connect() as conn:
#     #Checking the connection
#     result = conn.execute(text("SELECT sqlite_version();"))
#     print(result.fetchone())

#Creating a session factory --This way we will use ORM 
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#Will be used in builiding ORM Models
Base = declarative_base()

# Dependency for getting DB session in endpoints - so that in fastAPI each request will be operating independently
def get_db():
    db = SessionLocal()
    try:
        yield db #Ensures that function pauses here until api call completes work and then do db close
    finally:
        db.close()

