"""
Engine / session management.

Exposes a process-wide engine + sessionmaker bound to the configured
DATABASE_URL, plus a `session_scope` context manager that commits on success and
rolls back on error.
"""

from contextlib import contextmanager
from typing import Iterator, Optional

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from ..config import get_settings
from .base import Base

_engine: Optional[Engine] = None
_SessionLocal: Optional[sessionmaker] = None


def get_engine() -> Engine:
    """Return (creating on first use) the global SQLAlchemy engine."""
    global _engine
    if _engine is None:
        settings = get_settings()
        connect_args = {}
        if settings.database_url.startswith("sqlite"):
            # Allow cross-thread use under Flask's dev server.
            connect_args["check_same_thread"] = False
        _engine = create_engine(
            settings.database_url,
            echo=settings.sql_echo,
            future=True,
            connect_args=connect_args,
        )
    return _engine


def get_sessionmaker() -> sessionmaker:
    """Return (creating on first use) the global sessionmaker."""
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(
            bind=get_engine(), autoflush=False, expire_on_commit=False, future=True
        )
    return _SessionLocal


def init_db() -> None:
    """Create all tables from the ORM metadata (used by tests / first boot).

    Production uses Alembic migrations; this is a convenience for SQLite and
    fresh local databases.
    """
    # Import models so their tables register on Base.metadata.
    from . import models  # noqa: F401

    Base.metadata.create_all(bind=get_engine())


@contextmanager
def session_scope() -> Iterator[Session]:
    """Transactional session scope: commit on success, rollback on exception."""
    session = get_sessionmaker()()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def reset_engine_for_tests(database_url: str) -> None:
    """Rebind the engine to a specific URL (test helper)."""
    global _engine, _SessionLocal
    if _engine is not None:
        _engine.dispose()
    _engine = create_engine(
        database_url,
        future=True,
        connect_args={"check_same_thread": False}
        if database_url.startswith("sqlite")
        else {},
    )
    _SessionLocal = sessionmaker(
        bind=_engine, autoflush=False, expire_on_commit=False, future=True
    )
