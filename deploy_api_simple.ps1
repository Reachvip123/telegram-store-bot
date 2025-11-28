# Deploy API Bridge to Cambodia VPS - Simple PowerShell Script

Write-Host "Deploying API Bridge to Cambodia VPS..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$VPS_IP = "157.10.73.90"
$VPS_USER = "root"

# Create .env_api file
Write-Host "Creating API configuration..." -ForegroundColor Yellow

@"
MONGODB_URI=mongodb+srv://dztsorebase:reachvip@cluster0.tbyhuzf.mongodb.net
DATABASE_NAME=storebot
API_KEY=DZT-SECURE-API-2024-CHANGE-THIS-KEY
FLASK_ENV=production
FLASK_DEBUG=False
"@ | Out-File -FilePath ".env_api" -Encoding UTF8

Write-Host "Created .env_api configuration" -ForegroundColor Green

# Check if SSH is available
Write-Host "Checking SSH connectivity..." -ForegroundColor Yellow

try {
    $null = Get-Command ssh -ErrorAction Stop
    Write-Host "SSH command found" -ForegroundColor Green
} catch {
    Write-Host "SSH not available. Please install OpenSSH or use manual method." -ForegroundColor Red
    Write-Host ""
    Write-Host "Manual deployment steps:" -ForegroundColor Cyan
    Write-Host "1. Upload api_bridge.py to your VPS: /root/telegram-store-bot/"
    Write-Host "2. Upload .env_api to your VPS: /root/telegram-store-bot/"
    Write-Host "3. SSH to VPS: ssh root@157.10.73.90"
    Write-Host "4. Run: cd /root/telegram-store-bot"
    Write-Host "5. Run: pip install flask flask-cors python-dotenv pymongo"
    Write-Host "6. Run: nohup python3 api_bridge.py > api.log 2>&1 &"
    Write-Host "7. Run: ufw allow 8081"
    Write-Host "8. Test: curl http://localhost:8081/health"
    exit
}

# Test VPS connection
Write-Host "Testing VPS connection..." -ForegroundColor Yellow

$testConnection = ssh -o ConnectTimeout=10 -o BatchMode=yes "$VPS_USER@$VPS_IP" "echo 'OK'" 2>$null

if ($LASTEXITCODE -ne 0) {
    Write-Host "Cannot connect to VPS automatically." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Please follow manual deployment:" -ForegroundColor Cyan
    Write-Host "1. Upload files manually to VPS"
    Write-Host "2. Follow instructions in MANUAL_API_DEPLOYMENT.md"
    Write-Host ""
    Write-Host "Or try SSH connection manually:" -ForegroundColor Cyan
    Write-Host "ssh root@157.10.73.90"
    exit
}

Write-Host "VPS connection successful" -ForegroundColor Green

# Upload files
Write-Host "Uploading files to VPS..." -ForegroundColor Yellow

scp "api_bridge.py" ".env_api" "${VPS_USER}@${VPS_IP}:/root/telegram-store-bot/"

if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to upload files" -ForegroundColor Red
    Write-Host "Please upload manually or check SSH key access"
    exit
}

Write-Host "Files uploaded successfully" -ForegroundColor Green

# Deploy on VPS
Write-Host "Setting up API on VPS..." -ForegroundColor Yellow

$commands = "cd /root/telegram-store-bot && pip install flask flask-cors python-dotenv pymongo && pkill -f api_bridge.py 2>/dev/null; nohup python3 api_bridge.py > api.log 2>&1 & sleep 3; ufw allow 8081; curl -s http://localhost:8081/health"

ssh "$VPS_USER@$VPS_IP" $commands

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "DEPLOYMENT SUCCESSFUL!" -ForegroundColor Green
    Write-Host "=====================" -ForegroundColor Green
    Write-Host ""
    Write-Host "API URL: http://157.10.73.90:8081" -ForegroundColor Cyan
    Write-Host "Health Check: http://157.10.73.90:8081/health" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "1. Test API: Invoke-WebRequest http://157.10.73.90:8081/health"
    Write-Host "2. Upload hostinger_index.php to Hostinger"
    Write-Host "3. Access web admin at: http://yourdomain.com/admin"
} else {
    Write-Host "Deployment may have issues. Check manually:" -ForegroundColor Yellow
    Write-Host "ssh root@157.10.73.90"
    Write-Host "cd /root/telegram-store-bot"
    Write-Host "tail -f api.log"
}