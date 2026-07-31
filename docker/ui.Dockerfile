# Description: Dockerfile for Streamlit presentation UI
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git ffmpeg libsm6 libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Copy uv binaries
COPY --from=ghcr.io/astral-sh/uv:0.7.8 /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Copy dependency specifications first for Docker layer caching
COPY pyproject.toml uv.lock* ./

# Install dependencies system-wide
RUN uv pip install -r pyproject.toml --system --extra cpu

# Copy source files
COPY . .

EXPOSE 8501

ENV PYTHONUNBUFFERED=1

CMD ["streamlit", "run", "src/presentation/ui/app_ui.py", "--server.address", "0.0.0.0", "--server.port", "8501"]
