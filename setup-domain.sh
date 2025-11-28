#!/bin/bash

# ============================================
# Custom Domain Setup for Admin Panel
# Domain: dzpremium.store (or admin.dzpremium.store)
# ============================================

echo "============================================"
echo "🌐 Setting up Custom Domain for Admin Panel"
echo "============================================"
echo ""

# Prompt for domain choice
echo "Choose your domain option:"
echo "1) dzpremium.store (main domain)"
echo "2) admin.dzpremium.store (subdomain - RECOMMENDED)"
echo ""
read -p "Enter choice (1 or 2): " domain_choice

if [ "$domain_choice" == "1" ]; then
    DOMAIN="dzpremium.store"
else
    DOMAIN="admin.dzpremium.store"
fi

echo ""
echo "✅ Using domain: $DOMAIN"
echo ""

# Step 1: Update system
echo "📦 Updating system packages..."
sudo apt update

# Step 2: Install Nginx
echo "📦 Installing Nginx..."
sudo apt install nginx -y

# Step 3: Create Nginx configuration
echo "⚙️  Creating Nginx configuration..."
sudo tee /etc/nginx/sites-available/admin-panel > /dev/null <<EOF
server {
    listen 80;
    server_name $DOMAIN;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # WebSocket support (if needed)
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
EOF

# Step 4: Enable site
echo "🔗 Enabling site..."
sudo ln -sf /etc/nginx/sites-available/admin-panel /etc/nginx/sites-enabled/

# Step 5: Remove default site
sudo rm -f /etc/nginx/sites-enabled/default

# Step 6: Test Nginx configuration
echo "🧪 Testing Nginx configuration..."
sudo nginx -t

if [ $? -ne 0 ]; then
    echo "❌ Nginx configuration test failed!"
    exit 1
fi

# Step 7: Restart Nginx
echo "🔄 Restarting Nginx..."
sudo systemctl restart nginx
sudo systemctl enable nginx

# Step 8: Configure firewall
echo "🔥 Configuring firewall..."
sudo ufw allow 'Nginx Full'
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Step 9: Install Certbot for SSL
echo "🔒 Installing Certbot for SSL..."
sudo apt install certbot python3-certbot-nginx -y

# Step 10: Get SSL certificate
echo ""
echo "============================================"
echo "📋 DNS CONFIGURATION REQUIRED"
echo "============================================"
echo ""
echo "Before continuing, make sure you've added this DNS record:"
echo ""
echo "Type: A"
echo "Name: ${DOMAIN/dzpremium.store/}"
echo "Value: 157.10.73.90"
echo "TTL: 3600"
echo ""
read -p "Press ENTER once DNS is configured and propagated..."
echo ""

echo "🔒 Obtaining SSL certificate..."
sudo certbot --nginx -d $DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN --redirect

if [ $? -eq 0 ]; then
    echo ""
    echo "============================================"
    echo "✅ SUCCESS!"
    echo "============================================"
    echo ""
    echo "🌐 Your admin panel is now available at:"
    echo "   https://$DOMAIN"
    echo ""
    echo "🔒 SSL Certificate: ENABLED"
    echo "🔄 Auto-renewal: ENABLED"
    echo ""
    echo "📝 Default Login:"
    echo "   Username: admin"
    echo "   Password: admin123"
    echo ""
    echo "⚠️  CHANGE YOUR PASSWORD IMMEDIATELY!"
    echo ""
else
    echo ""
    echo "⚠️  SSL certificate installation failed."
    echo "You can still access via HTTP:"
    echo "   http://$DOMAIN"
    echo ""
    echo "To retry SSL later, run:"
    echo "   sudo certbot --nginx -d $DOMAIN"
    echo ""
fi

# Step 11: Setup auto-renewal
echo "🔄 Setting up SSL auto-renewal..."
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer

echo ""
echo "============================================"
echo "📊 Service Status"
echo "============================================"
echo ""
sudo systemctl status nginx --no-pager -l
echo ""
echo "✅ Setup complete!"
echo ""
