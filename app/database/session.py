"""
Session Manager
Session Factory و Context Manager
"""

import logging
from contextlib import contextmanager
from typing import Generator

from sqlalchemy.orm import sessionmaker, Session

from app.database.connection import engine


logger = logging.getLogger(__name__)


# Session Factory
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """
    Context manager برای Session
    
    استفاده:
        with get_session() as session:
            user = session.query(User).first()
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Session rolled back: {e}")
        raise
    finally:
        session.close()