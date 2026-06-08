#!/usr/bin/env bash
# Start the Flask backend with a fresh SQLite DB for Playwright e2e tests.
# Safe to call from any directory — it always cds to the project root.
set -euo pipefail

cd "$(dirname "$0")/.."

export PYTHONPATH=src
export DATABASE_URL="sqlite:///e2e_test.db"
export USE_MOCK_AI=true
export USE_MOCK_CHAIN=true
export RATELIMIT_ENABLED=false
export CORS_ALLOWED_ORIGINS=http://localhost:3000
export PORT=10000

rm -f e2e_test.db
python -m alembic upgrade head
python -m growpodempire.db.seed

exec python server.py
