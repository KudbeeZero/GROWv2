"""Optional SITE_PASSWORD gate for private/staging deployments."""

import base64
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


def _basic(pw: str) -> dict:
    raw = base64.b64encode(f"user:{pw}".encode()).decode()
    return {"Authorization": f"Basic {raw}"}


def _app_with_password(pw):
    from growpodempire.config import get_settings
    from growpodempire.api.flask_api import create_app

    get_settings.cache_clear()
    return create_app(init_database=False)


def test_gate_blocks_without_password(monkeypatch):
    monkeypatch.setenv("SITE_PASSWORD", "letmein")
    from growpodempire.config import get_settings

    try:
        app = _app_with_password("letmein")
        c = app.test_client()
        assert c.get("/").status_code == 401                       # gated
        assert c.get("/health").status_code == 200                 # probe stays open
        assert c.get("/", headers=_basic("wrong")).status_code == 401
        assert c.get("/", headers=_basic("letmein")).status_code == 200
    finally:
        get_settings.cache_clear()  # don't leak the gate into other tests


def test_no_gate_when_unset(monkeypatch):
    monkeypatch.delenv("SITE_PASSWORD", raising=False)
    from growpodempire.config import get_settings

    try:
        get_settings.cache_clear()
        app = create_app_unset = __import__(
            "growpodempire.api.flask_api", fromlist=["create_app"]
        ).create_app(init_database=False)
        c = app.test_client()
        assert c.get("/").status_code == 200  # open by default
    finally:
        get_settings.cache_clear()
