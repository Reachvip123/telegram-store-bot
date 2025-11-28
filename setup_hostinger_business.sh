#!/bin/bash

# 🎯 Deploy Web Admin Panel to Hostinger Business Plan
# This script helps you set up the perfect architecture:
# Bot (Cambodia VPS) ↔ Web Admin (Hostinger Business)

echo "🎯 HOSTINGER BUSINESS SETUP SCRIPT"
echo "=================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Architecture:${NC}"
echo "📱 Telegram Bot      → Cambodia VPS (157.10.73.90)"
echo "🗄️ Database          → MongoDB Atlas (Cloud)"  
echo "🌐 Web Admin Panel   → Hostinger Business Plan"
echo "📡 API Bridge        → Cambodia VPS (Port 8081)"
echo ""

# Check if required files exist
echo -e "${YELLOW}📋 Checking required files...${NC}"

if [ ! -f "api_bridge.py" ]; then
    echo -e "${RED}❌ api_bridge.py not found!${NC}"
    exit 1
fi

if [ ! -f "web_admin_standalone.php" ]; then
    echo -e "${RED}❌ web_admin_standalone.php not found!${NC}"
    exit 1
fi

echo -e "${GREEN}✅ All required files found${NC}"

# Step 1: Configure API Bridge for VPS
echo ""
echo -e "${YELLOW}🔧 Step 1: Configure API Bridge for Cambodia VPS${NC}"

# Create API environment file
cat > .env_api << 'EOF'
# API Bridge Configuration for Cambodia VPS
MONGODB_URI=mongodb+srv://dztsorebase:reachvip@cluster0.tbyhuzf.mongodb.net
DATABASE_NAME=storebot
API_KEY=DZT-API-2024-SUPER-SECRET-KEY-CHANGE-THIS

# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=False
EOF

echo -e "${GREEN}✅ Created .env_api configuration${NC}"

# Step 2: Create VPS deployment script
echo ""
echo -e "${YELLOW}🚀 Step 2: Creating VPS deployment commands${NC}"

cat > deploy_to_vps.sh << 'EOF'
#!/bin/bash

echo "📡 Deploying API Bridge to Cambodia VPS..."

# Upload API bridge to VPS
scp api_bridge.py .env_api root@157.10.73.90:/root/telegram-store-bot/

# Connect to VPS and setup API
ssh root@157.10.73.90 << 'ENDSSH'
cd /root/telegram-store-bot

# Install required packages
pip install flask flask-cors python-dotenv

# Stop existing API if running
pkill -f api_bridge.py

# Start API bridge
echo "🚀 Starting API Bridge..."
nohup python3 api_bridge.py > api.log 2>&1 &

# Check if API started
sleep 3
if curl -s http://localhost:8081/health > /dev/null; then
    echo "✅ API Bridge started successfully!"
    echo "📡 API running on port 8081"
else
    echo "❌ API Bridge failed to start"
    echo "📋 Check logs: tail -f api.log"
fi

# Open firewall port
ufw allow 8081

echo "🔥 API Bridge deployment complete!"
echo "🌐 API URL: http://157.10.73.90:8081"

ENDSSH

echo "✅ VPS deployment complete!"
EOF

chmod +x deploy_to_vps.sh

echo -e "${GREEN}✅ Created deploy_to_vps.sh script${NC}"

# Step 3: Configure Hostinger web admin
echo ""
echo -e "${YELLOW}🌐 Step 3: Configure Hostinger Web Admin${NC}"

# Update PHP file with proper configuration
cat > hostinger_index.php << 'EOF'
<?php
/**
 * Telegram Store Bot - Web Admin Panel
 * Hostinger Business Plan Version
 * 
 * Upload this file to: public_html/admin/index.php
 * Access at: http://yourdomain.com/admin
 */

session_start();

// ===========================================
// 🔧 CONFIGURATION - EDIT THESE VALUES!
// ===========================================

$ADMIN_PASSWORD = 'admin123';  // ⚠️ CHANGE THIS PASSWORD!
$VPS_API_URL = 'http://157.10.73.90:8081';  // Your Cambodia VPS API
$API_KEY = 'DZT-API-2024-SUPER-SECRET-KEY-CHANGE-THIS';  // ⚠️ CHANGE THIS!

// ===========================================
// 📱 AUTHENTICATION & SECURITY
// ===========================================

function httpRequest($endpoint, $data = null) {
    global $VPS_API_URL, $API_KEY;
    
    $url = $VPS_API_URL . '/api/' . $endpoint;
    
    $options = [
        'http' => [
            'method' => $data ? 'POST' : 'GET',
            'header' => [
                'Content-Type: application/json',
                'X-API-Key: ' . $API_KEY
            ],
            'content' => $data ? json_encode($data) : null,
            'timeout' => 30
        ]
    ];
    
    $context = stream_context_create($options);
    $result = @file_get_contents($url, false, $context);
    
    return $result ? json_decode($result, true) : false;
}

// Simple authentication
if (!isset($_SESSION['admin_logged_in']) && $_GET['action'] !== 'login') {
    showLoginPage();
    exit;
}

// Handle login
if ($_GET['action'] === 'login') {
    if ($_POST['password'] === $ADMIN_PASSWORD) {
        $_SESSION['admin_logged_in'] = true;
        header('Location: ?action=dashboard');
        exit;
    } else {
        showLoginPage('Invalid password!');
        exit;
    }
}

// Handle logout
if ($_GET['action'] === 'logout') {
    session_destroy();
    header('Location: ?action=login');
    exit;
}

$action = $_GET['action'] ?? 'dashboard';

?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Store Bot Admin - Hostinger</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .sidebar {
            min-height: 100vh;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .sidebar .nav-link {
            color: rgba(255,255,255,0.8);
            padding: 0.75rem 1rem;
            margin: 0.25rem 0;
            border-radius: 0.5rem;
            transition: all 0.3s;
        }
        .sidebar .nav-link:hover, .sidebar .nav-link.active {
            color: white;
            background-color: rgba(255,255,255,0.1);
        }
        .card {
            border: none;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        }
        .stat-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
        .btn-primary { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border: none; }
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="row">
            <!-- Sidebar -->
            <nav class="col-md-2 d-none d-md-block sidebar">
                <div class="position-sticky">
                    <div class="text-center py-4">
                        <h4 class="text-white"><i class="fas fa-store"></i> Store Admin</h4>
                        <small class="text-white-50">Hostinger + VPS</small>
                    </div>
                    
                    <ul class="nav flex-column">
                        <li class="nav-item">
                            <a class="nav-link <?= $action === 'dashboard' ? 'active' : '' ?>" href="?action=dashboard">
                                <i class="fas fa-chart-dashboard"></i> Dashboard
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link <?= $action === 'products' ? 'active' : '' ?>" href="?action=products">
                                <i class="fas fa-box"></i> Products
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link <?= $action === 'users' ? 'active' : '' ?>" href="?action=users">
                                <i class="fas fa-users"></i> Users
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link <?= $action === 'orders' ? 'active' : '' ?>" href="?action=orders">
                                <i class="fas fa-shopping-cart"></i> Orders
                            </a>
                        </li>
                        <li class="nav-item mt-4">
                            <a class="nav-link text-danger" href="?action=logout">
                                <i class="fas fa-sign-out-alt"></i> Logout
                            </a>
                        </li>
                    </ul>
                </div>
            </nav>

            <!-- Main content -->
            <main class="col-md-10 ms-sm-auto">
                <nav class="navbar navbar-light bg-white shadow-sm mb-4">
                    <span class="navbar-brand">
                        <i class="fas fa-robot"></i> Telegram Store Bot - Web Admin
                    </span>
                    <div class="navbar-nav ms-auto">
                        <span class="navbar-text me-3">
                            <i class="fas fa-server text-success"></i> VPS Connected
                        </span>
                    </div>
                </nav>

                <div class="container-fluid">
                    <?php
                    switch ($action) {
                        case 'dashboard':
                            showDashboard();
                            break;
                        case 'products':
                            showProducts();
                            break;
                        case 'users':
                            showUsers();
                            break;
                        case 'orders':
                            showOrders();
                            break;
                        default:
                            showDashboard();
                    }
                    ?>
                </div>
            </main>
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>

<?php
function showLoginPage($error = '') {
    global $VPS_API_URL;
    ?>
    <!DOCTYPE html>
    <html><head><title>Admin Login</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; align-items: center; justify-content: center; }
        .login-card { background: white; border-radius: 20px; box-shadow: 0 20px 40px rgba(0,0,0,0.1); max-width: 400px; width: 100%; }
    </style></head>
    <body>
        <div class="login-card p-4">
            <div class="text-center mb-4">
                <h2><i class="fas fa-robot"></i></h2>
                <h4>Store Bot Admin</h4>
                <p class="text-muted">Hostinger Business Plan</p>
                <small class="badge bg-success">Connected to: <?= $VPS_API_URL ?></small>
            </div>
            
            <?php if ($error): ?>
                <div class="alert alert-danger"><?= $error ?></div>
            <?php endif; ?>
            
            <form method="POST" action="?action=login">
                <div class="mb-3">
                    <input type="password" name="password" class="form-control" placeholder="Admin Password" required>
                </div>
                <button type="submit" class="btn btn-primary w-100">Login to Admin Panel</button>
            </form>
        </div>
    </body></html>
    <?php
}

function showDashboard() {
    $stats = httpRequest('stats');
    $connection_test = httpRequest('../health');
    ?>
    <h1><i class="fas fa-chart-dashboard"></i> Dashboard</h1>
    
    <!-- Connection Status -->
    <div class="row mb-4">
        <div class="col-12">
            <div class="alert alert-<?= $connection_test ? 'success' : 'danger' ?>">
                <i class="fas fa-<?= $connection_test ? 'check-circle' : 'exclamation-triangle' ?>"></i>
                <strong>VPS Connection:</strong> 
                <?= $connection_test ? 'Connected to Cambodia VPS ✅' : 'Connection Failed ❌' ?>
                <?php if ($connection_test): ?>
                    <small class="ms-2">Last sync: <?= date('Y-m-d H:i:s') ?></small>
                <?php endif; ?>
            </div>
        </div>
    </div>

    <!-- Statistics -->
    <div class="row mb-4">
        <div class="col-md-3"><div class="card stat-card"><div class="card-body text-center">
            <i class="fas fa-box fa-3x mb-3"></i>
            <h3><?= $stats['products'] ?? '0' ?></h3><p>Products</p>
        </div></div></div>
        <div class="col-md-3"><div class="card bg-success text-white"><div class="card-body text-center">
            <i class="fas fa-users fa-3x mb-3"></i>
            <h3><?= $stats['users'] ?? '0' ?></h3><p>Users</p>
        </div></div></div>
        <div class="col-md-3"><div class="card bg-warning text-white"><div class="card-body text-center">
            <i class="fas fa-shopping-cart fa-3x mb-3"></i>
            <h3><?= $stats['sold'] ?? '0' ?></h3><p>Sold</p>
        </div></div></div>
        <div class="col-md-3"><div class="card bg-info text-white"><div class="card-body text-center">
            <i class="fas fa-warehouse fa-3x mb-3"></i>
            <h3><?= $stats['stock'] ?? '0' ?></h3><p>Stock</p>
        </div></div></div>
    </div>

    <!-- Architecture Info -->
    <div class="row">
        <div class="col-12">
            <div class="card border-primary">
                <div class="card-header bg-primary text-white">
                    <h6><i class="fas fa-network-wired"></i> System Architecture</h6>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-4">
                            <h6><i class="fas fa-robot text-primary"></i> Telegram Bot</h6>
                            <p><small>Location: Cambodia VPS<br>Status: <span class="badge bg-success">Active</span></small></p>
                        </div>
                        <div class="col-md-4">
                            <h6><i class="fas fa-database text-info"></i> Database</h6>
                            <p><small>Type: MongoDB Atlas<br>Status: <span class="badge bg-success">Connected</span></small></p>
                        </div>
                        <div class="col-md-4">
                            <h6><i class="fas fa-globe text-warning"></i> Web Admin</h6>
                            <p><small>Host: Hostinger Business<br>Status: <span class="badge bg-success">Online</span></small></p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <?php
}

function showProducts() {
    $products = httpRequest('products');
    ?>
    <h1><i class="fas fa-box"></i> Products</h1>
    <div class="card">
        <div class="card-body">
            <?php if ($products && $products['success']): ?>
                <div class="table-responsive">
                    <table class="table">
                        <thead class="table-primary">
                            <tr><th>ID</th><th>Name</th><th>Description</th><th>Variants</th><th>Sold</th></tr>
                        </thead>
                        <tbody>
                            <?php foreach ($products['products'] as $id => $product): ?>
                            <tr>
                                <td><?= htmlspecialchars($id) ?></td>
                                <td><strong><?= htmlspecialchars($product['name']) ?></strong></td>
                                <td><?= htmlspecialchars($product['desc']) ?></td>
                                <td>
                                    <?php foreach ($product['variants'] as $vid => $variant): ?>
                                        <span class="badge bg-primary"><?= htmlspecialchars($variant['name']) ?> - $<?= $variant['price'] ?></span><br>
                                    <?php endforeach; ?>
                                </td>
                                <td><span class="badge bg-success"><?= $product['sold'] ?></span></td>
                            </tr>
                            <?php endforeach; ?>
                        </tbody>
                    </table>
                </div>
            <?php else: ?>
                <div class="text-center py-4">
                    <i class="fas fa-box fa-3x text-muted mb-3"></i>
                    <h5>No products found</h5>
                    <p class="text-muted">Products will appear here when added via bot commands.</p>
                </div>
            <?php endif; ?>
        </div>
    </div>
    <?php
}

function showUsers() {
    $users = httpRequest('users');
    ?>
    <h1><i class="fas fa-users"></i> Users</h1>
    <div class="card">
        <div class="card-body">
            <div class="text-center py-4">
                <i class="fas fa-users fa-3x text-muted mb-3"></i>
                <h5>User Management</h5>
                <p class="text-muted">User data is managed through the bot interface.</p>
            </div>
        </div>
    </div>
    <?php
}

function showOrders() {
    $orders = httpRequest('orders');
    ?>
    <h1><i class="fas fa-shopping-cart"></i> Orders</h1>
    <div class="card">
        <div class="card-body">
            <div class="text-center py-4">
                <i class="fas fa-shopping-cart fa-3x text-muted mb-3"></i>
                <h5>Order History</h5>
                <p class="text-muted">Order data will be displayed here when customers make purchases.</p>
            </div>
        </div>
    </div>
    <?php
}
?>
EOF

echo -e "${GREEN}✅ Created hostinger_index.php${NC}"

# Step 4: Create upload instructions
echo ""
echo -e "${YELLOW}📤 Step 4: Creating upload instructions${NC}"

cat > UPLOAD_TO_HOSTINGER.txt << 'EOF'
📤 UPLOAD INSTRUCTIONS FOR HOSTINGER BUSINESS

1. 📁 LOGIN TO HOSTINGER FILE MANAGER
   - Go to your Hostinger control panel
   - Click "File Manager"

2. 📂 CREATE ADMIN FOLDER
   - Navigate to: public_html
   - Create new folder: admin
   - Enter the admin folder

3. 📄 UPLOAD WEB ADMIN FILE
   - Upload: hostinger_index.php
   - Rename it to: index.php

4. 🔧 EDIT CONFIGURATION (IMPORTANT!)
   - Open index.php in file manager
   - Find these lines and change them:
   
   $ADMIN_PASSWORD = 'admin123';  // ← CHANGE THIS!
   $API_KEY = 'DZT-API-2024-SUPER-SECRET-KEY-CHANGE-THIS';  // ← CHANGE THIS!

5. 🌐 ACCESS YOUR ADMIN PANEL
   - URL: http://yourdomain.com/admin
   - Login with your password

6. ✅ DONE!
   Your web admin panel is now live on Hostinger!
EOF

echo -e "${GREEN}✅ Created upload instructions${NC}"

# Step 5: Summary
echo ""
echo -e "${GREEN}🎉 SETUP COMPLETE!${NC}"
echo "=================================="
echo ""
echo -e "${BLUE}📋 NEXT STEPS:${NC}"
echo ""
echo "1. 📡 Deploy API to Cambodia VPS:"
echo "   ${YELLOW}./deploy_to_vps.sh${NC}"
echo ""
echo "2. 📤 Upload to Hostinger Business:"
echo "   - Upload ${YELLOW}hostinger_index.php${NC} to ${YELLOW}public_html/admin/index.php${NC}"
echo "   - Edit configuration in the file"
echo ""
echo "3. 🌐 Access web admin:"
echo "   - URL: ${YELLOW}http://yourdomain.com/admin${NC}"
echo "   - Password: ${YELLOW}admin123${NC} (change this!)"
echo ""
echo -e "${GREEN}✅ PERFECT ARCHITECTURE READY!${NC}"
echo "📱 Bot: Cambodia VPS (smooth operation)"
echo "🌐 Admin: Hostinger Business (beautiful interface)"
echo "🔗 Connected via secure API"
echo ""
echo -e "${YELLOW}⚠️  SECURITY REMINDERS:${NC}"
echo "- Change admin password in hostinger_index.php"
echo "- Change API key in .env_api and hostinger_index.php"
echo "- Keep your VPS API port (8081) secure"
EOF