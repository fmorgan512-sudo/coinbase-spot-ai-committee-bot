#!/bin/bash
# Debug script to diagnose Docker issues

echo "=================================="
echo "Docker Debug Information"
echo "=================================="
echo ""

echo "1. Checking Docker status..."
docker --version || echo "ERROR: Docker not installed!"
echo ""

echo "2. Container status:"
docker compose ps
echo ""

echo "3. Dashboard logs (last 50 lines):"
echo "---"
docker compose logs --tail=50 dashboard
echo ""

echo "4. Worker logs (last 50 lines):"
echo "---"
docker compose logs --tail=50 worker
echo ""

echo "5. Checking port 8501:"
netstat -tuln | grep 8501 || ss -tuln | grep 8501 || echo "Port check not available"
echo ""

echo "6. Checking .env file exists:"
if [ -f .env ]; then
    echo "✅ .env file exists"
    echo "Contents (API keys hidden):"
    grep -v "API_KEY\|PRIVATE_KEY" .env || echo "No non-sensitive vars"
else
    echo "❌ .env file missing! Run: cp .env.example .env"
fi
echo ""

echo "7. Checking data directory:"
ls -lh data/ 2>/dev/null || echo "No data directory yet"
echo ""

echo "=================================="
echo "Common Fixes:"
echo "=================================="
echo "1. Port in use:     docker compose down && docker compose up -d"
echo "2. Container crash: docker compose logs dashboard"
echo "3. Rebuild:         ./rebuild.sh"
echo "4. Reset all:       docker compose down -v && ./rebuild.sh"
echo ""
