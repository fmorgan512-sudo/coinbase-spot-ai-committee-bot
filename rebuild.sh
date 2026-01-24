#!/bin/bash
# Docker rebuild script - fixes cache issues

echo "Stopping and removing old containers..."
docker compose down

echo "Removing old images..."
docker compose rm -f
docker rmi coinbase-spot-ai-committee-bot-worker coinbase-spot-ai-committee-bot-dashboard 2>/dev/null || true

echo "Cleaning build cache..."
docker builder prune -f

echo "Rebuilding without cache..."
docker compose build --no-cache

echo "Starting fresh containers..."
docker compose up -d

echo ""
echo "✅ Done! Check logs with: docker compose logs -f"
