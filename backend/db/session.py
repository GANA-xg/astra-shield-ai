from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session

from core.config import settings
from core.logging import logger

engine = None
SessionLocal = None

if settings.DATABASE_URL:
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
    )

    SessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
    )


def get_db():
    """
    FastAPI dependency that provides a database session.
    Yields None if DATABASE_URL is not configured (callers must handle).
    """
    if SessionLocal is None:
        logger.warning("DATABASE_URL not configured — DB features disabled")
        yield None
        return

    db: Session = SessionLocal()

    try:
        yield db
    finally:
        db.close()


def check_database_connection() -> bool:
    """
    Verify that the application can connect to PostgreSQL.
    """
    if engine is None:
        return False

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
