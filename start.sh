#!/bin/bash
# Start script for Railway deployment

set -e  # Exit on error

# Set default PORT if not provided
export PORT=${PORT:-8000}

echo "Starting Telegram SMS Bot on port $PORT..."
echo "Environment: ${ENVIRONMENT:-production}"

# Run database migrations if needed (uncomment if using alembic)
# alembic upgrade head

# Start the application
exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT"
