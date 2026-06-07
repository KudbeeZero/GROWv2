#!/bin/bash
# GROWv2 SessionStart hook — installs deps so tests/linters work in Claude Code
# on the web. Runs synchronously: the session waits until deps are ready (no
# race where the agent runs pytest before the install finishes).
set -euo pipefail

# Only needed in the remote (web) environment. Local devs use `make setup`
# (a venv), which avoids the system-package collision handled below.
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "$CLAUDE_PROJECT_DIR"

# pip itself is Debian-managed here and can't be uninstalled, so an upgrade is
# best-effort — never let it abort the install.
python -m pip install --upgrade pip || true

# The base image ships a Debian-managed PyYAML that pip cannot uninstall
# ("Cannot uninstall PyYAML 6.0.1, RECORD file not found"). --ignore-installed
# PyYAML installs the pinned wheel over it without trying to remove it, so the
# rest of the requirements resolve cleanly.
pip install --ignore-installed PyYAML -r requirements.txt -r requirements-dev.txt ruff

# Make `import growpodempire` work via the source tree, exactly like CI
# (env: PYTHONPATH=src). We deliberately avoid `pip install -e .` here: the
# base image's Debian-patched setuptools breaks the legacy editable build
# ("AttributeError: install_layout"). PYTHONPATH needs no build step.
echo 'export PYTHONPATH="src"' >> "$CLAUDE_ENV_FILE"
