#!/usr/bin/sh
# shebang

cd "$(dirname "$0")"  # Change to the directory containing the script
echo "Current directory: $(pwd)"

# Debug output
echo "Argument provided: $1"

# Check for the '--nobuild' argument
if [ "$1" = "--nobuild" ]; then # you can run ./docker/docker-build.sh --nobuild
    echo "Running without build"
    docker compose -f ./docker-compose.yml up -d
else
    echo "Running with build"
    docker compose -f ./docker-compose.yml up -d --build
fi
