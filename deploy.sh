#!/bin/bash
set -e

echo "Start deploying..."

docker compose down -v
docker compose build
docker compose up -d mysql

echo "Waiting MySQL..."
sleep 60

docker compose up --build data

echo "Filling Database"