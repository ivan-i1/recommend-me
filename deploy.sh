#!/bin/bash
set -euo pipefail

echo "Starting full deploy from scratch..."

# Confirmation prompt to avoid accidental data loss
read -p "WARNING: This will DELETE the current database and all data. Continue? [y/N] " confirm
if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
    echo "Deploy cancelled."
    exit 0
fi

# Remove containers, networks, and volumes (wipes DB)
echo "Cleaning up containers and volumes..."
docker system prune -f
docker compose down -v

# Build all images — --no-cache ensures latest code is always picked up
echo "Building images..."
docker compose build --no-cache mysql
docker compose --profile data-only build --no-cache data

# Start MySQL
echo "Starting MySQL..."
docker compose up -d mysql

# Wait until MySQL is actually healthy instead of a fixed sleep
echo "Waiting for MySQL to be ready..."
until docker compose exec mysql mysqladmin ping -h localhost --silent 2>/dev/null; do
    echo "  MySQL not ready yet, retrying in 5s..."
    sleep 5
done
echo "MySQL is ready."

# Fill the database — runs genres, regions, providers, movies, vectors
echo "Filling database (this may take a while)..."
docker compose --profile data-only run --rm data python fill_movie_db.py

# Fill actors and directors tables
echo "Filling actors and directors..."
docker compose --profile data-only run --rm data python fill_actors_directors_db.py

echo "Database filled. Run start_backend.sh to start the API."
