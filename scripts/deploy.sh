#!/bin/bash

set -e

APP_DIR="/home/ubuntu/ai-job-intelligence"

echo "Starting deployment..."

cd "$APP_DIR"

echo "Fetching latest code..."
git -c safe.directory="$APP_DIR" fetch origin main

echo "Resetting to latest main..."
git -c safe.directory="$APP_DIR" reset --hard origin/main

echo "Building backend image..."
docker build -t ai-job-intelligence-backend .

echo "Building frontend image..."
docker build \
  --build-arg VITE_API_BASE_URL=/api/v1 \
  -t ai-job-intelligence-frontend \
  ./frontend

echo "Starting application..."
docker compose -f docker-compose.prod.yml up -d

echo "Cleaning unused Docker resources..."
docker image prune -f

echo "Checking containers..."
docker compose -f docker-compose.prod.yml ps

echo "Deployment completed successfully."