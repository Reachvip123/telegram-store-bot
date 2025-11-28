#!/bin/bash
# Deploy Web Admin Panel to VPS
echo "🚀 Setting up Web Admin Panel on VPS..."

# Navigate to bot directory
cd /root/telegram-store-bot

# Pull latest code (includes admin panel)
echo "📥 Pulling latest code..."
git pull origin main

# Install Flask dependencies
echo "📦 Installing web dependencies..."
pip install flask bcrypt

# Add admin panel configuration to .env
echo "⚙️ Configuring admin panel..."
if ! grep -q "ADMIN_PASSWORD" .env; then
    echo "ADMIN_PASSWORD=admin123" >> .env
    echo "SECRET_KEY=telegram-store-bot-secret-2024" >> .env
    echo "✅ Added admin panel config to .env"
else
    echo "✅ Admin panel config already exists"
fi

# Create systemd service for admin panel
echo "🔧 Creating admin panel service..."
sudo tee /etc/systemd/system/telegram-admin-panel.service > /dev/null <<EOF
[Unit]
Description=Telegram Store Bot Admin Panel
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/telegram-store-bot
Environment=PYTHONPATH=/root/telegram-store-bot
ExecStart=/usr/bin/python3 /root/telegram-store-bot/admin_panel.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start admin panel service
echo "🔄 Starting admin panel service..."
sudo systemctl daemon-reload
sudo systemctl enable telegram-admin-panel
sudo systemctl start telegram-admin-panel

# Check status
echo "📊 Checking admin panel status..."
sleep 3
sudo systemctl status telegram-admin-panel --no-pager -l

echo ""
echo "✅ Web Admin Panel deployed!"
echo ""
echo "🌐 Access your admin panel at:"
echo "   http://157.10.73.90:8080"
echo ""
echo "🔑 Login credentials:"
echo "   Password: admin123"
echo ""
echo "📝 To check logs:"
echo "   sudo journalctl -u telegram-admin-panel -f"
echo ""
echo "🔧 To restart admin panel:"
echo "   sudo systemctl restart telegram-admin-panel"