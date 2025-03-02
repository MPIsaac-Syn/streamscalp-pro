# Base image (lightweight Python 3.10)
FROM python:3.10-slim

ENV PYTHONPATH=/app

# Install system dependencies (required for some Python packages)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Define build arguments with defaults
ARG INSTALL_ALPACA=false
ARG INSTALL_CCXT=false
ARG INSTALL_DEV=false
ARG INSTALL_BACKTRADER=false

# Copy requirements files first to leverage Docker layer caching
COPY ./requirements*.txt /app/

# Install dependencies in the correct order to avoid conflicts
RUN pip install --no-cache-dir --upgrade -r /app/requirements-base.txt && \
    if [ "$INSTALL_CCXT" = "true" ]; then \
        pip install --no-cache-dir --upgrade -r /app/requirements-ccxt.txt; \
    fi && \
    if [ "$INSTALL_ALPACA" = "true" ]; then \
        pip install --no-cache-dir --upgrade -r /app/requirements-alpaca.txt --no-deps; \
    fi && \
    if [ "$INSTALL_DEV" = "true" ]; then \
        pip install --no-cache-dir --upgrade -r /app/requirements-dev.txt; \
    fi && \
    if [ "$INSTALL_BACKTRADER" = "true" ]; then \
        pip install --no-cache-dir --upgrade -r /app/requirements-backtrader.txt; \
    fi

# Copy application code
COPY . /app

# Create logs directory
RUN mkdir -p /app/logs && chmod 777 /app/logs

# Expose the FastAPI dashboard port
EXPOSE 8000

# Run the application (FastAPI dashboard backend)
CMD ["uvicorn", "dashboard.backend.main:app", "--host", "0.0.0.0", "--port", "8000"]