#!/bin/bash

echo "=========================================="
echo "🚀 Installing Admin Panel"
echo "=========================================="
echo ""

cd /root/telegram-store-bot

# Install Flask
echo "📦 Installing Flask..."
pip install Flask --quiet

# Download admin_panel.py
echo "⬇️  Downloading admin_panel.py..."
wget -q -O admin_panel.py https://raw.githubusercontent.com/Reachvip123/telegram-store-bot/main/admin_panel.py

# Create templates folder
echo "📁 Creating templates folder..."
mkdir -p templates

# Download all template files
echo "⬇️  Downloading template files..."
cd templates
wget -q -O login.html https://raw.githubusercontent.com/Reachvip123/telegram-store-bot/main/templates/login.html
wget -q -O base.html https://raw.githubusercontent.com/Reachvip123/telegram-store-bot/main/templates/base.html
wget -q -O dashboard.html https://raw.githubusercontent.com/Reachvip123/telegram-store-bot/main/templates/dashboard.html
wget -q -O products.html https://raw.githubusercontent.com/Reachvip123/telegram-store-bot/main/templates/products.html
wget -q -O stock.html https://raw.githubusercontent.com/Reachvip123/telegram-store-bot/main/templates/stock.html
wget -q -O users.html https://raw.githubusercontent.com/Reachvip123/telegram-store-bot/main/templates/users.html
wget -q -O settings.html https://raw.githubusercontent.com/Reachvip123/telegram-store-bot/main/templates/settings.html
cd ..

# Verify files
echo ""
echo "✅ Checking files..."
if [ -f "admin_panel.py" ]; then
    echo "✅ admin_panel.py - OK"
else
    echo "❌ admin_panel.py - MISSING"
fi

if [ -d "templates" ]; then
    echo "✅ templates/ folder - OK"
    echo "   Files: $(ls templates/ | wc -l)"
else
    echo "❌ templates/ folder - MISSING"
fi

echo ""
echo "=========================================="
echo "✅ Installation Complete!"
echo "=========================================="
echo ""
echo "🚀 Starting admin panel..."
echo "📍 URL: http://157.10.73.90:5000"
echo "👤 Username: admin"
echo "🔑 Password: admin123"
echo ""
echo "=========================================="
echo ""

# Start the admin panel
python3 admin_panel.py
