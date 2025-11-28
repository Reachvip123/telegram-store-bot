#!/bin/bash
echo "==================================="
echo "Installing Admin Panel on VPS"
echo "==================================="

# Stop any existing admin panel
pkill -f admin_panel.py 2>/dev/null || true

# Navigate to bot directory
cd /root/telegram-store-bot || exit 1

# Pull latest code
git pull origin main

# Install Flask if not installed
pip3 install Flask --quiet

# Kill process on port 8080 if exists
fuser -k 8080/tcp 2>/dev/null || true

# Start admin panel in background
nohup python3 admin_panel.py > admin_panel.log 2>&1 &

echo ""
echo "==================================="
echo "Admin Panel Started!"
echo "==================================="
echo "Access at: http://157.10.73.90:8080"
echo "Username: admin"
echo "Password: admin123"
echo "==================================="
echo ""
echo "To view logs: tail -f /root/telegram-store-bot/admin_panel.log"
echo "To stop: pkill -f admin_panel.py"
