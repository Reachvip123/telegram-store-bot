#!/usr/bin/env python3
"""
Web Admin Panel for Cambodia VPS
MongoDB Database Management Interface
Access at: http://157.10.73.90:5000 (or http://localhost:5000 locally)
"""

from flask import Flask, render_template_string, request, redirect, url_for, flash, session
import pymongo
from bson import ObjectId
import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = 'cambodia-vps-admin-panel-2024'

# MongoDB Atlas Connection - Cambodia VPS
MONGODB_URI = "mongodb+srv://dztsorebase:reachvip@cluster0.tbyhuzf.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DATABASE_NAME = "telegram_store_bot"  # Using same database as bot

# Admin password
ADMIN_PASSWORD = "admin123"  # Change this!

def get_db():
    """Get MongoDB database connection"""
    try:
        client = pymongo.MongoClient(MONGODB_URI)
        return client[DATABASE_NAME]
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

# Simple authentication
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
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid password!', 'error')
    
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>Store Bot Admin - Cambodia VPS</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; align-items: center; justify-content: center; }
        .login-card { background: white; border-radius: 20px; box-shadow: 0 20px 40px rgba(0,0,0,0.1); max-width: 400px; width: 100%; }
    </style>
</head>
<body>
    <div class="login-card p-4">
        <div class="text-center mb-4">
            <h2><i class="fas fa-robot"></i></h2>
            <h4>Store Bot Admin</h4>
            <p class="text-muted">Cambodia VPS - MongoDB Control Panel</p>
        </div>
        
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ 'danger' if category == 'error' else 'success' }}"}>{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        <form method="POST">
            <div class="mb-3">
                <input type="password" name="password" class="form-control" placeholder="Admin Password" required>
            </div>
            <button type="submit" class="btn btn-primary w-100">Login</button>
        </form>
        
        <div class="text-center mt-3">
            <small class="text-muted">Cambodia VPS • MongoDB Atlas</small>
        </div>
    </div>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
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
        
        # Get statistics
        products_count = db.products.count_documents({})
        users_count = db.users.count_documents({})
        
        # Get total sold
        total_sold_pipeline = [{'$group': {'_id': None, 'total_sold': {'$sum': '$sold'}}}]
        sold_result = list(db.products.aggregate(total_sold_pipeline))
        total_sold = sold_result[0]['total_sold'] if sold_result else 0
        
        # Get stock count
        stock_count = db.stock.count_documents({'sold': False})
        
        stats = {
            'products': products_count,
            'users': users_count,
            'sold': total_sold,
            'stock': stock_count
        }
        
        return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>Dashboard - Store Bot Admin</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .stat-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
        .card { border: none; border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.08); }
    </style>
</head>
<body class="bg-light">
    <nav class="navbar navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="#">
                <i class="fas fa-robot"></i> Store Bot Admin - Cambodia VPS • MongoDB
            </a>
            <div>
                <a href="{{ url_for('products') }}" class="btn btn-light me-2">Products</a>
                <a href="{{ url_for('stock_management') }}" class="btn btn-light me-2">Stock</a>
                <a href="{{ url_for('logout') }}" class="btn btn-outline-light">Logout</a>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
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

        <h1 class="mb-4">📊 Dashboard</h1>
        
        <div class="row mb-4">
            <div class="col-md-3">
                <div class="card stat-card">
                    <div class="card-body text-center">
                        <i class="fas fa-box fa-3x mb-3"></i>
                        <h3>{{ stats.products }}</h3>
                        <p>Products</p>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card bg-success text-white">
                    <div class="card-body text-center">
                        <i class="fas fa-users fa-3x mb-3"></i>
                        <h3>{{ stats.users }}</h3>
                        <p>Users</p>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card bg-warning text-white">
                    <div class="card-body text-center">
                        <i class="fas fa-shopping-cart fa-3x mb-3"></i>
                        <h3>{{ stats.sold }}</h3>
                        <p>Sold</p>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card bg-info text-white">
                    <div class="card-body text-center">
                        <i class="fas fa-warehouse fa-3x mb-3"></i>
                        <h3>{{ stats.stock }}</h3>
                        <p>Stock Items</p>
                    </div>
                </div>
            </div>
        </div>

        <div class="row">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5>🚀 Quick Actions</h5>
                    </div>
                    <div class="card-body">
                        <div class="d-grid gap-2">
                            <a href="{{ url_for('products') }}" class="btn btn-primary">
                                <i class="fas fa-box"></i> Manage Products
                            </a>
                            <a href="{{ url_for('stock_management') }}" class="btn btn-success">
                                <i class="fas fa-warehouse"></i> Manage Stock
                            </a>
                            <a href="{{ url_for('users') }}" class="btn btn-info">
                                <i class="fas fa-users"></i> View Users
                            </a>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card border-success">
                    <div class="card-header bg-success text-white">
                        <h6><i class="fas fa-server"></i> System Info</h6>
                    </div>
                    <div class="card-body">
                        <p><strong>Server:</strong> Cambodia VPS</p>
                        <p><strong>IP:</strong> 157.10.73.90</p>
                        <p><strong>Database:</strong> MongoDB Atlas (telegram_store_bot)</p>
                        <p><strong>Status:</strong> <span class="badge bg-success">Online</span></p>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
        ''', stats=stats)
    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}', 'error')
        return redirect(url_for('login'))

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
                stock_count = db.stock.count_documents({
                    'product_id': product_data['id'],
                    'variant_id': variant_id,
                    'sold': False
                })
                product_data['stock_info'][variant_id] = stock_count
            
            products_list.append(product_data)
        
        return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>Products - Store Bot Admin</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
</head>
<body class="bg-light">
    <nav class="navbar navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="{{ url_for('dashboard') }}">
                <i class="fas fa-robot"></i> Store Bot Admin
            </a>
            <div>
                <a href="{{ url_for('dashboard') }}" class="btn btn-light me-2">Dashboard</a>
                <a href="{{ url_for('stock_management') }}" class="btn btn-light me-2">Stock</a>
                <a href="{{ url_for('logout') }}" class="btn btn-outline-light">Logout</a>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h1>📦 Products</h1>
        </div>

        {% if products_list %}
            <div class="row">
                {% for product in products_list %}
                <div class="col-md-6 mb-4">
                    <div class="card">
                        <div class="card-header">
                            <h5>{{ product.name }}</h5>
                            <small class="text-muted">ID: {{ product.id }}</small>
                        </div>
                        <div class="card-body">
                            <p>{{ product.desc }}</p>
                            <p><strong>Sold:</strong> <span class="badge bg-success">{{ product.sold }}</span></p>
                            
                            <h6>Variants & Stock:</h6>
                            {% for variant_id, variant in product.variants.items() %}
                                <div class="d-flex justify-content-between align-items-center mb-2">
                                    <span>{{ variant.name }} - ${{ variant.price }}</span>
                                    <div>
                                        <span class="badge bg-info">{{ product.stock_info.get(variant_id, 0) }} in stock</span>
                                        <a href="{{ url_for('add_stock_form', product_id=product.id, variant_id=variant_id) }}" 
                                           class="btn btn-sm btn-success ms-2">
                                            <i class="fas fa-plus"></i> Add Stock
                                        </a>
                                    </div>
                                </div>
                            {% endfor %}
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
        {% else %}
            <div class="card">
                <div class="card-body text-center">
                    <i class="fas fa-box fa-3x text-muted mb-3"></i>
                    <h5>No products yet</h5>
                    <p class="text-muted">Products will appear here when you add them via bot commands.</p>
                    <p class="text-muted">Use bot commands: /addproduct, /manageproducts</p>
                </div>
            </div>
        {% endif %}
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
        ''', products_list=products_list)
    except Exception as e:
        flash(f'Error loading products: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

@app.route('/stock')
@login_required
def stock_management():
    try:
        db = get_db()
        products_cursor = db.products.find({})
        products_list = []
        
        for product in products_cursor:
            product_data = {
                'id': str(product['_id']),
                'name': product.get('name', ''),
                'variants': product.get('variants', {})
            }
            
            # Get stock info for each variant
            product_data['variants_stock'] = {}
            for variant_id, variant in product_data['variants'].items():
                available = db.stock.count_documents({
                    'product_id': product_data['id'],
                    'variant_id': variant_id,
                    'sold': False
                })
                sold = db.stock.count_documents({
                    'product_id': product_data['id'],
                    'variant_id': variant_id,
                    'sold': True
                })
                
                product_data['variants_stock'][variant_id] = {
                    'name': variant['name'],
                    'price': variant['price'],
                    'available': available,
                    'sold': sold
                }
            
            products_list.append(product_data)
        
        return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>Stock Management - Store Bot Admin</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
</head>
<body class="bg-light">
    <nav class="navbar navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="{{ url_for('dashboard') }}">
                <i class="fas fa-robot"></i> Store Bot Admin
            </a>
            <div>
                <a href="{{ url_for('dashboard') }}" class="btn btn-light me-2">Dashboard</a>
                <a href="{{ url_for('products') }}" class="btn btn-light me-2">Products</a>
                <a href="{{ url_for('logout') }}" class="btn btn-outline-light">Logout</a>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <h1 class="mb-4">📊 Stock Management</h1>

        {% if products_list %}
            {% for product in products_list %}
            <div class="card mb-4">
                <div class="card-header">
                    <h5>{{ product.name }}</h5>
                </div>
                <div class="card-body">
                    <div class="table-responsive">
                        <table class="table">
                            <thead>
                                <tr>
                                    <th>Variant</th>
                                    <th>Price</th>
                                    <th>Available</th>
                                    <th>Sold</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for variant_id, stock_info in product.variants_stock.items() %}
                                <tr>
                                    <td><strong>{{ stock_info.name }}</strong></td>
                                    <td>${{ stock_info.price }}</td>
                                    <td>
                                        <span class="badge bg-{{ 'success' if stock_info.available > 0 else 'danger' }}">
                                            {{ stock_info.available }}
                                        </span>
                                    </td>
                                    <td><span class="badge bg-info">{{ stock_info.sold }}</span></td>
                                    <td>
                                        <a href="{{ url_for('add_stock_form', product_id=product.id, variant_id=variant_id) }}" 
                                           class="btn btn-sm btn-success me-2">
                                            <i class="fas fa-plus"></i> Add Stock
                                        </a>
                                        {% if stock_info.available > 0 %}
                                        <form method="POST" action="{{ url_for('clear_stock', product_id=product.id, variant_id=variant_id) }}" 
                                              style="display: inline;" onsubmit="return confirm('Clear all stock for this variant?')">
                                            <button type="submit" class="btn btn-sm btn-danger">
                                                <i class="fas fa-trash"></i> Clear
                                            </button>
                                        </form>
                                        {% endif %}
                                    </td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
            {% endfor %}
        {% else %}
            <div class="card">
                <div class="card-body text-center">
                    <i class="fas fa-warehouse fa-3x text-muted mb-3"></i>
                    <h5>No products to manage</h5>
                    <p class="text-muted">Add products first using bot commands.</p>
                </div>
            </div>
        {% endif %}
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
        ''', products_list=products_list)
    except Exception as e:
        flash(f'Error loading stock: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

@app.route('/add_stock/<product_id>/<variant_id>')
@login_required
def add_stock_form(product_id, variant_id):
    try:
        db = get_db()
        product = db.products.find_one({'_id': ObjectId(product_id)})
        if not product:
            flash('Product not found!', 'error')
            return redirect(url_for('products'))
        
        variant_info = product.get('variants', {}).get(variant_id, {})
        
        return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>Add Stock - Store Bot Admin</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
</head>
<body class="bg-light">
    <nav class="navbar navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="{{ url_for('dashboard') }}">
                <i class="fas fa-robot"></i> Store Bot Admin
            </a>
            <div>
                <a href="{{ url_for('products') }}" class="btn btn-light me-2">Products</a>
                <a href="{{ url_for('stock_management') }}" class="btn btn-light me-2">Stock</a>
                <a href="{{ url_for('logout') }}" class="btn btn-outline-light">Logout</a>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="row justify-content-center">
            <div class="col-md-8">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-plus"></i> Add Stock</h5>
                    </div>
                    <div class="card-body">
                        <div class="mb-3">
                            <strong>Product:</strong> {{ product.name }}<br>
                            <strong>Variant:</strong> {{ variant_info.name }} - ${{ variant_info.price }}
                        </div>
                        
                        <form method="POST" action="{{ url_for('add_stock', product_id=product_id, variant_id=variant_id) }}">
                            <div class="mb-3">
                                <label class="form-label">Stock Items (one per line)</label>
                                <textarea name="stock_data" class="form-control" rows="10" required
                                          placeholder="account1:password1
account2:password2
account3:password3
token:abc123
token:def456"></textarea>
                                <div class="form-text">Enter one account/token per line. Each line will be one stock item.</div>
                            </div>
                            
                            <div class="d-flex justify-content-between">
                                <a href="{{ url_for('products') }}" class="btn btn-secondary">
                                    <i class="fas fa-arrow-left"></i> Back to Products
                                </a>
                                <button type="submit" class="btn btn-success">
                                    <i class="fas fa-save"></i> Add Stock Items
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
        ''', product=product, variant_info=variant_info, product_id=product_id, variant_id=variant_id)
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('products'))

@app.route('/add_stock/<product_id>/<variant_id>', methods=['POST'])
@login_required
def add_stock(product_id, variant_id):
    try:
        db = get_db()
        stock_data = request.form.get('stock_data', '').strip()
        
        if not stock_data:
            flash('Stock data is required!', 'error')
            return redirect(url_for('add_stock_form', product_id=product_id, variant_id=variant_id))
        
        # Split by lines and clean
        lines = [line.strip() for line in stock_data.split('\n') if line.strip()]
        
        if not lines:
            flash('No valid stock items found!', 'error')
            return redirect(url_for('add_stock_form', product_id=product_id, variant_id=variant_id))
        
        # Add each line as a stock item
        for line in lines:
            db.stock.insert_one({
                'product_id': product_id,
                'variant_id': variant_id,
                'content': line,
                'sold': False,
                'added_at': datetime.now()
            })
        
        flash(f'Added {len(lines)} stock items successfully!', 'success')
        return redirect(url_for('products'))
    except Exception as e:
        flash(f'Error adding stock: {str(e)}', 'error')
        return redirect(url_for('add_stock_form', product_id=product_id, variant_id=variant_id))

@app.route('/clear_stock/<product_id>/<variant_id>', methods=['POST'])
@login_required
def clear_stock(product_id, variant_id):
    try:
        db = get_db()
        result = db.stock.delete_many({
            'product_id': product_id,
            'variant_id': variant_id,
            'sold': False
        })
        
        flash(f'Cleared {result.deleted_count} stock items!', 'success')
        return redirect(url_for('stock_management'))
    except Exception as e:
        flash(f'Error clearing stock: {str(e)}', 'error')
        return redirect(url_for('stock_management'))

@app.route('/users')
@login_required
def users():
    try:
        db = get_db()
        users_cursor = db.users.find({}).sort('spent', -1).limit(50)
        users_list = list(users_cursor)
        
        return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>Users - Store Bot Admin</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
</head>
<body class="bg-light">
    <nav class="navbar navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="{{ url_for('dashboard') }}">
                <i class="fas fa-robot"></i> Store Bot Admin
            </a>
            <div>
                <a href="{{ url_for('dashboard') }}" class="btn btn-light me-2">Dashboard</a>
                <a href="{{ url_for('products') }}" class="btn btn-light me-2">Products</a>
                <a href="{{ url_for('logout') }}" class="btn btn-outline-light">Logout</a>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <h1 class="mb-4">👥 Users (Top 50)</h1>

        {% if users_list %}
            <div class="table-responsive">
                <table class="table table-striped">
                    <thead class="table-primary">
                        <tr>
                            <th>User ID</th>
                            <th>Username</th>
                            <th>Total Spent</th>
                            <th>Joined</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for user in users_list %}
                        <tr>
                            <td>{{ user.user_id }}</td>
                            <td>{{ user.get('username', 'Unknown') }}</td>
                            <td><span class="badge bg-success">${{ "%.2f"|format(user.get('spent', 0)) }}</span></td>
                            <td>{{ user.get('joined_at', 'Unknown') }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        {% else %}
            <div class="card">
                <div class="card-body text-center">
                    <i class="fas fa-users fa-3x text-muted mb-3"></i>
                    <h5>No users yet</h5>
                    <p class="text-muted">Users will appear here when they interact with your bot.</p>
                </div>
            </div>
        {% endif %}
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
        ''', users_list=users_list)
    except Exception as e:
        flash(f'Error loading users: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

if __name__ == '__main__':
    import sys
    
    # Check for port argument
    port = 5000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            port = 5000
    
    print("\n" + "="*60)
    print("🌐 Store Bot Admin Panel - Cambodia VPS")
    print("="*60)
    print(f"🎯 Purpose: Manage MongoDB database for your Telegram bot")
    print(f"📡 Server: Cambodia VPS (157.10.73.90)")
    print(f"💾 Database: MongoDB Atlas - telegram_store_bot")
    print(f"🌐 Access URL: http://localhost:{port} (local)")
    print(f"🌐 VPS Access: http://157.10.73.90:{port} (remote)")
    print(f"🔑 Admin Password: {ADMIN_PASSWORD}")
    print("="*60 + "\n")
    print("🚀 Features:")
    print("  📊 Dashboard with live statistics")
    print("  📦 Products management")
    print("  📈 Stock management (add/clear)")
    print("  👥 Users overview")
    print("  🔒 Password protection")
    print(f"\n🚀 Starting admin panel on port {port}...")
    print(f"🔧 If port {port} is busy, try:")
    print(f"   python simple_vps_admin.py 8080")
    print(f"   python simple_vps_admin.py 3000")
    print("\n" + "="*60)
    
    try:
        # Run the Flask app on Cambodia VPS
        app.run(host='0.0.0.0', port=port, debug=False)
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"\n❌ Port {port} is already in use!")
            print(f"🔧 Try a different port:")
            print(f"   python simple_vps_admin.py 8080")
            print(f"   python simple_vps_admin.py 3000")
        else:
            print(f"\n❌ Error starting server: {e}")
            print("🔧 Check if you have permission to bind to this port")