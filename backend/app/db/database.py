from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config.settings import settings


# Create the SQLAlchemy database engine
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}
)


# Create a session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db():
    """
    Provide a database session for FastAPI requests.
    """
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()