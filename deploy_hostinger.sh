#!/bin/bash

# 🚀 Hostinger MySQL Bot Deployment Script

echo "🚀 Starting Hostinger MySQL Bot Deployment"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  Creating .env file from template...${NC}"
    cp .env_hostinger_template .env
    echo -e "${RED}❌ Please edit .env file with your Hostinger MySQL details!${NC}"
    echo "   1. Open .env file"
    echo "   2. Set your MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE"
    echo "   3. Set your BOT_TOKEN and other config"
    echo "   4. Run this script again"
    exit 1
fi

echo -e "${GREEN}✅ Found .env file${NC}"

# Load environment variables
source .env

# Check if MySQL variables are set
if [ -z "$MYSQL_HOST" ] || [ -z "$MYSQL_USER" ] || [ -z "$MYSQL_PASSWORD" ] || [ -z "$MYSQL_DATABASE" ]; then
    echo -e "${RED}❌ MySQL configuration incomplete in .env file!${NC}"
    echo "Please set: MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE"
    exit 1
fi

echo -e "${GREEN}✅ MySQL configuration found${NC}"

# Install dependencies
echo -e "${YELLOW}📦 Installing Python dependencies...${NC}"
pip install -r requirements_mysql.txt

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to install dependencies!${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Dependencies installed${NC}"

# Test database connection
echo -e "${YELLOW}🔍 Testing MySQL connection...${NC}"
python3 -c "
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

try:
    conn = mysql.connector.connect(
        host=os.getenv('MYSQL_HOST'),
        user=os.getenv('MYSQL_USER'),
        password=os.getenv('MYSQL_PASSWORD'),
        database=os.getenv('MYSQL_DATABASE'),
        port=int(os.getenv('MYSQL_PORT', '3306'))
    )
    print('✅ MySQL connection successful!')
    conn.close()
except Exception as e:
    print(f'❌ MySQL connection failed: {e}')
    exit(1)
"

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Database connection failed!${NC}"
    echo "Please check your MySQL configuration in .env file"
    exit 1
fi

echo -e "${GREEN}✅ Database connection successful${NC}"

# Create startup scripts
echo -e "${YELLOW}📝 Creating startup scripts...${NC}"

# Bot startup script
cat > start_bot.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
echo "🤖 Starting Telegram Store Bot (MySQL version)..."
nohup python3 storebot_mysql.py > bot.log 2>&1 &
echo $! > bot.pid
echo "✅ Bot started! PID: $(cat bot.pid)"
echo "📋 Check logs: tail -f bot.log"
EOF

# Admin panel startup script
cat > start_admin.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
echo "🌐 Starting Admin Panel..."
nohup python3 admin_panel_mysql.py > admin.log 2>&1 &
echo $! > admin.pid
echo "✅ Admin panel started! PID: $(cat admin.pid)"
echo "🌐 Access at: http://your-domain:8080"
echo "📋 Check logs: tail -f admin.log"
EOF

# Stop scripts
cat > stop_bot.sh << 'EOF'
#!/bin/bash
if [ -f bot.pid ]; then
    PID=$(cat bot.pid)
    kill $PID 2>/dev/null
    rm bot.pid
    echo "🤖 Bot stopped!"
else
    echo "❌ Bot PID file not found"
fi
EOF

cat > stop_admin.sh << 'EOF'
#!/bin/bash
if [ -f admin.pid ]; then
    PID=$(cat admin.pid)
    kill $PID 2>/dev/null
    rm admin.pid
    echo "🌐 Admin panel stopped!"
else
    echo "❌ Admin panel PID file not found"
fi
EOF

# Make scripts executable
chmod +x start_bot.sh start_admin.sh stop_bot.sh stop_admin.sh

echo -e "${GREEN}✅ Startup scripts created${NC}"

# Create status check script
cat > status.sh << 'EOF'
#!/bin/bash
echo "📊 Bot Status Check"
echo "=================="

# Check bot
if [ -f bot.pid ]; then
    PID=$(cat bot.pid)
    if ps -p $PID > /dev/null 2>&1; then
        echo "🤖 Bot: ✅ RUNNING (PID: $PID)"
    else
        echo "🤖 Bot: ❌ STOPPED (stale PID file)"
        rm bot.pid
    fi
else
    echo "🤖 Bot: ❌ NOT RUNNING"
fi

# Check admin panel
if [ -f admin.pid ]; then
    PID=$(cat admin.pid)
    if ps -p $PID > /dev/null 2>&1; then
        echo "🌐 Admin: ✅ RUNNING (PID: $PID)"
    else
        echo "🌐 Admin: ❌ STOPPED (stale PID file)"
        rm admin.pid
    fi
else
    echo "🌐 Admin: ❌ NOT RUNNING"
fi

# Check ports
echo ""
echo "🔍 Port Status:"
netstat -tlnp 2>/dev/null | grep ":8080 " && echo "🌐 Port 8080: ✅ OPEN" || echo "🌐 Port 8080: ❌ CLOSED"
EOF

chmod +x status.sh

echo ""
echo -e "${GREEN}🎉 DEPLOYMENT COMPLETE!${NC}"
echo "================================"
echo ""
echo -e "${YELLOW}📋 NEXT STEPS:${NC}"
echo "1. Start the bot:        ./start_bot.sh"
echo "2. Start admin panel:    ./start_admin.sh"
echo "3. Check status:         ./status.sh"
echo "4. View logs:            tail -f bot.log"
echo "5. Access admin:         http://your-domain:8080"
echo ""
echo -e "${YELLOW}🛡️  DEFAULT LOGIN:${NC}"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo -e "${YELLOW}⚠️  IMPORTANT:${NC}"
echo "- Change admin password in .env file"
echo "- Test bot with /start command"
echo "- Add products through admin panel"
echo "- Check bot.log and admin.log for errors"
echo ""
echo -e "${GREEN}✅ Ready for Hostinger! 🚀${NC}"