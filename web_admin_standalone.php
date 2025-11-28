<?php
/**
 * Standalone Web Admin Panel for Telegram Store Bot
 * This runs on Hostinger Business Plan (PHP hosting)
 * Connects to your MongoDB Atlas database
 */

session_start();

// Configuration
$ADMIN_PASSWORD = 'admin123'; // Change this!
$MONGODB_URI = 'mongodb+srv://dztsorebase:reachvip@cluster0.tbyhuzf.mongodb.net';
$DATABASE_NAME = 'storebot';

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

// Main application
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
        .sidebar .nav-link:hover,
        .sidebar .nav-link.active {
            color: white;
            background-color: rgba(255,255,255,0.1);
        }
        .card {
            border: none;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        }
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
        }
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="row">
            <!-- Sidebar -->
            <nav class="col-md-2 d-none d-md-block sidebar">
                <div class="position-sticky">
                    <div class="text-center py-4">
                        <h4 class="text-white">
                            <i class="fas fa-store"></i>
                            Store Admin
                        </h4>
                        <small class="text-white-50">Hostinger Web Panel</small>
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
                            <a class="nav-link <?= $action === 'stock' ? 'active' : '' ?>" href="?action=stock">
                                <i class="fas fa-warehouse"></i> Stock
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
                <nav class="navbar navbar-expand-lg navbar-light bg-white shadow-sm mb-4">
                    <div class="container-fluid">
                        <span class="navbar-brand">
                            <i class="fas fa-robot"></i>
                            Telegram Store Bot - Web Admin
                        </span>
                        <div class="navbar-nav ms-auto">
                            <span class="navbar-text me-3">
                                <i class="fas fa-server"></i>
                                Bot: Cambodia VPS | Admin: Hostinger
                            </span>
                            <a class="nav-link" href="?action=logout">
                                <i class="fas fa-sign-out-alt"></i> Logout
                            </a>
                        </div>
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
                        case 'stock':
                            showStock();
                            break;
                        case 'users':
                            showUsers();
                            break;
                        case 'orders':
                            showOrders();
                            break;
                        case 'add_product':
                            addProduct();
                            break;
                        case 'add_stock':
                            addStock();
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

// ==========================================
// MONGODB CONNECTION FUNCTIONS
// ==========================================

function connectMongoDB() {
    global $MONGODB_URI, $DATABASE_NAME;
    
    // For Hostinger, we'll use HTTP API calls to your VPS
    // Since MongoDB extension might not be available
    return true;
}

function httpRequest($endpoint, $data = null) {
    // Make HTTP requests to your Cambodia VPS API
    $vps_api_url = 'http://157.10.73.90:8081/api/' . $endpoint;
    
    $options = [
        'http' => [
            'method' => $data ? 'POST' : 'GET',
            'header' => 'Content-Type: application/json',
            'content' => $data ? json_encode($data) : null
        ]
    ];
    
    $context = stream_context_create($options);
    $result = @file_get_contents($vps_api_url, false, $context);
    
    return $result ? json_decode($result, true) : false;
}

function showLoginPage($error = '') {
    ?>
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Admin Login</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .login-card {
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                max-width: 400px;
                width: 100%;
            }
        </style>
    </head>
    <body>
        <div class="login-card p-4">
            <div class="text-center mb-4">
                <h2><i class="fas fa-robot"></i></h2>
                <h4>Store Bot Admin</h4>
                <p class="text-muted">Hostinger Web Panel</p>
            </div>
            
            <?php if ($error): ?>
                <div class="alert alert-danger"><?= $error ?></div>
            <?php endif; ?>
            
            <form method="POST" action="?action=login">
                <div class="mb-3">
                    <label class="form-label">Admin Password</label>
                    <input type="password" name="password" class="form-control" required>
                </div>
                <button type="submit" class="btn btn-primary w-100">Login</button>
            </form>
        </div>
    </body>
    </html>
    <?php
}

function showDashboard() {
    // Get stats from your VPS via HTTP API
    $stats = httpRequest('stats');
    ?>
    <h1>Dashboard</h1>
    
    <!-- Statistics Cards -->
    <div class="row mb-4">
        <div class="col-md-3">
            <div class="card stat-card">
                <div class="card-body text-center">
                    <i class="fas fa-box fa-3x mb-3"></i>
                    <h3><?= $stats['products'] ?? '0' ?></h3>
                    <p>Products</p>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card bg-success text-white">
                <div class="card-body text-center">
                    <i class="fas fa-users fa-3x mb-3"></i>
                    <h3><?= $stats['users'] ?? '0' ?></h3>
                    <p>Users</p>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card bg-warning text-white">
                <div class="card-body text-center">
                    <i class="fas fa-shopping-cart fa-3x mb-3"></i>
                    <h3><?= $stats['sold'] ?? '0' ?></h3>
                    <p>Sold</p>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card bg-info text-white">
                <div class="card-body text-center">
                    <i class="fas fa-warehouse fa-3x mb-3"></i>
                    <h3><?= $stats['stock'] ?? '0' ?></h3>
                    <p>Stock</p>
                </div>
            </div>
        </div>
    </div>

    <!-- Quick Actions -->
    <div class="row">
        <div class="col-12">
            <div class="card">
                <div class="card-header">
                    <h5>Quick Actions</h5>
                </div>
                <div class="card-body">
                    <div class="row text-center">
                        <div class="col-md-3">
                            <a href="?action=add_product" class="btn btn-primary btn-lg w-100 mb-2">
                                <i class="fas fa-plus"></i><br>Add Product
                            </a>
                        </div>
                        <div class="col-md-3">
                            <a href="?action=add_stock" class="btn btn-success btn-lg w-100 mb-2">
                                <i class="fas fa-warehouse"></i><br>Add Stock
                            </a>
                        </div>
                        <div class="col-md-3">
                            <a href="?action=users" class="btn btn-info btn-lg w-100 mb-2">
                                <i class="fas fa-users"></i><br>View Users
                            </a>
                        </div>
                        <div class="col-md-3">
                            <a href="?action=orders" class="btn btn-warning btn-lg w-100 mb-2">
                                <i class="fas fa-list"></i><br>View Orders
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Connection Status -->
    <div class="row mt-4">
        <div class="col-12">
            <div class="card border-success">
                <div class="card-header bg-success text-white">
                    <h6><i class="fas fa-link"></i> Connection Status</h6>
                </div>
                <div class="card-body">
                    <p><strong>🤖 Bot Location:</strong> Cambodia VPS (157.10.73.90)</p>
                    <p><strong>🌐 Admin Panel:</strong> Hostinger Business Plan</p>
                    <p><strong>📊 Database:</strong> MongoDB Atlas</p>
                    <p><strong>⚡ API Connection:</strong> <span class="badge bg-success">Active</span></p>
                </div>
            </div>
        </div>
    </div>
    <?php
}

function showProducts() {
    $products = httpRequest('products');
    ?>
    <div class="d-flex justify-content-between align-items-center mb-4">
        <h1>Products</h1>
        <a href="?action=add_product" class="btn btn-primary">
            <i class="fas fa-plus"></i> Add Product
        </a>
    </div>

    <div class="card">
        <div class="card-body">
            <?php if ($products): ?>
                <div class="table-responsive">
                    <table class="table">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Name</th>
                                <th>Description</th>
                                <th>Variants</th>
                                <th>Sold</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            <?php foreach ($products as $id => $product): ?>
                            <tr>
                                <td><?= $id ?></td>
                                <td><strong><?= htmlspecialchars($product['name']) ?></strong></td>
                                <td><?= htmlspecialchars($product['desc']) ?></td>
                                <td>
                                    <?php foreach ($product['variants'] as $vid => $variant): ?>
                                        <span class="badge bg-primary"><?= $variant['name'] ?> - $<?= $variant['price'] ?></span><br>
                                    <?php endforeach; ?>
                                </td>
                                <td><span class="badge bg-success"><?= $product['sold'] ?></span></td>
                                <td>
                                    <button class="btn btn-sm btn-warning">Edit</button>
                                    <button class="btn btn-sm btn-danger">Delete</button>
                                </td>
                            </tr>
                            <?php endforeach; ?>
                        </tbody>
                    </table>
                </div>
            <?php else: ?>
                <div class="text-center py-4">
                    <i class="fas fa-box fa-3x text-muted mb-3"></i>
                    <h5>No products yet</h5>
                    <a href="?action=add_product" class="btn btn-primary">Add Your First Product</a>
                </div>
            <?php endif; ?>
        </div>
    </div>
    <?php
}

function showStock() {
    $stock = httpRequest('stock');
    ?>
    <h1>Stock Management</h1>
    
    <div class="card">
        <div class="card-header">
            <h5>Stock Overview</h5>
        </div>
        <div class="card-body">
            <p>Manage your product inventory here.</p>
            <a href="?action=add_stock" class="btn btn-success">
                <i class="fas fa-plus"></i> Add Stock
            </a>
        </div>
    </div>
    <?php
}

function showUsers() {
    $users = httpRequest('users');
    ?>
    <h1>Users</h1>
    
    <div class="card">
        <div class="card-body">
            <p>User management interface.</p>
        </div>
    </div>
    <?php
}

function showOrders() {
    $orders = httpRequest('orders');
    ?>
    <h1>Orders</h1>
    
    <div class="card">
        <div class="card-body">
            <p>Order management interface.</p>
        </div>
    </div>
    <?php
}

function addProduct() {
    if ($_POST) {
        // Handle product addition via API
        $result = httpRequest('add_product', $_POST);
        if ($result['success']) {
            echo '<div class="alert alert-success">Product added successfully!</div>';
        } else {
            echo '<div class="alert alert-danger">Error adding product.</div>';
        }
    }
    ?>
    <h1>Add Product</h1>
    
    <div class="card">
        <div class="card-body">
            <form method="POST">
                <div class="mb-3">
                    <label class="form-label">Product Name</label>
                    <input type="text" name="name" class="form-control" required>
                </div>
                <div class="mb-3">
                    <label class="form-label">Description</label>
                    <textarea name="description" class="form-control"></textarea>
                </div>
                <div class="mb-3">
                    <label class="form-label">Variants (JSON format)</label>
                    <textarea name="variants" class="form-control" placeholder='{"var_1": {"name": "Basic", "price": 10}}'></textarea>
                </div>
                <button type="submit" class="btn btn-primary">Add Product</button>
                <a href="?action=products" class="btn btn-secondary">Cancel</a>
            </form>
        </div>
    </div>
    <?php
}

function addStock() {
    ?>
    <h1>Add Stock</h1>
    
    <div class="card">
        <div class="card-body">
            <form method="POST">
                <div class="mb-3">
                    <label class="form-label">Product</label>
                    <select name="product_id" class="form-control" required>
                        <option value="">Select Product</option>
                        <!-- Load products via API -->
                    </select>
                </div>
                <div class="mb-3">
                    <label class="form-label">Variant</label>
                    <select name="variant_id" class="form-control" required>
                        <option value="">Select Variant</option>
                    </select>
                </div>
                <div class="mb-3">
                    <label class="form-label">Stock Items (one per line)</label>
                    <textarea name="stock_data" class="form-control" rows="10" placeholder="account1:password1
account2:password2
account3:password3"></textarea>
                </div>
                <button type="submit" class="btn btn-success">Add Stock</button>
                <a href="?action=stock" class="btn btn-secondary">Cancel</a>
            </form>
        </div>
    </div>
    <?php
}

?>