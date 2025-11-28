#!/usr/bin/env python3
"""
Web Admin Panel for Telegram Store Bot
Access via: http://your-vps-ip:8080
Features: Add products, manage stock, view transactions, user management
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import os
import json
from datetime import datetime
from pymongo import MongoClient
from bson.objectid import ObjectId
from dotenv import load_dotenv
import bcrypt

# Load environment
load_dotenv()

# Configuration
MONGODB_URI = os.getenv("MONGODB_URI", "")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")  # Change this!
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")

# Flask app
app = Flask(__name__)
app.secret_key = SECRET_KEY

# MongoDB connection
try:
    client = MongoClient(MONGODB_URI)
    db = client['telegram_store_bot']
    products_coll = db['products']
    users_coll = db['users']
    stock_coll = db['stock']
    orders_coll = db['orders']
    config_coll = db['config']
    print("✅ Connected to MongoDB Atlas")
except Exception as e:
    print(f"❌ Failed to connect to MongoDB: {e}")
    exit(1)

# Helper functions
def format_currency(amount):
    return f"${amount:.2f}"

def get_stats():
    stats = {
        'total_products': products_coll.count_documents({}),
        'total_users': users_coll.count_documents({}),
        'total_stock': stock_coll.count_documents({'sold': False}),
        'sold_items': stock_coll.count_documents({'sold': True}),
        'total_orders': orders_coll.count_documents({}),
        'total_revenue': 0
    }
    
    # Calculate revenue
    orders = orders_coll.find({}, {'total': 1})
    stats['total_revenue'] = sum(order.get('total', 0) for order in orders)
    
    return stats

def check_admin_password(password):
    # Simple password check - you can make this more secure
    return password == ADMIN_PASSWORD

# Routes
@app.route('/')
def index():
    if not request.args.get('auth'):
        return render_template('login.html')
    
    if not check_admin_password(request.args.get('auth', '')):
        flash('Invalid password!', 'error')
        return render_template('login.html')
    
    stats = get_stats()
    recent_orders = list(orders_coll.find({}).sort('timestamp', -1).limit(5))
    
    return render_template('dashboard.html', stats=stats, recent_orders=recent_orders, auth=request.args.get('auth'))

@app.route('/products')
def products():
    auth = request.args.get('auth')
    if not check_admin_password(auth):
        return redirect(url_for('index'))
    
    products = list(products_coll.find({}))
    
    # Add stock counts for each variant
    for product in products:
        for vid, variant in product.get('variants', {}).items():
            stock_count = stock_coll.count_documents({
                'product_id': product['_id'],
                'variant_id': vid,
                'sold': False
            })
            variant['stock_count'] = stock_count
    
    return render_template('products.html', products=products, auth=auth)

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    auth = request.args.get('auth') or request.form.get('auth')
    if not check_admin_password(auth):
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        # Get next product ID
        last_product = products_coll.find().sort('_id', -1).limit(1)
        next_id = 1
        for p in last_product:
            next_id = p['_id'] + 1
        
        product_data = {
            '_id': next_id,
            'name': request.form['name'],
            'desc': request.form['description'],
            'sold': 0,
            'variants': {
                request.form['variant_id']: {
                    'name': request.form['variant_name'],
                    'price': float(request.form['price'])
                }
            }
        }
        
        products_coll.insert_one(product_data)
        flash(f'Product "{request.form["name"]}" added successfully!', 'success')
        return redirect(url_for('products', auth=auth))
    
    return render_template('add_product.html', auth=auth)

@app.route('/stock')
def stock():
    auth = request.args.get('auth')
    if not check_admin_password(auth):
        return redirect(url_for('index'))
    
    # Get all products with stock info
    products = list(products_coll.find({}))
    stock_data = []
    
    for product in products:
        for vid, variant in product.get('variants', {}).items():
            available_stock = list(stock_coll.find({
                'product_id': product['_id'],
                'variant_id': vid,
                'sold': False
            }))
            
            stock_data.append({
                'product_id': product['_id'],
                'product_name': product['name'],
                'variant_id': vid,
                'variant_name': variant['name'],
                'price': variant['price'],
                'stock_count': len(available_stock),
                'stock_items': available_stock
            })
    
    return render_template('stock.html', stock_data=stock_data, auth=auth)

@app.route('/add_stock', methods=['POST'])
def add_stock():
    auth = request.form.get('auth')
    if not check_admin_password(auth):
        return redirect(url_for('index'))
    
    product_id = int(request.form['product_id'])
    variant_id = request.form['variant_id']
    stock_content = request.form['stock_content'].strip()
    
    # Add each line as a separate stock item
    lines = stock_content.split('\n')
    count = 0
    for line in lines:
        line = line.strip()
        if line:
            stock_item = {
                'product_id': product_id,
                'variant_id': variant_id,
                'content': line,
                'sold': False,
                'added_at': datetime.now()
            }
            stock_coll.insert_one(stock_item)
            count += 1
    
    flash(f'Added {count} stock items successfully!', 'success')
    return redirect(url_for('stock', auth=auth))

@app.route('/users')
def users():
    auth = request.args.get('auth')
    if not check_admin_password(auth):
        return redirect(url_for('index'))
    
    users = list(users_coll.find({}).sort('spent', -1))
    return render_template('users.html', users=users, auth=auth)

@app.route('/orders')
def orders():
    auth = request.args.get('auth')
    if not check_admin_password(auth):
        return redirect(url_for('index'))
    
    # Get recent orders with product info
    orders = list(orders_coll.find({}).sort('timestamp', -1).limit(100))
    
    # Add product names
    for order in orders:
        product = products_coll.find_one({'_id': order['product_id']})
        if product:
            order['product_name'] = product['name']
            order['variant_name'] = product.get('variants', {}).get(order['variant_id'], {}).get('name', 'Unknown')
        else:
            order['product_name'] = 'Deleted Product'
            order['variant_name'] = 'Unknown'
    
    return render_template('orders.html', orders=orders, auth=auth)

@app.route('/api/stats')
def api_stats():
    return jsonify(get_stats())

@app.route('/delete_stock/<stock_id>')
def delete_stock(stock_id):
    auth = request.args.get('auth')
    if not check_admin_password(auth):
        return redirect(url_for('index'))
    
    stock_coll.delete_one({'_id': ObjectId(stock_id)})
    flash('Stock item deleted!', 'success')
    return redirect(url_for('stock', auth=auth))

# Templates (embedded in Python for easy deployment)
templates = {
    'login.html': '''
<!DOCTYPE html>
<html>
<head>
    <title>Store Bot Admin</title>
    <style>
        body { font-family: Arial; background: #f5f5f5; margin: 0; padding: 50px; }
        .login-box { max-width: 400px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .login-box h2 { text-align: center; color: #333; margin-bottom: 30px; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }
        .btn { background: #007bff; color: white; padding: 12px 20px; border: none; border-radius: 5px; cursor: pointer; width: 100%; }
        .btn:hover { background: #0056b3; }
        .alert { padding: 10px; margin-bottom: 20px; border-radius: 5px; }
        .alert-error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
    </style>
</head>
<body>
    <div class="login-box">
        <h2>🏪 Store Bot Admin Panel</h2>
        {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
        {% for category, message in messages %}
        <div class="alert alert-{{ category }}">{{ message }}</div>
        {% endfor %}
        {% endif %}
        {% endwith %}
        <form method="GET">
            <div class="form-group">
                <label>Admin Password:</label>
                <input type="password" name="auth" required>
            </div>
            <button type="submit" class="btn">Login</button>
        </form>
    </div>
</body>
</html>
    ''',
    
    'dashboard.html': '''
<!DOCTYPE html>
<html>
<head>
    <title>Dashboard - Store Bot Admin</title>
    <style>
        body { font-family: Arial; margin: 0; background: #f8f9fa; }
        .header { background: #007bff; color: white; padding: 1rem; }
        .nav { display: flex; gap: 20px; margin-top: 10px; }
        .nav a { color: white; text-decoration: none; padding: 8px 12px; border-radius: 4px; }
        .nav a:hover { background: rgba(255,255,255,0.2); }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .stat-card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); text-align: center; }
        .stat-number { font-size: 2em; font-weight: bold; color: #007bff; }
        .stat-label { color: #666; margin-top: 5px; }
        .recent-orders { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 10px; text-align: left; border-bottom: 1px solid #eee; }
        th { background: #f8f9fa; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🏪 Store Bot Admin Panel</h1>
        <nav class="nav">
            <a href="/?auth={{ auth }}">Dashboard</a>
            <a href="/products?auth={{ auth }}">Products</a>
            <a href="/stock?auth={{ auth }}">Stock</a>
            <a href="/users?auth={{ auth }}">Users</a>
            <a href="/orders?auth={{ auth }}">Orders</a>
        </nav>
    </div>
    
    <div class="container">
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{{ stats.total_products }}</div>
                <div class="stat-label">Products</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ stats.total_users }}</div>
                <div class="stat-label">Users</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ stats.total_stock }}</div>
                <div class="stat-label">Available Stock</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">${{ "%.2f"|format(stats.total_revenue) }}</div>
                <div class="stat-label">Total Revenue</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ stats.sold_items }}</div>
                <div class="stat-label">Sold Items</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ stats.total_orders }}</div>
                <div class="stat-label">Orders</div>
            </div>
        </div>
        
        <div class="recent-orders">
            <h3>Recent Orders</h3>
            <table>
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>User ID</th>
                        <th>Product</th>
                        <th>Amount</th>
                        <th>Transaction ID</th>
                    </tr>
                </thead>
                <tbody>
                    {% for order in recent_orders %}
                    <tr>
                        <td>{{ order.timestamp.strftime('%Y-%m-%d %H:%M') if order.timestamp else 'N/A' }}</td>
                        <td>{{ order.user_id }}</td>
                        <td>Product {{ order.product_id }}</td>
                        <td>${{ "%.2f"|format(order.total) }}</td>
                        <td>{{ order.trx_id }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
    '''
}

# Set template folder
app.template_folder = 'templates'

if __name__ == '__main__':
    print(f"🚀 Starting Store Bot Admin Panel...")
    print(f"🌐 Access: http://your-vps-ip:8080")
    print(f"🔑 Password: {ADMIN_PASSWORD}")
    print(f"⚠️  Change ADMIN_PASSWORD in .env for security!")
    app.run(host='0.0.0.0', port=8080, debug=False)