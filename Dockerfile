# GrowPodEmpire API image.
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/src \
    PORT=10000

WORKDIR /app

# Install dependencies first for better layer caching.
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 10000

# Apply migrations + seed, then serve with gunicorn (server.py exposes `app`).
CMD ["sh", "-c", "alembic upgrade head && python -m growpodempire.db.seed && gunicorn -b 0.0.0.0:${PORT} -w 2 server:app"]
