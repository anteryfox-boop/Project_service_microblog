#!/bin/bash
set -e

echo "Waiting for PostgreSQL..."
while ! nc -z postgres_db 5432; do
  sleep 1
done
echo "PostgreSQL is up!"

echo "Initializing database..."
python init_db.py

echo "Seeding database..."
python seed_db.py

echo "Starting application..."
exec "$@"