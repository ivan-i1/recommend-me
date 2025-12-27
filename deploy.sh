#!/bin/bash
set -e

echo "Start deploying..."

docker compose down
docker compose build
docker compose up -d mysql

echo "Waiting MySQL..."
sleep 60

docker compose run --rm data

echo "Filling Database"