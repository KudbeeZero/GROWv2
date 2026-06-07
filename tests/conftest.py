"""
Shared pytest fixtures.

Each test that needs persistence gets an isolated, freshly-seeded SQLite
database file so tests never bleed into one another.
"""

import os
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from growpodempire.db.session import reset_engine_for_tests, init_db, session_scope  # noqa: E402
from growpodempire.db.seed import seed_strains  # noqa: E402
from growpodempire.services.game_service import GameService  # noqa: E402


@pytest.fixture()
def db(tmp_path):
    """Bind the global engine to a throwaway SQLite file, create schema + seed."""
    db_path = tmp_path / "test.db"
    reset_engine_for_tests(f"sqlite:///{db_path}")
    init_db()
    seed_strains()
    yield


@pytest.fixture()
def session(db):
    """A transactional session scope for direct ORM access in tests."""
    with session_scope() as s:
        yield s


@pytest.fixture()
def service(db):
    """A GameService bound to its own committing session per call site."""
    with session_scope() as s:
        yield GameService(s)
