"""
Time abstraction so the simulation never calls datetime.now() directly — tests
inject a FrozenClock they can advance deterministically.
"""

from datetime import datetime, timedelta
from typing import Protocol


class Clock(Protocol):
    def now(self) -> datetime:  # pragma: no cover - protocol
        ...


class SystemClock:
    """Real wall-clock (UTC)."""

    def now(self) -> datetime:
        return datetime.utcnow()


class FrozenClock:
    """A controllable clock for tests/simulations."""

    def __init__(self, start: datetime):
        self._now = start

    def now(self) -> datetime:
        return self._now

    def advance(self, **kwargs) -> datetime:
        """Advance by a timedelta (e.g. advance(hours=3, days=1))."""
        self._now = self._now + timedelta(**kwargs)
        return self._now

    def set(self, when: datetime) -> None:
        self._now = when
