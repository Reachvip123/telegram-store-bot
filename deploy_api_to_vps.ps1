# 🚀 Deploy API Bridge to Cambodia VPS - PowerShell Version
# This script will upload and start the API bridge on your VPS

Write-Host "🚀 DEPLOYING API BRIDGE TO CAMBODIA VPS" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan

$VPS_IP = "157.10.73.90"
$VPS_USER = "root"
$VPS_PATH = "/root/telegram-store-bot"

Write-Host "📡 Target VPS: $VPS_IP" -ForegroundColor Blue
Write-Host "👤 User: $VPS_USER" -ForegroundColor Blue
Write-Host "📂 Path: $VPS_PATH" -ForegroundColor Blue
Write-Host ""

# Check if required files exist
Write-Host "📋 Checking required files..." -ForegroundColor Yellow

if (-not (Test-Path "api_bridge.py")) {
    Write-Host "❌ api_bridge.py not found!" -ForegroundColor Red
    Write-Host "Make sure you're in the correct directory."
    exit 1
}

Write-Host "✅ api_bridge.py found" -ForegroundColor Green

# Create API environment file for VPS
Write-Host "🔧 Creating API configuration..." -ForegroundColor Yellow

$envContent = @"
# API Bridge Configuration for Cambodia VPS
MONGODB_URI=mongodb+srv://dztsorebase:reachvip@cluster0.tbyhuzf.mongodb.net
DATABASE_NAME=storebot
API_KEY=DZT-SECURE-API-2024-CHANGE-THIS-KEY

# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=False
"@

$envContent | Out-File -FilePath ".env_api" -Encoding UTF8

Write-Host "✅ Created .env_api configuration" -ForegroundColor Green

# Test VPS connection (if ssh is available)
Write-Host "🔍 Testing VPS connection..." -ForegroundColor Yellow

try {
    $sshTest = ssh -o ConnectTimeout=10 "$VPS_USER@$VPS_IP" "echo 'Connection OK'" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ VPS connection successful" -ForegroundColor Green
    } else {
        throw "SSH connection failed"
    }
} catch {
    Write-Host "❌ Cannot connect to VPS!" -ForegroundColor Red
    Write-Host "Please check:" -ForegroundColor Yellow
    Write-Host "1. VPS IP address: $VPS_IP"
    Write-Host "2. SSH access configured"
    Write-Host "3. Internet connection"
    Write-Host ""
    Write-Host "💡 If you don't have SSH configured, use manual upload method:" -ForegroundColor Cyan
    Write-Host "1. Upload api_bridge.py and .env_api to your VPS manually"
    Write-Host "2. Run: python3 api_bridge.py on your VPS"
    exit 1
}

# Upload files to VPS
Write-Host "📤 Uploading files to VPS..." -ForegroundColor Yellow

try {
    scp "api_bridge.py" ".env_api" "$VPS_USER@${VPS_IP}:$VPS_PATH/"
    if ($LASTEXITCODE -ne 0) {
        throw "SCP upload failed"
    }
    Write-Host "✅ Files uploaded successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to upload files!" -ForegroundColor Red
    Write-Host "💡 Manual upload method:" -ForegroundColor Cyan
    Write-Host "1. Copy api_bridge.py to your VPS: $VPS_PATH/"
    Write-Host "2. Copy .env_api to your VPS: $VPS_PATH/"
    exit 1
}

# Connect to VPS and setup API
Write-Host "🔧 Setting up API bridge on VPS..." -ForegroundColor Yellow

$sshCommands = @"
cd $VPS_PATH

echo "📦 Installing required packages..."
pip install flask flask-cors python-dotenv pymongo

echo "🔄 Stopping existing API if running..."
pkill -f api_bridge.py 2>/dev/null || echo "No existing API process found"

echo "🚀 Starting API Bridge..."
nohup python3 api_bridge.py > api.log 2>&1 &
API_PID=`$!

echo "⏳ Waiting for API to start..."
sleep 5

# Check if API started successfully
if curl -s http://localhost:8081/health > /dev/null; then
    echo "✅ API Bridge started successfully!"
    echo "📡 API running on port 8081"
    echo "🔧 Process ID: `$API_PID"
    echo `$API_PID > api.pid
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
echo "📋 Logs: tail -f $VPS_PATH/api.log"
echo "🛑 Stop API: kill \`$(cat $VPS_PATH/api.pid\`)"
"@

try {
    ssh "$VPS_USER@$VPS_IP" $sshCommands
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "🎉 DEPLOYMENT SUCCESSFUL!" -ForegroundColor Green
        Write-Host "=================================="
        Write-Host ""
        Write-Host "📋 NEXT STEPS:" -ForegroundColor Blue
        Write-Host "1. Test API: Invoke-WebRequest http://157.10.73.90:8081/health"
        Write-Host "2. Upload hostinger_index.php to Hostinger"
        Write-Host "3. Access web admin at: http://yourdomain.com/admin"
        Write-Host ""
        Write-Host "⚠️  SECURITY REMINDERS:" -ForegroundColor Yellow
        Write-Host "- Change API_KEY in .env_api on VPS"
        Write-Host "- Change admin password in web interface"
        Write-Host "- Keep port 8081 secure"
        Write-Host ""
        Write-Host "✅ Your API bridge is now running on Cambodia VPS!" -ForegroundColor Green
    } else {
        throw "SSH command execution failed"
    }
} catch {
    Write-Host "❌ Deployment failed! Check the error messages above." -ForegroundColor Red
    exit 1
}

# Test the API endpoint
Write-Host ""
Write-Host "🔍 Testing API endpoint..." -ForegroundColor Yellow

try {
    $response = Invoke-WebRequest -Uri "http://157.10.73.90:8081/health" -TimeoutSec 10
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ API is responding correctly!" -ForegroundColor Green
        $content = $response.Content | ConvertFrom-Json
        Write-Host "📡 API Status: $($content.status)" -ForegroundColor Cyan
        Write-Host "🏢 Service: $($content.service)" -ForegroundColor Cyan
        Write-Host "📍 Location: $($content.location)" -ForegroundColor Cyan
    } else {
        Write-Host "⚠️  API responded but with unexpected status: $($response.StatusCode)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  Cannot test API endpoint from here (might be firewall)" -ForegroundColor Yellow
    Write-Host "💡 Test manually: ssh $VPS_USER@$VPS_IP 'curl http://localhost:8081/health'" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "🎯 READY FOR HOSTINGER SETUP!" -ForegroundColor Green
Write-Host "Now upload the web admin panel to your Hostinger Business Plan."