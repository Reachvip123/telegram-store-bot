#!/usr/bin/env python3
"""
Premium Web Admin Panel for Cambodia VPS
Best Interface for MongoDB Management
Access at: http://157.10.73.90:8080
"""

from flask import Flask, render_template_string, request, redirect, url_for, flash, session, jsonify
import pymongo
from bson import ObjectId
import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
import re

load_dotenv()

app = Flask(__name__)
app.secret_key = 'premium-secret-key-2024'

# MongoDB connection
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb+srv://dztsorebase:reachvip@cluster0.tbyhuzf.mongodb.net")
DATABASE_NAME = os.getenv("DATABASE_NAME", "storebot")

# Admin password
ADMIN_PASSWORD = "admin123"

def get_db():
    """Get MongoDB database connection"""
    try:
        client = pymongo.MongoClient(MONGODB_URI)
        return client[DATABASE_NAME]
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def login_required(f):
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.route('/')
def index():
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password', '')
        if password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            flash('Welcome to Premium Admin Panel! 🎉', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid password!', 'error')
    
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>Premium Store Bot Admin</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .login-card {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            box-shadow: 0 25px 50px rgba(0,0,0,0.15);
            backdrop-filter: blur(10px);
            max-width: 450px;
            width: 100%;
            overflow: hidden;
        }
        .login-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            text-align: center;
        }
        .btn-premium {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            padding: 12px 24px;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        .btn-premium:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
        }
    </style>
</head>
<body>
    <div class="login-card">
        <div class="login-header">
            <i class="fas fa-crown fa-3x mb-3"></i>
            <h3>Premium Store Admin</h3>
            <p class="mb-0">Advanced MongoDB Management</p>
        </div>
        
        <div class="p-4">
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    {% for category, message in messages %}
                        <div class="alert alert-{{ 'danger' if category == 'error' else 'success' }} mb-3">
                            {{ message }}
                        </div>
                    {% endfor %}
                {% endif %}
            {% endwith %}
            
            <form method="POST">
                <div class="mb-4">
                    <div class="input-group">
                        <span class="input-group-text"><i class="fas fa-lock"></i></span>
                        <input type="password" name="password" class="form-control form-control-lg" 
                               placeholder="Enter admin password" required>
                    </div>
                </div>
                <button type="submit" class="btn btn-premium btn-lg w-100">
                    <i class="fas fa-sign-in-alt me-2"></i>Access Admin Panel
                </button>
            </form>
            
            <div class="text-center mt-4">
                <small class="text-muted">
                    <i class="fas fa-server me-1"></i>Cambodia VPS • 
                    <i class="fas fa-database me-1"></i>MongoDB Atlas
                </small>
            </div>
        </div>
    </div>
</body>
</html>
    ''')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    try:
        db = get_db()
        if not db:
            flash('Database connection failed!', 'error')
            return redirect(url_for('login'))
        
        # Enhanced statistics
        products_count = db.products.count_documents({})
        users_count = db.users.count_documents({})
        
        # Revenue calculations
        total_sold_pipeline = [{'$group': {'_id': None, 'total_sold': {'$sum': '$sold'}}}]
        sold_result = list(db.products.aggregate(total_sold_pipeline))
        total_sold = sold_result[0]['total_sold'] if sold_result else 0
        
        # Calculate revenue from users collection
        revenue_pipeline = [{'$group': {'_id': None, 'total_revenue': {'$sum': '$spent'}}}]
        revenue_result = list(db.users.aggregate(revenue_pipeline))
        total_revenue = revenue_result[0]['total_revenue'] if revenue_result else 0
        
        # Stock statistics
        total_stock = db.stock.count_documents({'sold': False})
        sold_stock = db.stock.count_documents({'sold': True})
        
        # Recent activity (last 7 days)
        week_ago = datetime.now() - timedelta(days=7)
        new_users_week = db.users.count_documents({'joined_at': {'$gte': week_ago}}) if 'joined_at' in db.users.find_one({}) or {} else 0
        
        # Top products
        top_products = list(db.products.find({}).sort('sold', -1).limit(5))
        
        stats = {
            'products': products_count,
            'users': users_count,
            'sold': total_sold,
            'stock': total_stock,
            'revenue': total_revenue,
            'sold_stock': sold_stock,
            'new_users_week': new_users_week,
            'top_products': top_products
        }
        
        return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>Premium Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/chart.js@4.0.0/dist/chart.min.js" rel="stylesheet">
    <style>
        body { background: #f8f9fa; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        .navbar-premium { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .stat-card { border: none; border-radius: 15px; box-shadow: 0 8px 25px rgba(0,0,0,0.08); transition: all 0.3s ease; }
        .stat-card:hover { transform: translateY(-5px); box-shadow: 0 15px 35px rgba(0,0,0,0.15); }
        .stat-icon { font-size: 2.5rem; opacity: 0.8; }
        .gradient-1 { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .gradient-2 { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
        .gradient-3 { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }
        .gradient-4 { background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); }
        .gradient-5 { background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); }
        .gradient-6 { background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); }
        .btn-premium { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border: none; }
        .btn-premium:hover { transform: translateY(-2px); }
    </style>
</head>
<body>
    <nav class="navbar navbar-dark navbar-premium">
        <div class="container-fluid">
            <a class="navbar-brand" href="#">
                <i class="fas fa-crown me-2"></i>Premium Store Admin
            </a>
            <div class="d-flex">
                <a href="{{ url_for('products') }}" class="btn btn-outline-light me-2">
                    <i class="fas fa-box me-1"></i>Products
                </a>
                <a href="{{ url_for('stock_management') }}" class="btn btn-outline-light me-2">
                    <i class="fas fa-warehouse me-1"></i>Stock
                </a>
                <a href="{{ url_for('users') }}" class="btn btn-outline-light me-2">
                    <i class="fas fa-users me-1"></i>Users
                </a>
                <div class="dropdown">
                    <button class="btn btn-outline-light dropdown-toggle" type="button" data-bs-toggle="dropdown">
                        <i class="fas fa-user-crown me-1"></i>Admin
                    </button>
                    <ul class="dropdown-menu">
                        <li><a class="dropdown-item" href="{{ url_for('database_tools') }}">
                            <i class="fas fa-database me-2"></i>Database Tools
                        </a></li>
                        <li><hr class="dropdown-divider"></li>
                        <li><a class="dropdown-item" href="{{ url_for('logout') }}">
                            <i class="fas fa-sign-out-alt me-2"></i>Logout
                        </a></li>
                    </ul>
                </div>
            </div>
        </div>
    </nav>

    <div class="container-fluid mt-4">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ 'danger' if category == 'error' else 'success' }} alert-dismissible fade show">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}

        <div class="row mb-4">
            <div class="col-12">
                <h1 class="display-6 fw-bold text-dark mb-0">
                    <i class="fas fa-chart-line text-primary me-3"></i>Premium Dashboard
                </h1>
                <p class="text-muted">Advanced MongoDB Store Management</p>
            </div>
        </div>
        
        <!-- Main Stats Row -->
        <div class="row g-4 mb-4">
            <div class="col-xl-2 col-lg-4 col-md-6">
                <div class="card stat-card gradient-1 text-white">
                    <div class="card-body text-center">
                        <i class="fas fa-box stat-icon mb-3"></i>
                        <h3 class="fw-bold">{{ stats.products }}</h3>
                        <p class="mb-0">Products</p>
                    </div>
                </div>
            </div>
            <div class="col-xl-2 col-lg-4 col-md-6">
                <div class="card stat-card gradient-2 text-white">
                    <div class="card-body text-center">
                        <i class="fas fa-users stat-icon mb-3"></i>
                        <h3 class="fw-bold">{{ stats.users }}</h3>
                        <p class="mb-0">Total Users</p>
                    </div>
                </div>
            </div>
            <div class="col-xl-2 col-lg-4 col-md-6">
                <div class="card stat-card gradient-3 text-white">
                    <div class="card-body text-center">
                        <i class="fas fa-dollar-sign stat-icon mb-3"></i>
                        <h3 class="fw-bold">${{ "%.0f"|format(stats.revenue) }}</h3>
                        <p class="mb-0">Revenue</p>
                    </div>
                </div>
            </div>
            <div class="col-xl-2 col-lg-4 col-md-6">
                <div class="card stat-card gradient-4 text-white">
                    <div class="card-body text-center">
                        <i class="fas fa-shopping-cart stat-icon mb-3"></i>
                        <h3 class="fw-bold">{{ stats.sold }}</h3>
                        <p class="mb-0">Items Sold</p>
                    </div>
                </div>
            </div>
            <div class="col-xl-2 col-lg-4 col-md-6">
                <div class="card stat-card gradient-5 text-white">
                    <div class="card-body text-center">
                        <i class="fas fa-warehouse stat-icon mb-3"></i>
                        <h3 class="fw-bold">{{ stats.stock }}</h3>
                        <p class="mb-0">In Stock</p>
                    </div>
                </div>
            </div>
            <div class="col-xl-2 col-lg-4 col-md-6">
                <div class="card stat-card gradient-6 text-dark">
                    <div class="card-body text-center">
                        <i class="fas fa-user-plus stat-icon mb-3"></i>
                        <h3 class="fw-bold">{{ stats.new_users_week }}</h3>
                        <p class="mb-0">New (7d)</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- Quick Actions & Top Products -->
        <div class="row g-4">
            <div class="col-lg-6">
                <div class="card stat-card">
                    <div class="card-header bg-gradient-primary text-white">
                        <h5 class="mb-0"><i class="fas fa-rocket me-2"></i>Quick Actions</h5>
                    </div>
                    <div class="card-body">
                        <div class="row g-3">
                            <div class="col-md-6">
                                <a href="{{ url_for('products') }}" class="btn btn-premium w-100">
                                    <i class="fas fa-box me-2"></i>Manage Products
                                </a>
                            </div>
                            <div class="col-md-6">
                                <a href="{{ url_for('stock_management') }}" class="btn btn-success w-100">
                                    <i class="fas fa-warehouse me-2"></i>Manage Stock
                                </a>
                            </div>
                            <div class="col-md-6">
                                <a href="{{ url_for('users') }}" class="btn btn-info w-100">
                                    <i class="fas fa-users me-2"></i>View Users
                                </a>
                            </div>
                            <div class="col-md-6">
                                <a href="{{ url_for('database_tools') }}" class="btn btn-warning w-100">
                                    <i class="fas fa-database me-2"></i>Database Tools
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="col-lg-6">
                <div class="card stat-card">
                    <div class="card-header bg-success text-white">
                        <h5 class="mb-0"><i class="fas fa-trophy me-2"></i>Top Products</h5>
                    </div>
                    <div class="card-body">
                        {% if stats.top_products %}
                            {% for product in stats.top_products %}
                            <div class="d-flex justify-content-between align-items-center mb-2 p-2 bg-light rounded">
                                <div>
                                    <strong>{{ product.name }}</strong>
                                    <small class="text-muted d-block">{{ product.desc[:50] }}...</small>
                                </div>
                                <span class="badge bg-success">{{ product.sold }} sold</span>
                            </div>
                            {% endfor %}
                        {% else %}
                            <p class="text-muted text-center mb-0">No products yet</p>
                        {% endif %}
                    </div>
                </div>
            </div>
        </div>

        <!-- System Info -->
        <div class="row mt-4">
            <div class="col-12">
                <div class="card stat-card border-success">
                    <div class="card-header bg-success text-white">
                        <h6 class="mb-0"><i class="fas fa-server me-2"></i>System Information</h6>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-3">
                                <strong>Location:</strong> Cambodia VPS
                            </div>
                            <div class="col-md-3">
                                <strong>IP:</strong> 157.10.73.90
                            </div>
                            <div class="col-md-3">
                                <strong>Database:</strong> MongoDB Atlas
                            </div>
                            <div class="col-md-3">
                                <strong>Status:</strong> <span class="badge bg-success">Online</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
        ''', stats=stats)
    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}', 'error')
        return redirect(url_for('login'))

@app.route('/database_tools')
@login_required  
def database_tools():
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>Database Tools - Premium Admin</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background: #f8f9fa; }
        .navbar-premium { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .tool-card { border: none; border-radius: 15px; box-shadow: 0 8px 25px rgba(0,0,0,0.08); transition: all 0.3s ease; }
        .tool-card:hover { transform: translateY(-5px); }
    </style>
</head>
<body>
    <nav class="navbar navbar-dark navbar-premium">
        <div class="container-fluid">
            <a class="navbar-brand" href="{{ url_for('dashboard') }}">
                <i class="fas fa-crown me-2"></i>Premium Store Admin
            </a>
            <div>
                <a href="{{ url_for('dashboard') }}" class="btn btn-outline-light">
                    <i class="fas fa-arrow-left me-1"></i>Back to Dashboard
                </a>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <h1 class="display-6 fw-bold mb-4">
            <i class="fas fa-database text-primary me-3"></i>Database Management Tools
        </h1>
        
        <div class="row g-4">
            <div class="col-md-6">
                <div class="card tool-card">
                    <div class="card-header bg-primary text-white">
                        <h5 class="mb-0"><i class="fas fa-search me-2"></i>Database Explorer</h5>
                    </div>
                    <div class="card-body">
                        <p>Browse and search all collections in your MongoDB database</p>
                        <a href="{{ url_for('db_explorer') }}" class="btn btn-primary">
                            <i class="fas fa-eye me-2"></i>Explore Database
                        </a>
                    </div>
                </div>
            </div>
            
            <div class="col-md-6">
                <div class="card tool-card">
                    <div class="card-header bg-success text-white">
                        <h5 class="mb-0"><i class="fas fa-download me-2"></i>Data Export</h5>
                    </div>
                    <div class="card-body">
                        <p>Export your data to JSON format for backup</p>
                        <a href="{{ url_for('export_data') }}" class="btn btn-success">
                            <i class="fas fa-file-export me-2"></i>Export Data
                        </a>
                    </div>
                </div>
            </div>
            
            <div class="col-md-6">
                <div class="card tool-card">
                    <div class="card-header bg-warning text-white">
                        <h5 class="mb-0"><i class="fas fa-chart-bar me-2"></i>Analytics</h5>
                    </div>
                    <div class="card-body">
                        <p>Advanced analytics and reports</p>
                        <a href="{{ url_for('analytics') }}" class="btn btn-warning">
                            <i class="fas fa-chart-line me-2"></i>View Analytics
                        </a>
                    </div>
                </div>
            </div>
            
            <div class="col-md-6">
                <div class="card tool-card">
                    <div class="card-header bg-info text-white">
                        <h5 class="mb-0"><i class="fas fa-broom me-2"></i>Cleanup Tools</h5>
                    </div>
                    <div class="card-body">
                        <p>Clean up old data and optimize database</p>
                        <a href="{{ url_for('cleanup_tools') }}" class="btn btn-info">
                            <i class="fas fa-tools me-2"></i>Cleanup Tools
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
    ''')

# ... (continuing with more routes in next part due to length)
@app.route('/db_explorer')
@login_required
def db_explorer():
    try:
        db = get_db()
        collections = db.list_collection_names()
        
        # Get sample data from each collection
        collection_info = {}
        for col_name in collections:
            count = db[col_name].count_documents({})
            sample = list(db[col_name].find({}).limit(1))
            collection_info[col_name] = {
                'count': count,
                'sample': sample[0] if sample else None
            }
        
        return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>Database Explorer - Premium Admin</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background: #f8f9fa; }
        .navbar-premium { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .collection-card { border: none; border-radius: 10px; box-shadow: 0 5px 15px rgba(0,0,0,0.08); }
        .json-view { background: #f8f9fa; border-radius: 8px; font-family: 'Courier New', monospace; }
    </style>
</head>
<body>
    <nav class="navbar navbar-dark navbar-premium">
        <div class="container-fluid">
            <a class="navbar-brand" href="{{ url_for('dashboard') }}">
                <i class="fas fa-crown me-2"></i>Premium Store Admin
            </a>
            <div>
                <a href="{{ url_for('database_tools') }}" class="btn btn-outline-light">
                    <i class="fas fa-arrow-left me-1"></i>Back to Tools
                </a>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <h1 class="display-6 fw-bold mb-4">
            <i class="fas fa-search text-primary me-3"></i>Database Explorer
        </h1>
        
        {% for col_name, info in collections.items() %}
        <div class="card collection-card mb-4">
            <div class="card-header bg-primary text-white">
                <h5 class="mb-0">
                    <i class="fas fa-table me-2"></i>{{ col_name }}
                    <span class="badge bg-light text-dark ms-2">{{ info.count }} documents</span>
                </h5>
            </div>
            <div class="card-body">
                {% if info.sample %}
                    <h6>Sample Document:</h6>
                    <pre class="json-view p-3">{{ info.sample | tojsonpretty }}</pre>
                {% else %}
                    <p class="text-muted">No documents in this collection</p>
                {% endif %}
                <div class="mt-3">
                    <a href="{{ url_for('view_collection', collection=col_name) }}" class="btn btn-primary btn-sm">
                        <i class="fas fa-eye me-1"></i>View All Documents
                    </a>
                </div>
            </div>
        </div>
        {% endfor %}
    </div>
</body>
</html>
        ''', collections=collection_info)
    except Exception as e:
        flash(f'Error exploring database: {str(e)}', 'error')
        return redirect(url_for('database_tools'))

if __name__ == '__main__':
    import sys
    
    # Default to port 8080 for better compatibility
    port = 8080
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            port = 8080
    
    print("\n" + "="*70)
    print("👑 PREMIUM WEB ADMIN PANEL")
    print("="*70)
    print(f"🎯 Best Interface for MongoDB Management")
    print(f"📡 Location: Cambodia VPS")
    print(f"🌐 Access URL: http://157.10.73.90:{port}")
    print(f"🔑 Password: {ADMIN_PASSWORD}")
    print("="*70 + "\n")
    print("✨ PREMIUM FEATURES:")
    print("  🎨 Beautiful modern interface")
    print("  📊 Advanced dashboard with analytics") 
    print("  💰 Revenue tracking")
    print("  🏆 Top products analysis")
    print("  🔍 Database explorer")
    print("  📈 Stock management")
    print("  👥 User management")
    print("  🛠️ Database tools")
    print("  📱 Mobile responsive")
    print("  🎯 Easy stock adding")
    print(f"\n🚀 Starting premium server on port {port}...")
    print("="*70 + "\n")
    
    try:
        app.run(host='0.0.0.0', port=port, debug=False)
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"\n❌ Port {port} is already in use!")
            print(f"🔧 Try: python3 premium_admin.py 3000")
        else:
            print(f"\n❌ Error: {e}")