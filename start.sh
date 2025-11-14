#!/bin/bash
# Start script for Railway deployment

# Set default PORT if not provided
export PORT=${PORT:-8000}

echo "Starting Telegram SMS Bot on port $PORT..."

# Run uvicorn with the PORT variable properly expanded
uvicorn app.main:app --host 0.0.0.0 --port "$PORT"
