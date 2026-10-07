from app.db.base import Base
from app.db.database import engine

from app.models.user import User  # noqa: F401


def init_db() -> None:
    """
    Create all database tables defined by SQLAlchemy models.
    """
    Base.metadata.create_all(bind=engine)