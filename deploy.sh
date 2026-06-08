#!/bin/bash
set -e

echo "Start deploying..."

docker system prune -f
docker compose down -v
docker compose build
docker compose up -d mysql

echo "Waiting MySQL..."
sleep 60

echo "Filling Database"

#docker compose up --build data
docker compose --profile data-only up --build data

echo "Filled Database"
sleep 5

#docker compose up --build Backend

docker compose --profile backend-only up --build -d backend
docker compose --profile backend-only exec backend python API_recommendme/manage.py migrate

echo "API Running"