#!/bin/bash
# Fix Web Admin Access on Cambodia VPS

echo "🔧 Fixing Web Admin Access Issues..."
echo "=================================="

# 1. Check if port 5000 is open
echo "📋 1. Checking if web admin is running..."
if pgrep -f "admin_panel.py" > /dev/null; then
    echo "✅ Web admin is running"
    echo "Process: $(pgrep -f 'admin_panel.py')"
else
    echo "❌ Web admin is NOT running"
    echo "You need to start it with: python3 admin_panel.py"
fi

echo ""
echo "📋 2. Opening firewall port 5000..."

# For Ubuntu/Debian systems with ufw
if command -v ufw &> /dev/null; then
    echo "Using UFW firewall..."
    ufw allow 5000/tcp
    ufw status
fi

# For CentOS/RHEL systems with firewalld
if command -v firewall-cmd &> /dev/null; then
    echo "Using firewalld..."
    firewall-cmd --permanent --add-port=5000/tcp
    firewall-cmd --reload
    firewall-cmd --list-ports
fi

# For systems with iptables
if command -v iptables &> /dev/null; then
    echo "Using iptables..."
    iptables -I INPUT -p tcp --dport 5000 -j ACCEPT
    # Save rules (varies by system)
    if command -v iptables-save &> /dev/null; then
        iptables-save > /etc/iptables/rules.v4 2>/dev/null || echo "Could not save iptables rules"
    fi
fi

echo ""
echo "📋 3. Checking if port 5000 is listening..."
netstat -tulpn | grep :5000 || echo "Port 5000 is not listening"

echo ""
echo "📋 4. Testing local connection..."
curl -s -o /dev/null -w "%{http_code}" http://localhost:5000 || echo "Could not connect locally"

echo ""
echo "🔧 Quick fixes to try:"
echo "=================================="
echo "1. Make sure web admin is running:"
echo "   python3 admin_panel.py"
echo ""
echo "2. If using different port, try port 8080:"
echo "   python3 -c \"from simple_vps_admin import app; app.run(host='0.0.0.0', port=8080)\""
echo ""
echo "3. Check if your VPS provider blocks ports:"
echo "   Contact your VPS provider about opening port 5000"
echo ""
echo "4. Try accessing with different URLs:"
echo "   http://157.10.73.90:5000"
echo "   http://157.10.73.90:8080"
echo ""
echo "5. Check VPS control panel firewall settings"
echo ""
echo "🌐 After fixing, access at:"
echo "   http://157.10.73.90:5000"
echo "   Password: admin123"