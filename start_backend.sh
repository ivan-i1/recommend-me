#!/bin/bash
set -euo pipefail

echo "Starting backend..."
docker compose --profile backend-only up -d backend

echo "Waiting for backend to start..."
sleep 5
docker compose --profile backend-only exec backend python API_recommendme/manage.py migrate

echo "API is running."
