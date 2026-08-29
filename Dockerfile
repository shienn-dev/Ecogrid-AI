FROM python:3.11-slim

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

COPY backend ./backend
COPY frontend ./frontend
COPY .env.example ./.env.example

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    HOST=0.0.0.0 \
    PORT=5000 \
    FLASK_DEBUG=false \
    DATABASE_URL=sqlite:///database/energy.db

EXPOSE 5000

# Ensure DB dir exists (match Flask-SQLAlchemy relative to backend/)
RUN mkdir -p backend/database database

CMD ["gunicorn", "--config", "gunicorn.conf.py", "backend.app:create_app()"]
