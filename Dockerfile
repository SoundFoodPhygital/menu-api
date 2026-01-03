# syntax=docker/dockerfile:1

# -------------------------------------------
# Production stage
# -------------------------------------------
FROM python:3.11-slim AS production

# Prevent Python from writing pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Create non-root user for security
RUN adduser --disabled-password --gecos '' appuser

# Copy application code
COPY --chown=appuser:appuser . .

# Create instance directory for SQLite database
RUN mkdir -p instance && chown appuser:appuser instance

# Switch to non-root user
USER appuser

# Set environment variables
ENV FLASK_ENV=production
ENV FLASK_APP=wsgi.py

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/auth/login || exit 1

# Run with gunicorn
CMD ["python", "-m", "gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "wsgi:app"]

# -------------------------------------------
# Development stage
# -------------------------------------------
FROM python:3.11-slim AS development

# Prevent Python from writing pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies (includes dev deps in requirements.txt)
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create instance directory for SQLite database
RUN mkdir -p instance

ENV FLASK_ENV=development
ENV FLASK_APP=wsgi.py
ENV FLASK_DEBUG=1

EXPOSE 5000

CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000", "--debug"]
