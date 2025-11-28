#!/bin/bash
# Bakong KHQR Proxy Setup Script for Cambodia VPS
# Run this script on your Cambodia VPS

echo "=================================="
echo "Bakong KHQR Proxy Setup"
echo "=================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (use: sudo bash setup_vps.sh)"
    exit 1
fi

# Step 1: Update system
echo "Step 1: Updating system..."
apt update -y
apt upgrade -y

# Step 2: Install Python and dependencies
echo "Step 2: Installing Python and dependencies..."
apt install -y python3 python3-pip python3-venv git curl ufw

# Step 3: Create project directory
echo "Step 3: Creating project directory..."
cd /root
if [ -d "telegram-store-bot" ]; then
    echo "Directory already exists, pulling latest changes..."
    cd telegram-store-bot
    git pull
else
    echo "Cloning repository..."
    git clone https://github.com/Reachvip123/telegram-store-bot.git
    cd telegram-store-bot
fi

# Step 4: Install Python packages
echo "Step 4: Installing Python packages..."
pip3 install flask bakong-khqr python-dotenv gunicorn requests

# Step 5: Create .env file
echo "Step 5: Setting up configuration..."
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cat > .env << 'EOF'
# Replace this with your actual Bakong token
BAKONG_TOKEN=your_bakong_token_here
EOF
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file and add your BAKONG_TOKEN"
    echo "Run: nano /root/telegram-store-bot/.env"
else
    echo ".env file already exists"
fi

# Step 6: Create systemd service
echo "Step 6: Creating systemd service..."
cat > /etc/systemd/system/bakong-proxy.service << 'EOF'
[Unit]
Description=Bakong KHQR Proxy Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/telegram-store-bot
EnvironmentFile=/root/telegram-store-bot/.env
ExecStart=/usr/bin/python3 /root/telegram-store-bot/bakong_proxy.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Step 7: Configure firewall
echo "Step 7: Configuring firewall..."
ufw --force enable
ufw allow 22/tcp
ufw allow 5000/tcp
ufw status

# Step 8: Reload systemd
echo "Step 8: Reloading systemd..."
systemctl daemon-reload
systemctl enable bakong-proxy

echo ""
echo "=================================="
echo "Setup Complete!"
echo "=================================="
echo ""
echo "📋 Next Steps:"
echo ""
echo "1. Edit .env file with your Bakong token:"
echo "   nano /root/telegram-store-bot/.env"
echo ""
echo "2. Start the proxy service:"
echo "   systemctl start bakong-proxy"
echo ""
echo "3. Check if it's running:"
echo "   systemctl status bakong-proxy"
echo ""
echo "4. Test the proxy:"
echo "   curl http://localhost:5000/health"
echo ""
echo "5. Get your VPS IP address:"
echo "   curl ifconfig.me"
echo ""
echo "6. Add to Railway environment variables:"
echo "   BAKONG_PROXY_URL=http://YOUR_VPS_IP:5000"
echo ""
echo "=================================="
