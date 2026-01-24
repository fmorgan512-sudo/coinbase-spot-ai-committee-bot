# Deployment Guide

## Option 1: Railway.app (Easiest - 5 minutes)

1. Sign up at [railway.app](https://railway.app)
2. Click "New Project" → "Deploy from GitHub"
3. Select this repository
4. Railway will auto-detect Docker setup
5. Add environment variables in Railway dashboard
6. Deploy! Your app will be live at `yourapp.railway.app`

**Pros:** Zero config, automatic HTTPS, built-in monitoring
**Cons:** ~$5-10/month minimum

---

## Option 2: DigitalOcean Droplet (Recommended)

### Step 1: Create Droplet
- Size: Basic ($6/mo with 1GB RAM is enough)
- Image: Ubuntu 22.04 LTS
- Enable monitoring

### Step 2: Initial Setup
```bash
# SSH into droplet
ssh root@your-droplet-ip

# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose (if not included)
apt install docker-compose-plugin -y
```

### Step 3: Deploy Bot
```bash
# Clone repository
git clone https://github.com/fmorgan512-sudo/coinbase-spot-ai-committee-bot.git
cd coinbase-spot-ai-committee-bot

# Setup environment
cp .env.example .env
nano .env  # Configure your settings

# Create data directory
mkdir -p data

# Start services
docker compose -f docker-compose.prod.yml up -d

# Check status
docker compose ps
docker compose logs -f
```

### Step 4: Access Dashboard
- Navigate to: `http://your-droplet-ip:8501`
- Configure API keys through the web interface

### Step 5: Enable Firewall
```bash
ufw allow 22/tcp   # SSH
ufw allow 8501/tcp # Dashboard
ufw enable
```

---

## Option 3: AWS EC2 (Enterprise)

### Launch Instance:
1. AMI: Ubuntu Server 22.04 LTS
2. Instance Type: t3.micro (free tier eligible)
3. Security Group: Allow ports 22, 8501

### Deploy:
```bash
# Connect to instance
ssh -i your-key.pem ubuntu@ec2-instance-ip

# Follow same steps as DigitalOcean above
```

---

## Option 4: Local Server / Raspberry Pi

### Requirements:
- Always-on computer or Raspberry Pi 4 (4GB+ RAM)
- Ubuntu/Debian OS
- Stable internet connection

### Setup:
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Clone and run
git clone https://github.com/fmorgan512-sudo/coinbase-spot-ai-committee-bot.git
cd coinbase-spot-ai-committee-bot
cp .env.example .env
nano .env

# Run
docker compose up -d
```

### Access Locally:
- Dashboard: `http://localhost:8501`
- Or from network: `http://192.168.1.xxx:8501`

### Make Accessible from Internet (Optional):
Use **ngrok** for quick testing:
```bash
# Install ngrok
snap install ngrok

# Expose dashboard
ngrok http 8501
# You'll get a public URL like: https://abc123.ngrok.io
```

---

## Option 5: Heroku (Budget-Friendly)

**Note:** Heroku no longer has a free tier, but starts at $5/month.

### Setup:
```bash
# Install Heroku CLI
curl https://cli-assets.heroku.com/install.sh | sh

# Login
heroku login

# Create app
heroku create your-bot-name

# Add config vars (equivalent to .env)
heroku config:set DRY_RUN=true
heroku config:set DB_PATH=/app/data/bot.sqlite3
# ... add other vars

# Deploy
git push heroku main

# Scale services
heroku ps:scale worker=1 dashboard=1
```

---

## Security Best Practices

### 1. Enable HTTPS (Production)
```bash
# Install certbot
apt install certbot python3-certbot-nginx -y

# Get SSL certificate (requires domain name)
certbot --nginx -d yourdomain.com
```

### 2. Secure Environment Variables
```bash
# Never commit .env file
echo ".env" >> .gitignore

# Use strong passwords for key encryption
# Minimum 16 characters, mix of letters/numbers/symbols
```

### 3. Firewall Rules
```bash
# Only allow necessary ports
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp   # SSH
ufw allow 8501/tcp # Dashboard (or 80/443 if using nginx)
ufw enable
```

### 4. Regular Updates
```bash
# Update bot
cd coinbase-spot-ai-committee-bot
git pull
docker compose down
docker compose up -d --build

# Update system
apt update && apt upgrade -y
```

---

## Monitoring & Maintenance

### View Logs:
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f worker
docker compose logs -f dashboard

# Last 100 lines
docker compose logs --tail=100
```

### Restart Services:
```bash
docker compose restart worker
docker compose restart dashboard
```

### Stop Services:
```bash
docker compose down
```

### Backup Database:
```bash
# Backup
cp data/bot.sqlite3 data/bot.sqlite3.backup-$(date +%Y%m%d)

# Restore
cp data/bot.sqlite3.backup-20260124 data/bot.sqlite3
```

---

## Cost Comparison

| Solution | Monthly Cost | Setup Time | Difficulty |
|----------|--------------|------------|------------|
| Local/Raspberry Pi | $0 (electricity) | 15 min | Easy |
| Railway.app | $5-10 | 5 min | Very Easy |
| DigitalOcean | $6 | 20 min | Easy |
| Hetzner | $4 | 20 min | Easy |
| AWS EC2 (t3.micro) | $8-15 | 30 min | Medium |
| Heroku | $7+ | 15 min | Easy |

---

## Recommended Setup for Different Users

### **Hobbyist / Testing:**
→ Local machine or Railway.app

### **Serious Trader:**
→ DigitalOcean Droplet + custom domain + SSL

### **Enterprise:**
→ AWS EC2 + RDS + Load Balancer + CloudWatch

---

## Troubleshooting

### Dashboard won't start:
```bash
# Check logs
docker compose logs dashboard

# Common fix: rebuild
docker compose down
docker compose build --no-cache
docker compose up -d
```

### Worker keeps crashing:
```bash
# Usually API key issues - check logs
docker compose logs worker

# Verify .env file
cat .env
```

### Can't access dashboard:
```bash
# Check if port is open
netstat -tulpn | grep 8501

# Check firewall
ufw status
```

### Database locked:
```bash
# Stop all services
docker compose down

# Check for orphaned processes
ps aux | grep python

# Restart
docker compose up -d
```

---

## Need Help?

- Check logs first: `docker compose logs -f`
- Review .env configuration
- Ensure API keys are valid
- Verify network connectivity
- Check GitHub issues for known problems
