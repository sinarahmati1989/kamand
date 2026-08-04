"""
Database Connection
ساخت Engine و مدیریت اتصال
"""

import logging
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from app.config.settings import settings


logger = logging.getLogger(__name__)


def create_db_engine() -> Engine:
    """ساخت Engine دیتابیس"""
    
    engine = create_engine(
        settings.DATABASE_URL,
        echo=False,           # اگه True کنی، همه SQL ها لاگ میشن
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,   # چک زنده بودن قبل استفاده
        pool_recycle=3600,    # هر ساعت اتصال جدید
    )
    
    logger.info(f"Database engine created for: {settings.DB_NAME}@{settings.DB_HOST}")
    return engine


def test_connection(engine: Engine) -> bool:
    """تست اتصال به دیتابیس"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.scalar()
            logger.info(f"✅ Database connection OK")
            logger.info(f"PostgreSQL Version: {version}")
            return True
    except SQLAlchemyError as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False


# Singleton Engine
engine: Engine = create_db_engine()