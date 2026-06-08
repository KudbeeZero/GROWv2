#!/usr/bin/env python3
"""Fail if the Alembic migration graph has more than one head.

A second head means two migrations share a parent (a fork). `alembic upgrade
head` then becomes ambiguous and CI/deploys break with a confusing error. A
real fork (at ``fbb8fceedacd``) was once caught only by manual testing — this
guard makes the check automatic and gives an actionable fix message.

Reads the migration scripts only (no database needed), so it is cheap and safe
to run anywhere. Run from the repo root: ``python scripts/check_single_head.py``.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    # Resolve script_location ("alembic") relative to the repo root regardless
    # of the caller's cwd, mirroring how CI invokes alembic.
    os.chdir(ROOT)
    cfg = Config(str(ROOT / "alembic.ini"))
    script = ScriptDirectory.from_config(cfg)
    heads = list(script.get_heads())

    if len(heads) == 1:
        print(f"[PASS] single Alembic head: {heads[0]}")
        return 0

    if not heads:
        print("[FAIL] no Alembic heads found — is alembic/versions populated?")
        return 1

    print(f"[FAIL] expected exactly one Alembic migration head, found {len(heads)}:")
    for h in heads:
        rev = script.get_revision(h)
        name = Path(rev.path).name if rev and rev.path else "?"
        print(f"  - {h}  ({name})")
    print(
        "\nMerge the fork with:\n"
        f'  alembic merge -m "merge heads" {" ".join(heads)}'
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
