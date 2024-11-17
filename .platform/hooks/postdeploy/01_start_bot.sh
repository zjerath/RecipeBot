#!/bin/bash
source /var/app/venv/*/bin/activate

# Kill any existing bot processes
pkill -f "python bot.py" || true

# Start the bot
cd /var/app/current
nohup python bot.py > /var/log/bot.log 2>&1 &