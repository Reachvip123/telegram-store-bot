#!/bin/bash

echo "🚀 Setting up Simple Web Admin Panel on Cambodia VPS"
echo "================================================="

# Create venv if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install required packages
echo "📦 Installing required packages..."
pip install flask pymongo python-dotenv

# Check if .env exists, if not create one
if [ ! -f ".env" ]; then
    echo "⚙️ Creating .env file..."
    cat > .env << EOL
# MongoDB Connection (same as your bot)
MONGODB_URI=mongodb+srv://dztsorebase:reachvip@cluster0.tbyhuzf.mongodb.net
DATABASE_NAME=storebot
EOL
fi

echo "✅ Setup complete!"
echo ""
echo "🌟 How to run:"
echo "1. Copy simple_vps_admin.py to your VPS"
echo "2. Run: python3 simple_vps_admin.py"
echo "3. Access: http://157.10.73.90:5000"
echo "4. Password: admin123"
echo ""
echo "🎯 This admin panel will:"
echo "  - Show live dashboard with stats"
echo "  - Manage products and stock"
echo "  - View users"
echo "  - Add stock items easily"
echo ""
echo "📋 Next steps:"
echo "  - Change the admin password in the script"
echo "  - Run both your bot and admin panel"
echo "  - Access from any browser!"