# Coinbase Spot AI Committee Bot (OpenAI + Claude)

⚠️ **WARNING**
- This is an experimental trading system. Use at your own risk.
- Default mode is DRY_RUN=true (no orders will be placed).
- Fully autonomous trading requires strict risk controls and careful testing.

## What it does
- Polls Coinbase Advanced Trade API (v3) for balances/orders/fills.
- Computes a minimal realized PnL placeholder (fees-based until you implement proper accounting).
- Runs an AI "committee" (OpenAI + Claude) only on triggers / schedule to minimize LLM calls.
- Applies only actions that:
  1) BOTH models agree on, and
  2) pass deterministic risk validation.

## Requirements
- Docker + Docker Compose (recommended)
- OR Python 3.11+ with pip

## Quick Start

### Option 1: Docker (Recommended)
```bash
# Clone repository
git clone https://github.com/fmorgan512-sudo/coinbase-spot-ai-committee-bot.git
cd coinbase-spot-ai-committee-bot

# Quick deploy
chmod +x deploy.sh
./deploy.sh

# Or manually:
cp .env.example .env
nano .env  # Configure your settings
docker compose up -d
```

### Option 2: Python Direct
```bash
# Install dependencies
pip install -r app/requirements.txt

# Configure environment
cp .env.example .env
nano .env

# Run dashboard
streamlit run app/dashboard.py --server.port=8501

# In another terminal, run worker
python3 -m app.worker
```

## Configuration

1. Copy `.env.example` to `.env`
2. Fill in your API credentials:
   - `COINBASE_API_KEY_NAME` - Your Coinbase CDP API key name
   - `COINBASE_API_PRIVATE_KEY_PEM` - Your Coinbase private key (PEM format)
   - `OPENAI_API_KEY` - Your OpenAI API key
   - `ANTHROPIC_API_KEY` - Your Anthropic/Claude API key

**Note:** Coinbase uses JWT Bearer auth for Advanced Trade endpoints. See [Coinbase CDP docs](https://docs.cdp.coinbase.com/).

Alternatively, configure API keys through the dashboard at http://localhost:8501 → Settings tab.

## Dashboard Access

Open http://localhost:8501 to view the Streamlit dashboard.

### Dashboard Tabs
- **Performance**: Realized PnL, equity curve
- **Positions**: Balances, current exposure, open orders
- **AI Committee**: Latest recommendations from OpenAI + Claude, agreement/consensus
- **Actions**: Action logs and execution history
- **Settings**: API keys management and configuration

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed hosting instructions including:
- Railway.app (easiest, 5 minutes)
- DigitalOcean/AWS/GCP (production-ready)
- Local/Raspberry Pi (home server)
- Docker production setup

### Quick Deploy to Cloud:

**Railway.app** (recommended for beginners):
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

**DigitalOcean Droplet**:
```bash
ssh root@your-droplet-ip
curl -fsSL https://get.docker.com | sh
git clone https://github.com/fmorgan512-sudo/coinbase-spot-ai-committee-bot.git
cd coinbase-spot-ai-committee-bot
./deploy.sh
```

## Safety Features
- DRY_RUN mode by default
- Max daily loss circuit breaker
- Max position size limits
- Max trades per hour limit
- Both AI models must agree on actions
- Deterministic risk validator as final gate
