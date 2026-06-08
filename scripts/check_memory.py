#!/usr/bin/env python3
"""Memory-integrity checker — keeps the Markdown memory layer honest.

The memory system's whole premise is "the docs can never lie again." This script
makes that enforceable instead of aspirational. It fails (exit 1) if:

  1. links      — any relative Markdown link under docs/memory (or CLAUDE.md)
                  points at a file that doesn't exist.
  2. citations  — any "✅ built" claim in the Design Codex cites a repo path
                  (a backtick token containing "/", e.g. `services/game_service.py`)
                  that doesn't resolve. Bare filenames like `engine.py` are
                  ambiguous and skipped — we optimise for precision so the gate
                  never cries wolf.
  3. structure  — a required memory file is missing, or the Design Codex isn't
                  referenced from the always-loaded layer-map files.

Pure standard library so it runs in CI with no extra install.
Run locally with `make check-memory` (or `python scripts/check_memory.py`).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import List

ROOT = Path(__file__).resolve().parents[1]
MEMORY = ROOT / "docs" / "memory"
CLAUDE_MD = ROOT / "CLAUDE.md"

LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
BACKTICK_RE = re.compile(r"`([^`]+)`")
# A backtick token we treat as a checkable repo path: has a "/", ends in a known
# extension, optionally followed by ":<line>" or ":<symbol>".
PATH_LIKE_RE = re.compile(r"^[A-Za-z0-9_./-]+/[A-Za-z0-9_./-]+\.(py|ya?ml|md)(:[\w-]+)?$")

# Files the memory system must always have.
REQUIRED = [
    CLAUDE_MD,
    MEMORY / "README.md",
    MEMORY / "MAP.md",
    MEMORY / "ARCHITECTURE.md",
    MEMORY / "DECISIONS.md",
    MEMORY / "BACKLOG.md",
    MEMORY / "design" / "README.md",
]


def _rel(p: Path) -> str:
    return str(p.resolve().relative_to(ROOT))


def _md_files() -> List[Path]:
    files = sorted(MEMORY.rglob("*.md"))
    if CLAUDE_MD.exists():
        files.append(CLAUDE_MD)
    return files


def check_links() -> List[str]:
    errors: List[str] = []
    for f in _md_files():
        for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            for m in LINK_RE.finditer(line):
                link = m.group(1).split("#")[0].split()[0].strip() if m.group(1).strip() else ""
                if not link or link.startswith(("http://", "https://", "mailto:")):
                    continue
                if not (f.parent / link).resolve().exists():
                    errors.append(f"{_rel(f)}:{n}: broken link -> {link}")
    return errors


def _resolves(token: str) -> bool:
    base = token.split(":")[0]
    candidates = (ROOT / base, ROOT / "src" / base, ROOT / "src" / "growpodempire" / base)
    return any(c.exists() for c in candidates)


def check_citations() -> List[str]:
    errors: List[str] = []
    design = MEMORY / "design"
    for f in sorted(design.rglob("*.md")):
        for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            if "✅" not in line:
                continue
            for tok in BACKTICK_RE.findall(line):
                tok = tok.strip()
                if PATH_LIKE_RE.match(tok) and not _resolves(tok):
                    errors.append(f"{_rel(f)}:{n}: ✅ cites missing path -> {tok}")
    return errors


def check_structure() -> List[str]:
    errors: List[str] = []
    for f in REQUIRED:
        if not f.exists():
            errors.append(f"missing required memory file -> {_rel(f)}")
    # The Design Codex must be discoverable from the always-loaded layer map.
    for f in (CLAUDE_MD, MEMORY / "README.md"):
        if f.exists() and "design/" not in f.read_text(encoding="utf-8"):
            errors.append(f"{_rel(f)}: does not reference the Design Codex (docs/memory/design/)")
    return errors


def main() -> int:
    checks = (
        ("links", check_links),
        ("citations", check_citations),
        ("structure", check_structure),
    )
    all_errors: List[str] = []
    for name, fn in checks:
        errs = fn()
        print(f"[{'PASS' if not errs else 'FAIL'}] {name}: {'ok' if not errs else f'{len(errs)} problem(s)'}")
        all_errors.extend(errs)

    if all_errors:
        print("\nMemory-integrity check FAILED:")
        for e in all_errors:
            print(f"  - {e}")
        return 1
    print("\nMemory integrity OK — links resolve, ✅ claims cite real paths, structure intact.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
