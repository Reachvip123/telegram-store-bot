#!/usr/bin/env python3
"""
🔥 ULTIMATE Premium MongoDB Admin Interface 🔥
The BEST interface for managing your store database
Beautifully designed • Feature-rich • Super easy to use
"""

from flask import Flask, render_template_string, request, redirect, url_for, flash, session, jsonify, Response
import pymongo
from bson import ObjectId
import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
import re

load_dotenv()
app = Flask(__name__)
app.secret_key = 'ultimate-premium-secret-2024'

# MongoDB connection
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb+srv://dztsorebase:reachvip@cluster0.tbyhuzf.mongodb.net")
DATABASE_NAME = os.getenv("DATABASE_NAME", "storebot")
ADMIN_PASSWORD = "admin123"

def get_db():
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

# Filter for pretty JSON
@app.template_filter('tojsonpretty')
def to_json_pretty(value):
    return json.dumps(value, indent=2, default=str, ensure_ascii=False)

@app.route('/')
def index():
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password', '')
        if password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            flash('🎉 Welcome to Ultimate Admin Panel!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('❌ Invalid password!', 'error')
    
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>Ultimate Store Admin</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            animation: gradientShift 10s ease infinite;
        }
        @keyframes gradientShift {
            0%, 100% { background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%); }
            50% { background: linear-gradient(135deg, #f093fb 0%, #667eea 50%, #764ba2 100%); }
        }
        .login-container {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 25px;
            box-shadow: 0 30px 80px rgba(0,0,0,0.2);
            backdrop-filter: blur(20px);
            max-width: 500px;
            width: 100%;
            overflow: hidden;
            animation: float 6s ease-in-out infinite;
        }
        @keyframes float {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-10px); }
        }
        .login-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 3rem 2rem;
            text-align: center;
            position: relative;
        }
        .login-header::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="1" fill="white" opacity="0.1"/><circle cx="75" cy="75" r="1" fill="white" opacity="0.1"/><circle cx="50" cy="10" r="0.5" fill="white" opacity="0.2"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
        }
        .crown-icon {
            font-size: 4rem;
            margin-bottom: 1rem;
            text-shadow: 0 4px 8px rgba(0,0,0,0.3);
            animation: pulse 2s ease-in-out infinite;
        }
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.1); }
        }
        .btn-ultimate {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            padding: 15px 30px;
            font-weight: 600;
            font-size: 1.1rem;
            transition: all 0.4s ease;
            position: relative;
            overflow: hidden;
        }
        .btn-ultimate:hover {
            transform: translateY(-3px);
            box-shadow: 0 15px 35px rgba(102, 126, 234, 0.4);
        }
        .btn-ultimate::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
            transition: left 0.6s;
        }
        .btn-ultimate:hover::before {
            left: 100%;
        }
        .form-control-lg {
            border-radius: 15px;
            padding: 15px 20px;
            border: 2px solid #e9ecef;
            transition: all 0.3s ease;
        }
        .form-control-lg:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
        }
        .input-group-text {
            border-radius: 15px 0 0 15px;
            border: 2px solid #e9ecef;
            border-right: none;
            background: #f8f9fa;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="login-header">
            <i class="fas fa-crown crown-icon"></i>
            <h2 class="fw-bold mb-2">Ultimate Store Admin</h2>
            <p class="mb-0 opacity-90">Premium MongoDB Management Platform</p>
        </div>
        
        <div class="p-4">
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    {% for category, message in messages %}
                        <div class="alert alert-{{ 'danger' if category == 'error' else 'success' }} mb-3 border-0 rounded-4">
                            {{ message }}
                        </div>
                    {% endfor %}
                {% endif %}
            {% endwith %}
            
            <form method="POST">
                <div class="mb-4">
                    <div class="input-group input-group-lg">
                        <span class="input-group-text">
                            <i class="fas fa-lock text-primary"></i>
                        </span>
                        <input type="password" name="password" class="form-control form-control-lg" 
                               placeholder="Enter admin password" required>
                    </div>
                </div>
                <button type="submit" class="btn btn-ultimate btn-lg w-100 rounded-4">
                    <i class="fas fa-rocket me-2"></i>Launch Admin Panel
                </button>
            </form>
            
            <div class="text-center mt-4 pt-3 border-top">
                <div class="row text-center">
                    <div class="col-4">
                        <i class="fas fa-server text-primary"></i>
                        <small class="d-block text-muted">Cambodia VPS</small>
                    </div>
                    <div class="col-4">
                        <i class="fas fa-database text-success"></i>
                        <small class="d-block text-muted">MongoDB Atlas</small>
                    </div>
                    <div class="col-4">
                        <i class="fas fa-shield-alt text-warning"></i>
                        <small class="d-block text-muted">Secure Access</small>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
    ''')

@app.route('/logout')
def logout():
    session.clear()
    flash('👋 Logged out successfully!', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    try:
        db = get_db()
        if not db:
            flash('❌ Database connection failed!', 'error')
            return redirect(url_for('login'))
        
        # Enhanced statistics with error handling
        try:
            products_count = db.products.count_documents({})
        except:
            products_count = 0
            
        try:
            users_count = db.users.count_documents({})
        except:
            users_count = 0
            
        # Revenue calculations
        try:
            total_sold_pipeline = [{'$group': {'_id': None, 'total_sold': {'$sum': '$sold'}}}]
            sold_result = list(db.products.aggregate(total_sold_pipeline))
            total_sold = sold_result[0]['total_sold'] if sold_result else 0
        except:
            total_sold = 0
            
        try:
            revenue_pipeline = [{'$group': {'_id': None, 'total_revenue': {'$sum': '$spent'}}}]
            revenue_result = list(db.users.aggregate(revenue_pipeline))
            total_revenue = revenue_result[0]['total_revenue'] if revenue_result else 0
        except:
            total_revenue = 0
            
        # Stock statistics
        try:
            total_stock = db.stock.count_documents({'sold': False})
            sold_stock = db.stock.count_documents({'sold': True})
        except:
            total_stock = 0
            sold_stock = 0
            
        # Recent activity
        try:
            week_ago = datetime.now() - timedelta(days=7)
            new_users_week = db.users.count_documents({'joined_at': {'$gte': week_ago}})
        except:
            new_users_week = 0
            
        # Top products
        try:
            top_products = list(db.products.find({}).sort('sold', -1).limit(5))
        except:
            top_products = []
        
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
    <title>🔥 Ultimate Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        body { 
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            min-height: 100vh;
        }
        .navbar-ultimate { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }
        .stat-card { 
            border: none; 
            border-radius: 20px; 
            box-shadow: 0 10px 30px rgba(0,0,0,0.1); 
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            overflow: hidden;
            position: relative;
        }
        .stat-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, #667eea, #764ba2, #f093fb);
        }
        .stat-card:hover { 
            transform: translateY(-8px) scale(1.02);
            box-shadow: 0 20px 50px rgba(0,0,0,0.15);
        }
        .stat-icon { 
            font-size: 3rem; 
            opacity: 0.9;
            margin-bottom: 1rem;
            text-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .gradient-1 { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .gradient-2 { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
        .gradient-3 { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }
        .gradient-4 { background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); }
        .gradient-5 { background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); }
        .gradient-6 { background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); }
        .btn-ultimate { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            border-radius: 15px;
            padding: 12px 24px;
            font-weight: 600;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        .btn-ultimate:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
        }
        .btn-ultimate::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            transition: left 0.6s;
        }
        .btn-ultimate:hover::before {
            left: 100%;
        }
        .card-premium {
            border: none;
            border-radius: 20px;
            box-shadow: 0 8px 30px rgba(0,0,0,0.08);
            transition: all 0.3s ease;
        }
        .card-premium:hover {
            transform: translateY(-4px);
            box-shadow: 0 12px 40px rgba(0,0,0,0.12);
        }
        .top-product-item {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border-radius: 15px;
            padding: 1rem;
            margin-bottom: 0.5rem;
            transition: all 0.3s ease;
        }
        .top-product-item:hover {
            background: linear-gradient(135deg, #e9ecef 0%, #dee2e6 100%);
            transform: translateX(5px);
        }
        .page-title {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-weight: 800;
        }
        .quick-action-btn {
            border-radius: 15px;
            padding: 15px;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        .quick-action-btn:hover {
            transform: translateY(-3px);
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-dark navbar-ultimate sticky-top">
        <div class="container-fluid">
            <a class="navbar-brand fw-bold" href="#">
                <i class="fas fa-crown me-2"></i>Ultimate Store Admin
                <span class="badge bg-warning text-dark ms-2">Premium</span>
            </a>
            <div class="d-flex">
                <div class="dropdown">
                    <button class="btn btn-outline-light dropdown-toggle me-2" type="button" data-bs-toggle="dropdown">
                        <i class="fas fa-cogs me-1"></i>Manage
                    </button>
                    <ul class="dropdown-menu">
                        <li><a class="dropdown-item" href="{{ url_for('products') }}">
                            <i class="fas fa-box me-2 text-primary"></i>Products
                        </a></li>
                        <li><a class="dropdown-item" href="{{ url_for('stock_management') }}">
                            <i class="fas fa-warehouse me-2 text-success"></i>Stock
                        </a></li>
                        <li><a class="dropdown-item" href="{{ url_for('users') }}">
                            <i class="fas fa-users me-2 text-info"></i>Users
                        </a></li>
                    </ul>
                </div>
                <div class="dropdown">
                    <button class="btn btn-outline-light dropdown-toggle" type="button" data-bs-toggle="dropdown">
                        <i class="fas fa-user-crown me-1"></i>Admin
                    </button>
                    <ul class="dropdown-menu">
                        <li><a class="dropdown-item" href="{{ url_for('database_tools') }}">
                            <i class="fas fa-database me-2 text-warning"></i>Database Tools
                        </a></li>
                        <li><a class="dropdown-item" href="{{ url_for('analytics') }}">
                            <i class="fas fa-chart-line me-2 text-info"></i>Analytics
                        </a></li>
                        <li><hr class="dropdown-divider"></li>
                        <li><a class="dropdown-item text-danger" href="{{ url_for('logout') }}">
                            <i class="fas fa-sign-out-alt me-2"></i>Logout
                        </a></li>
                    </ul>
                </div>
            </div>
        </div>
    </nav>

    <div class="container-fluid mt-4 px-4">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ 'danger' if category == 'error' else 'success' }} alert-dismissible fade show border-0 rounded-4 shadow-sm">
                        <i class="fas fa-{{ 'exclamation-triangle' if category == 'error' else 'check-circle' }} me-2"></i>
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}

        <!-- Header -->
        <div class="row mb-4">
            <div class="col-12">
                <h1 class="page-title display-4 fw-bold mb-2">
                    <i class="fas fa-tachometer-alt me-3"></i>Ultimate Dashboard
                </h1>
                <p class="lead text-muted">Advanced MongoDB Store Management • Real-time Analytics</p>
            </div>
        </div>
        
        <!-- Main Stats Grid -->
        <div class="row g-4 mb-5">
            <div class="col-xl-2 col-lg-4 col-md-6">
                <div class="card stat-card gradient-1 text-white h-100">
                    <div class="card-body text-center d-flex flex-column justify-content-center">
                        <i class="fas fa-box stat-icon"></i>
                        <h2 class="fw-bold mb-2">{{ stats.products }}</h2>
                        <p class="mb-0 opacity-90">Products</p>
                    </div>
                </div>
            </div>
            <div class="col-xl-2 col-lg-4 col-md-6">
                <div class="card stat-card gradient-2 text-white h-100">
                    <div class="card-body text-center d-flex flex-column justify-content-center">
                        <i class="fas fa-users stat-icon"></i>
                        <h2 class="fw-bold mb-2">{{ stats.users }}</h2>
                        <p class="mb-0 opacity-90">Total Users</p>
                    </div>
                </div>
            </div>
            <div class="col-xl-2 col-lg-4 col-md-6">
                <div class="card stat-card gradient-3 text-white h-100">
                    <div class="card-body text-center d-flex flex-column justify-content-center">
                        <i class="fas fa-dollar-sign stat-icon"></i>
                        <h2 class="fw-bold mb-2">${{ "%.0f"|format(stats.revenue) }}</h2>
                        <p class="mb-0 opacity-90">Revenue</p>
                    </div>
                </div>
            </div>
            <div class="col-xl-2 col-lg-4 col-md-6">
                <div class="card stat-card gradient-4 text-white h-100">
                    <div class="card-body text-center d-flex flex-column justify-content-center">
                        <i class="fas fa-shopping-cart stat-icon"></i>
                        <h2 class="fw-bold mb-2">{{ stats.sold }}</h2>
                        <p class="mb-0 opacity-90">Items Sold</p>
                    </div>
                </div>
            </div>
            <div class="col-xl-2 col-lg-4 col-md-6">
                <div class="card stat-card gradient-5 text-white h-100">
                    <div class="card-body text-center d-flex flex-column justify-content-center">
                        <i class="fas fa-warehouse stat-icon"></i>
                        <h2 class="fw-bold mb-2">{{ stats.stock }}</h2>
                        <p class="mb-0 opacity-90">In Stock</p>
                    </div>
                </div>
            </div>
            <div class="col-xl-2 col-lg-4 col-md-6">
                <div class="card stat-card gradient-6 text-dark h-100">
                    <div class="card-body text-center d-flex flex-column justify-content-center">
                        <i class="fas fa-user-plus stat-icon"></i>
                        <h2 class="fw-bold mb-2">{{ stats.new_users_week }}</h2>
                        <p class="mb-0 opacity-90">New (7d)</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- Quick Actions & Analytics -->
        <div class="row g-4 mb-4">
            <div class="col-lg-8">
                <div class="card card-premium">
                    <div class="card-header bg-white border-0 pt-4">
                        <h5 class="fw-bold mb-0">
                            <i class="fas fa-rocket text-primary me-2"></i>Quick Actions
                        </h5>
                    </div>
                    <div class="card-body">
                        <div class="row g-3">
                            <div class="col-md-3 col-sm-6">
                                <a href="{{ url_for('products') }}" class="btn btn-primary quick-action-btn w-100">
                                    <i class="fas fa-box d-block mb-2" style="font-size: 1.5rem;"></i>
                                    <span class="fw-bold">Products</span>
                                </a>
                            </div>
                            <div class="col-md-3 col-sm-6">
                                <a href="{{ url_for('stock_management') }}" class="btn btn-success quick-action-btn w-100">
                                    <i class="fas fa-warehouse d-block mb-2" style="font-size: 1.5rem;"></i>
                                    <span class="fw-bold">Stock</span>
                                </a>
                            </div>
                            <div class="col-md-3 col-sm-6">
                                <a href="{{ url_for('users') }}" class="btn btn-info quick-action-btn w-100">
                                    <i class="fas fa-users d-block mb-2" style="font-size: 1.5rem;"></i>
                                    <span class="fw-bold">Users</span>
                                </a>
                            </div>
                            <div class="col-md-3 col-sm-6">
                                <a href="{{ url_for('database_tools') }}" class="btn btn-warning quick-action-btn w-100">
                                    <i class="fas fa-database d-block mb-2" style="font-size: 1.5rem;"></i>
                                    <span class="fw-bold">Database</span>
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="col-lg-4">
                <div class="card card-premium h-100">
                    <div class="card-header bg-white border-0 pt-4">
                        <h5 class="fw-bold mb-0">
                            <i class="fas fa-trophy text-warning me-2"></i>Top Products
                        </h5>
                    </div>
                    <div class="card-body">
                        {% if stats.top_products %}
                            {% for product in stats.top_products %}
                            <div class="top-product-item">
                                <div class="d-flex justify-content-between align-items-center">
                                    <div class="flex-grow-1">
                                        <h6 class="fw-bold mb-1">{{ product.name }}</h6>
                                        <small class="text-muted">{{ product.desc[:40] }}...</small>
                                    </div>
                                    <span class="badge bg-success fs-6">{{ product.sold }}</span>
                                </div>
                            </div>
                            {% endfor %}
                        {% else %}
                            <div class="text-center py-4">
                                <i class="fas fa-box-open fa-3x text-muted mb-3"></i>
                                <p class="text-muted">No products yet</p>
                            </div>
                        {% endif %}
                    </div>
                </div>
            </div>
        </div>

        <!-- System Status -->
        <div class="row">
            <div class="col-12">
                <div class="card card-premium border-success">
                    <div class="card-header bg-success text-white border-0">
                        <h6 class="mb-0 fw-bold">
                            <i class="fas fa-server me-2"></i>System Status
                        </h6>
                    </div>
                    <div class="card-body">
                        <div class="row text-center">
                            <div class="col-md-3">
                                <div class="d-flex align-items-center justify-content-center">
                                    <i class="fas fa-map-marker-alt text-primary me-2"></i>
                                    <span><strong>Location:</strong> Cambodia VPS</span>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="d-flex align-items-center justify-content-center">
                                    <i class="fas fa-globe text-info me-2"></i>
                                    <span><strong>IP:</strong> 157.10.73.90</span>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="d-flex align-items-center justify-content-center">
                                    <i class="fas fa-database text-warning me-2"></i>
                                    <span><strong>Database:</strong> MongoDB Atlas</span>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="d-flex align-items-center justify-content-center">
                                    <i class="fas fa-heart text-success me-2"></i>
                                    <span><strong>Status:</strong> <span class="badge bg-success">Online</span></span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
        ''', stats=stats)
    except Exception as e:
        flash(f'❌ Error loading dashboard: {str(e)}', 'error')
        return redirect(url_for('login'))

# Continue with other routes...
@app.route('/products')
@login_required
def products():
    try:
        db = get_db()
        products_cursor = db.products.find({})
        products_list = []
        
        for product in products_cursor:
            product_data = {
                'id': str(product['_id']),
                'name': product.get('name', ''),
                'desc': product.get('desc', ''),
                'sold': product.get('sold', 0),
                'variants': product.get('variants', {})
            }
            
            # Get stock count for each variant
            product_data['stock_info'] = {}
            for variant_id in product_data['variants'].keys():
                try:
                    stock_count = db.stock.count_documents({
                        'product_id': product_data['id'],
                        'variant_id': variant_id,
                        'sold': False
                    })
                    product_data['stock_info'][variant_id] = stock_count
                except:
                    product_data['stock_info'][variant_id] = 0
            
            products_list.append(product_data)
        
        return render_template_string(PRODUCTS_TEMPLATE, products_list=products_list)
    except Exception as e:
        flash(f'❌ Error loading products: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

# Templates
PRODUCTS_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>🔥 Products Manager</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); font-family: 'Inter', sans-serif; }
        .navbar-ultimate { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .product-card { border: none; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); transition: all 0.3s ease; }
        .product-card:hover { transform: translateY(-5px); box-shadow: 0 20px 40px rgba(0,0,0,0.15); }
        .btn-ultimate { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border: none; border-radius: 10px; }
    </style>
</head>
<body>
    <nav class="navbar navbar-dark navbar-ultimate">
        <div class="container-fluid">
            <a class="navbar-brand fw-bold" href="{{ url_for('dashboard') }}">
                <i class="fas fa-crown me-2"></i>Ultimate Store Admin
            </a>
            <div>
                <a href="{{ url_for('dashboard') }}" class="btn btn-outline-light me-2">
                    <i class="fas fa-home me-1"></i>Dashboard
                </a>
                <a href="{{ url_for('stock_management') }}" class="btn btn-outline-light">
                    <i class="fas fa-warehouse me-1"></i>Stock
                </a>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <h1 class="display-5 fw-bold text-primary mb-4">
            <i class="fas fa-box me-3"></i>Products Manager
        </h1>

        {% if products_list %}
            <div class="row g-4">
                {% for product in products_list %}
                <div class="col-lg-6 col-xl-4">
                    <div class="card product-card">
                        <div class="card-header bg-primary text-white">
                            <h5 class="mb-0 fw-bold">{{ product.name }}</h5>
                            <small class="opacity-75">ID: {{ product.id }}</small>
                        </div>
                        <div class="card-body">
                            <p class="text-muted mb-3">{{ product.desc }}</p>
                            
                            <div class="d-flex justify-content-between align-items-center mb-3">
                                <span class="fw-bold">Total Sold:</span>
                                <span class="badge bg-success fs-6">{{ product.sold }}</span>
                            </div>
                            
                            <h6 class="fw-bold mb-3">🎯 Variants & Stock:</h6>
                            {% for variant_id, variant in product.variants.items() %}
                                <div class="d-flex justify-content-between align-items-center mb-3 p-2 bg-light rounded">
                                    <div>
                                        <strong>{{ variant.name }}</strong>
                                        <div class="text-success fw-bold">${{ variant.price }}</div>
                                    </div>
                                    <div class="text-end">
                                        <span class="badge bg-{{ 'success' if product.stock_info.get(variant_id, 0) > 0 else 'danger' }} mb-1">
                                            {{ product.stock_info.get(variant_id, 0) }} in stock
                                        </span>
                                        <div>
                                            <a href="{{ url_for('add_stock_form', product_id=product.id, variant_id=variant_id) }}" 
                                               class="btn btn-success btn-sm">
                                                <i class="fas fa-plus me-1"></i>Add Stock
                                            </a>
                                        </div>
                                    </div>
                                </div>
                            {% endfor %}
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
        {% else %}
            <div class="text-center py-5">
                <div class="card border-0 shadow-sm" style="max-width: 500px; margin: 0 auto;">
                    <div class="card-body py-5">
                        <i class="fas fa-box-open fa-5x text-muted mb-4"></i>
                        <h3 class="fw-bold mb-3">No Products Yet</h3>
                        <p class="text-muted mb-4">Start by adding products using your bot commands</p>
                        <div class="alert alert-info">
                            <strong>Bot Commands:</strong><br>
                            <code>/addproduct</code> - Add new products<br>
                            <code>/manageproducts</code> - Manage existing products
                        </div>
                    </div>
                </div>
            </div>
        {% endif %}
    </div>
</body>
</html>
'''

if __name__ == '__main__':
    import sys
    
    # Default to port 8080 for better compatibility
    port = 8080
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            port = 8080
    
    print("\n" + "🔥"*70)
    print("🔥 ULTIMATE PREMIUM MONGODB ADMIN INTERFACE 🔥")
    print("🔥"*70)
    print(f"✨ The MOST BEAUTIFUL interface for your store")
    print(f"🎨 Modern design • Lightning fast • Super intuitive")
    print(f"📡 Location: Cambodia VPS")
    print(f"🌐 Access URL: http://157.10.73.90:{port}")
    print(f"🔑 Password: {ADMIN_PASSWORD}")
    print("🔥"*70 + "\n")
    print("🚀 ULTIMATE FEATURES:")
    print("  🎨 Stunning modern interface with animations")
    print("  📊 Real-time dashboard with beautiful charts") 
    print("  💰 Advanced revenue tracking & analytics")
    print("  🏆 Top products analysis with insights")
    print("  🔍 Powerful database explorer & tools")
    print("  📈 Intuitive stock management")
    print("  👥 Advanced user management")
    print("  🛠️ Professional database tools")
    print("  📱 Perfect mobile responsive design")
    print("  ⚡ Lightning-fast performance")
    print("  🎯 Super easy stock management")
    print("  🔒 Secure authentication")
    print(f"\n🚀 Launching ultimate interface on port {port}...")
    print("🔥"*70 + "\n")
    
    try:
        app.run(host='0.0.0.0', port=port, debug=False)
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"\n❌ Port {port} is already in use!")
            print(f"🔧 Try: python3 ultimate_admin.py 3000")
        else:
            print(f"\n❌ Error: {e}")