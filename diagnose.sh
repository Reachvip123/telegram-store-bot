#!/bin/bash

echo "=========================================="
echo "🔍 Diagnosing Admin Panel Issue"
echo "=========================================="
echo ""

# Check current directory
echo "📁 Current directory:"
pwd
echo ""

# Check if files exist
echo "📋 Checking for admin panel files:"
echo ""
echo "admin_panel.py:"
if [ -f "admin_panel.py" ]; then
    echo "✅ Found"
    ls -lh admin_panel.py
else
    echo "❌ NOT FOUND"
fi
echo ""

echo "templates/ directory:"
if [ -d "templates" ]; then
    echo "✅ Found"
    ls -la templates/
else
    echo "❌ NOT FOUND"
fi
echo ""

# Check git status
echo "🔄 Git status:"
git status
echo ""

# Try git pull
echo "⬇️  Running git pull:"
git pull
echo ""

# List all files
echo "📂 All files in directory:"
ls -la
echo ""

# Check if Flask is installed
echo "🐍 Checking Python packages:"
python3 -c "import flask; print('✅ Flask installed')" 2>/dev/null || echo "❌ Flask NOT installed"
echo ""

# Check if port 5000 is in use
echo "🔌 Checking port 5000:"
sudo lsof -i :5000 || echo "Port 5000 is free"
echo ""

# Check admin panel service
echo "⚙️  Checking admin-panel service:"
systemctl status admin-panel --no-pager 2>/dev/null || echo "Service not found (that's OK)"
echo ""

echo "=========================================="
echo "✅ Diagnosis complete"
echo "=========================================="
