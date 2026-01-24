#!/bin/bash
set -e

echo "=================================="
echo "Coinbase AI Bot - Quick Deploy"
echo "=================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Docker not found. Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    echo "Docker installed successfully!"
fi

# Check if .env exists
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file with your configuration"
    echo "Run: nano .env"
    echo ""
    read -p "Press Enter to continue after editing .env..."
fi

# Create data directory
mkdir -p data

# Build and start services
echo ""
echo "Building Docker images..."
docker compose build

echo ""
echo "Starting services..."
docker compose up -d

echo ""
echo "=================================="
echo "✅ Deployment Complete!"
echo "=================================="
echo ""
echo "Dashboard URL: http://localhost:8501"
echo ""
echo "Useful commands:"
echo "  View logs:     docker compose logs -f"
echo "  Stop services: docker compose down"
echo "  Restart:       docker compose restart"
echo ""
echo "🔐 Configure your API keys through the dashboard"
echo "   Navigate to: Settings tab → API Keys & Settings"
echo ""
