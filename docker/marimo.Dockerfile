# Description: Dockerfile for serving Marimo interactive notebook web application
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy uv binaries from official astral-sh image
COPY --from=ghcr.io/astral-sh/uv:0.7.8 /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Copy dependency specifications first to leverage Docker layer caching
COPY pyproject.toml uv.lock* ./

# Install dependencies system-wide (cached unless pyproject.toml/uv.lock changes)
RUN uv pip install -r pyproject.toml --system --extra cpu

# Copy application source code after dependency installation
COPY . .

# Unbuffered python logs
ENV PYTHONUNBUFFERED=1

# Serve Marimo notebook as a web app
CMD ["marimo", "run", "notebooks/explore_marimo.py", "--host", "0.0.0.0", "--port", "2718"]
