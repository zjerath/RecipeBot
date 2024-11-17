#!/bin/bash
source /var/app/venv/*/bin/activate
cd /var/app/current

# Kill any existing processes
pkill -f "python app.py" || true

# Start the bot
nohup python app.py &