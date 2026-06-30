"""SQLAlchemy engine, session və DB hazır olmasını gözləmə.

PostgreSQL container backend-dən gec qalxa bildiyi üçün startup-da
qısa retry ilə bağlantı yoxlanılır.
"""
from __future__ import annotations

import logging
import time

from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import get_settings

logger = logging.getLogger("db")

settings = get_settings()
engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI dependency — request başına session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def wait_for_db(max_attempts: int = 15, delay: float = 2.0) -> None:
    """DB qalxana qədər gözlə (docker-compose-da backend db-dən tez başlaya bilər)."""
    for attempt in range(1, max_attempts + 1):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("DB bağlantısı hazırdır")
            return
        except OperationalError as exc:
            logger.warning("DB hazır deyil (%d/%d): %s", attempt, max_attempts, exc)
            time.sleep(delay)
    raise RuntimeError("DB bağlantısı qurulmadı")


def init_db() -> None:
    from . import models  # noqa: F401 — cədvəllərin qeydiyyatı üçün

    wait_for_db()
    Base.metadata.create_all(bind=engine)
