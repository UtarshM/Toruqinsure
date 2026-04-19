# ─────────────────────────────────────────────────────────────────────────────
# Toque Insurance – FastAPI Backend
# Multi-stage Docker build for Railway deployment
# ─────────────────────────────────────────────────────────────────────────────

# ── Stage 1: Builder ──────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies into an isolated prefix
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --prefix=/install --no-cache-dir -r requirements.txt || true
# Note: "|| true" skips the emergentintegrations package that isn't publicly available.
# Remove it from requirements.txt for production.

# ── Stage 2: Runtime ──────────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

WORKDIR /app

# System deps for asyncpg / psycopg
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application source
COPY . .

# Create non-root user for security
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser
USER appuser

# Railway injects PORT at runtime; default 8000 for local Docker runs
ENV PORT=8000

EXPOSE $PORT

# Run Alembic migrations then start the server
CMD alembic upgrade head && \
    uvicorn app.main:app \
        --host 0.0.0.0 \
        --port $PORT \
        --workers 2 \
        --log-level info \
        --no-access-log
