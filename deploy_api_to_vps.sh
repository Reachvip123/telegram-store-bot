#!/bin/bash

# 🚀 Deploy API Bridge to Cambodia VPS
# This script will upload and start the API bridge on your VPS

echo "🚀 DEPLOYING API BRIDGE TO CAMBODIA VPS"
echo "======================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

VPS_IP="157.10.73.90"
VPS_USER="root"
VPS_PATH="/root/telegram-store-bot"

echo -e "${BLUE}📡 Target VPS: ${VPS_IP}${NC}"
echo -e "${BLUE}👤 User: ${VPS_USER}${NC}"
echo -e "${BLUE}📂 Path: ${VPS_PATH}${NC}"
echo ""

# Check if required files exist
echo -e "${YELLOW}📋 Checking required files...${NC}"

if [ ! -f "api_bridge.py" ]; then
    echo -e "${RED}❌ api_bridge.py not found!${NC}"
    echo "Make sure you're in the correct directory."
    exit 1
fi

echo -e "${GREEN}✅ api_bridge.py found${NC}"

# Create API environment file for VPS
echo -e "${YELLOW}🔧 Creating API configuration...${NC}"

cat > .env_api << 'EOF'
# API Bridge Configuration for Cambodia VPS
MONGODB_URI=mongodb+srv://dztsorebase:reachvip@cluster0.tbyhuzf.mongodb.net
DATABASE_NAME=storebot
API_KEY=DZT-SECURE-API-2024-CHANGE-THIS-KEY

# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=False
EOF

echo -e "${GREEN}✅ Created .env_api configuration${NC}"

# Test VPS connection
echo -e "${YELLOW}🔍 Testing VPS connection...${NC}"

if ! ssh -o ConnectTimeout=10 ${VPS_USER}@${VPS_IP} "echo 'Connection OK'" 2>/dev/null; then
    echo -e "${RED}❌ Cannot connect to VPS!${NC}"
    echo "Please check:"
    echo "1. VPS IP address: ${VPS_IP}"
    echo "2. SSH access"
    echo "3. Internet connection"
    exit 1
fi

echo -e "${GREEN}✅ VPS connection successful${NC}"

# Upload files to VPS
echo -e "${YELLOW}📤 Uploading files to VPS...${NC}"

scp api_bridge.py .env_api ${VPS_USER}@${VPS_IP}:${VPS_PATH}/ || {
    echo -e "${RED}❌ Failed to upload files!${NC}"
    exit 1
}

echo -e "${GREEN}✅ Files uploaded successfully${NC}"

# Connect to VPS and setup API
echo -e "${YELLOW}🔧 Setting up API bridge on VPS...${NC}"

ssh ${VPS_USER}@${VPS_IP} << 'ENDSSH'
cd /root/telegram-store-bot

echo "📦 Installing required packages..."
pip install flask flask-cors python-dotenv pymongo

echo "🔄 Stopping existing API if running..."
pkill -f api_bridge.py 2>/dev/null || echo "No existing API process found"

echo "🚀 Starting API Bridge..."
nohup python3 api_bridge.py > api.log 2>&1 &
API_PID=$!

echo "⏳ Waiting for API to start..."
sleep 5

# Check if API started successfully
if curl -s http://localhost:8081/health > /dev/null; then
    echo "✅ API Bridge started successfully!"
    echo "📡 API running on port 8081"
    echo "🔧 Process ID: $API_PID"
    echo $API_PID > api.pid
else
    echo "❌ API Bridge failed to start"
    echo "📋 Checking logs..."
    tail -n 10 api.log
    exit 1
fi

echo "🔥 Opening firewall port 8081..."
ufw allow 8081 2>/dev/null || echo "Firewall command not available or already configured"

echo ""
echo "🎉 API BRIDGE DEPLOYMENT COMPLETE!"
echo "=================================="
echo "📡 API URL: http://157.10.73.90:8081"
echo "🔍 Health Check: http://157.10.73.90:8081/health"
echo "📋 Logs: tail -f /root/telegram-store-bot/api.log"
echo "🛑 Stop API: kill \$(cat /root/telegram-store-bot/api.pid)"

ENDSSH

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}🎉 DEPLOYMENT SUCCESSFUL!${NC}"
    echo "=================================="
    echo ""
    echo -e "${BLUE}📋 NEXT STEPS:${NC}"
    echo "1. Test API: curl http://157.10.73.90:8081/health"
    echo "2. Upload hostinger_index.php to Hostinger"
    echo "3. Access web admin at: http://yourdomain.com/admin"
    echo ""
    echo -e "${YELLOW}⚠️  SECURITY REMINDERS:${NC}"
    echo "- Change API_KEY in .env_api on VPS"
    echo "- Change admin password in web interface"
    echo "- Keep port 8081 secure"
    echo ""
    echo -e "${GREEN}✅ Your API bridge is now running on Cambodia VPS!${NC}"
else
    echo -e "${RED}❌ Deployment failed! Check the error messages above.${NC}"
    exit 1
fi