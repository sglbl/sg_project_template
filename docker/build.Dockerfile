# Description: Dockerfile for building the image with python light version and uv
FROM python:3.10.12-slim
# Install git to clone the repository 
RUN apt-get update && apt-get install git ffmpeg libsm6 libxext6 -y
# Copy the uv and uvx binaries from the uv package manager image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
# Set the working directory
WORKDIR /app
# Copy files to the working directory [except the files mentioned in .dockerignore]
COPY . .
# Install the dependencies from the pyproject.toml file on system-wide
RUN uv pip install -r pyproject.toml --system --no-cache-dir --extra cpu
# Expose the port 8000
EXPOSE 8000
# Set this environment variable to see the print statements in the logs
ENV PYTHONUNBUFFERED=1
# Run the main module from the source
CMD ["python3", "-m", "src.main"]
