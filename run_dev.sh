#!/usr/bin/env bash
set -e

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"

echo "Starting backend services..."
cd "$REPO_ROOT/backend"
docker-compose up --build -d

echo "Waiting for backend health check..."
until curl -sf http://localhost:8080/health > /dev/null 2>&1; do
  sleep 1
done
echo "Backend is healthy!"

cd "$REPO_ROOT/frontend"
if [ ! -f .env.local ]; then
  cp .env.local.template .env.local
  echo "Created frontend/.env.local from template"
fi

echo "Installing frontend dependencies..."
npm install

if [ ! -d ios ] || [ ! -d android ]; then
  echo "Running Expo prebuild..."
  npx expo prebuild --clean
else
  echo "Native directories exist, skipping prebuild (run 'npx expo prebuild --clean' manually if needed)"
fi

echo "Starting Expo dev server (development build)..."
npx expo run:ios
