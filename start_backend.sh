#!/bin/bash
set -euo pipefail

echo "Building backend image..."
docker compose --profile backend-only build --no-cache backend

echo "Starting backend and nginx..."
docker compose --profile backend-only up -d

echo "Waiting for backend to be ready..."
until docker compose --profile backend-only exec backend python -c "import socket; s=socket.create_connection(('localhost', 8000), timeout=2); s.close()" 2>/dev/null; do
    echo "  Backend not ready yet, retrying in 5s..."
    sleep 5
done

echo "Running migrations..."
docker compose --profile backend-only exec backend python /app/API_recommendme/manage.py migrate

echo ""
echo "API is running at http://188.166.155.92"
echo ""
echo "Services status:"
docker compose --profile backend-only ps
