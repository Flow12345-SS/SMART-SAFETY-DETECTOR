from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

# Check if running on Vercel
is_vercel = os.environ.get("VERCEL", False)
default_db_path = "sqlite:////tmp/safety_detector.db" if is_vercel else "sqlite:///./safety_detector.db"

DATABASE_URL = os.getenv("DATABASE_URL", default_db_path)

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
