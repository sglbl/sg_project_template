# Description: Dockerfile for core application services (Streamlit UI, FastAPI REST API)
FROM python:3.12-slim

# Install uv binary from official Astral image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install system runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git ffmpeg libsm6 libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Set application working directory and uv environment
WORKDIR /app

ENV UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

# Optimization: Intermediate Layer Caching via Bind Mounts & --no-install-project
# 1. --mount=type=bind mounts pyproject.toml & uv.lock directly into the layer without explicit COPY commands.
# 2. --no-install-project installs all heavy static dependencies into /app/.venv without project source code.
# 3. When application source code in src/ changes, Docker hits CACHED (0.0s) for this heavy installation step.
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --extra cpu --group mlops

# Copy application source code into the container image
COPY . /app

# Fast final sync: Registers local workspace project into .venv (completes in ~0.4s)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --extra cpu --group mlops

EXPOSE 8501

CMD ["streamlit", "run", "src/presentation/ui/app_ui.py", "--server.address", "0.0.0.0", "--server.port", "8501"]
