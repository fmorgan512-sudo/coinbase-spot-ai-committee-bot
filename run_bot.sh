#!/bin/bash
# Script to run the bot persistently

cd /home/user/coinbase-spot-ai-committee-bot

# Start dashboard in background
nohup streamlit run app/dashboard.py --server.port=8501 --server.address=0.0.0.0 > logs/dashboard.log 2>&1 &

# Start worker in background
nohup python3 -m app.worker > logs/worker.log 2>&1 &

echo "Bot started!"
echo "Dashboard: http://localhost:8501"
echo "Logs: tail -f logs/*.log"
