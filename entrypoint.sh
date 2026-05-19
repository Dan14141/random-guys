#!/usr/bin/env sh
set -e

# Ждём, пока PostgreSQL станет доступен
echo "Waiting for PostgreSQL at $POSTGRES_HOST:$POSTGRES_PORT..."
until python -c "import socket; s=socket.socket(); s.settimeout(2); s.connect(('$POSTGRES_HOST', int('$POSTGRES_PORT'))); s.close()" 2>/dev/null; do
    sleep 1
done
echo "PostgreSQL is up."

echo "Applying migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput || true

echo "Loading initial guys from API (skipped if DB already has guys)..."
python manage.py load_initial_guys || true

echo "Starting Gunicorn..."
exec gunicorn core.wsgi:application --bind 0.0.0.0:8000 --workers 3
