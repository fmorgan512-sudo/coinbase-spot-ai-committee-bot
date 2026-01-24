#!/bin/bash
# Fix common Docker issues

set -e

echo "🔧 Fixing common Docker issues..."
echo ""

# Stop old containers
echo "1. Stopping existing containers..."
docker compose down 2>/dev/null || true

# Kill anything on port 8501
echo "2. Freeing port 8501..."
lsof -ti:8501 | xargs kill -9 2>/dev/null || true

# Remove old containers and images
echo "3. Cleaning up old containers..."
docker compose rm -f 2>/dev/null || true

# Create required directories
echo "4. Creating required directories..."
mkdir -p data
chmod 777 data

# Check .env exists
echo "5. Checking configuration..."
if [ ! -f .env ]; then
    echo "   Creating .env from template..."
    cp .env.example .env
    echo "   ⚠️  EDIT .env file before continuing!"
    echo "   Run: nano .env"
    exit 1
fi

# Rebuild without cache
echo "6. Rebuilding images (this may take a few minutes)..."
docker compose build --no-cache

# Start services
echo "7. Starting services..."
docker compose up -d

# Wait for startup
echo "8. Waiting for services to start..."
sleep 5

# Show status
echo ""
echo "=================================="
echo "✅ Services Started"
echo "=================================="
docker compose ps
echo ""

# Show logs
echo "Dashboard logs:"
docker compose logs --tail=20 dashboard
echo ""

echo "=================================="
echo "🌐 Dashboard URL: http://localhost:8501"
echo ""
echo "Useful commands:"
echo "  View logs:    docker compose logs -f"
echo "  Restart:      docker compose restart"
echo "  Stop:         docker compose down"
echo "  Full debug:   ./debug.sh"
echo "=================================="
