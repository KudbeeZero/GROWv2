"""
Environment-driven configuration for GrowPodEmpire.

Reads from process env (and a local .env via python-dotenv) so the same code
runs against SQLite locally/in tests and Postgres on Render. No secrets are
hardcoded here.
"""

import os
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()  # no-op if .env is absent

# Package root, used to locate bundled data files (balance / strain catalog).
PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(PACKAGE_DIR, "data")


class Settings:
    """Lightweight settings object sourced from environment variables."""

    def __init__(self) -> None:
        # Default to a local SQLite file; Render injects a Postgres DATABASE_URL.
        self.database_url: str = os.environ.get(
            "DATABASE_URL", "sqlite:///growpod.db"
        )
        # SQLAlchemy historically used the "postgres://" scheme; normalise it.
        if self.database_url.startswith("postgres://"):
            self.database_url = self.database_url.replace(
                "postgres://", "postgresql://", 1
            )

        self.balance_file: str = os.environ.get(
            "BALANCE_FILE", os.path.join(DATA_DIR, "balance.yaml")
        )
        self.strains_file: str = os.environ.get(
            "STRAINS_FILE", os.path.join(DATA_DIR, "strains.yaml")
        )

        # Optional global RNG seed for reproducible breeding in deterministic
        # contexts (tests / demos). When None, breeding draws a fresh seed.
        seed = os.environ.get("RNG_SEED")
        self.rng_seed = int(seed) if seed not in (None, "") else None

        self.sql_echo: bool = os.environ.get("SQL_ECHO", "false").lower() == "true"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()
