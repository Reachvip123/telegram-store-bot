#!/usr/bin/env python3
"""
API Server for Telegram Store Bot
Provides REST API endpoints for the admin panel to manage the bot
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import glob
import hashlib

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests from Railway

# Database paths
DB_DIR = 'database'
PRODUCTS_FILE = os.path.join(DB_DIR, 'products.json')
USERS_FILE = os.path.join(DB_DIR, 'users.json')
CONFIG_FILE = os.path.join(DB_DIR, 'config.json')

# Simple API key authentication
API_KEY = "your-secret-api-key-change-this"  # Change this!

def verify_api_key():
    """Check if request has valid API key"""
    key = request.headers.get('X-API-Key')
    if key != API_KEY:
        return False
    return True

def load_json_file(filepath):
    """Load JSON file"""
    if not os.path.exists(filepath):
        return {}
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json_file(filepath, data):
    """Save JSON file"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# ==================== PRODUCTS API ====================

@app.route('/api/products', methods=['GET'])
def get_products():
    """Get all products"""
    if not verify_api_key():
        return jsonify({'error': 'Unauthorized'}), 401
    
    products = load_json_file(PRODUCTS_FILE)
    return jsonify(products)

@app.route('/api/products', methods=['POST'])
def add_product():
    """Add new product"""
    if not verify_api_key():
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    products = load_json_file(PRODUCTS_FILE)
    
    # Generate new product ID
    product_id = str(len(products) + 1)
    products[product_id] = {
        'name': data.get('name'),
        'price': data.get('price'),
        'variants': data.get('variants', {}),
        'description': data.get('description', ''),
        'emoji': data.get('emoji', '📦')
    }
    
    save_json_file(PRODUCTS_FILE, products)
    return jsonify({'success': True, 'product_id': product_id})

@app.route('/api/products/<product_id>', methods=['PUT'])
def update_product(product_id):
    """Update product"""
    if not verify_api_key():
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    products = load_json_file(PRODUCTS_FILE)
    
    if product_id not in products:
        return jsonify({'error': 'Product not found'}), 404
    
    products[product_id].update(data)
    save_json_file(PRODUCTS_FILE, products)
    return jsonify({'success': True})

@app.route('/api/products/<product_id>', methods=['DELETE'])
def delete_product(product_id):
    """Delete product"""
    if not verify_api_key():
        return jsonify({'error': 'Unauthorized'}), 401
    
    products = load_json_file(PRODUCTS_FILE)
    
    if product_id in products:
        del products[product_id]
        save_json_file(PRODUCTS_FILE, products)
        return jsonify({'success': True})
    
    return jsonify({'error': 'Product not found'}), 404

# ==================== STOCK API ====================

@app.route('/api/stock', methods=['GET'])
def get_all_stock():
    """Get stock summary for all products"""
    if not verify_api_key():
        return jsonify({'error': 'Unauthorized'}), 401
    
    products = load_json_file(PRODUCTS_FILE)
    stock_data = []
    
    for pid, product in products.items():
        for vid, variant in product.get('variants', {}).items():
            stock_file = os.path.join(DB_DIR, f'stock_{pid}_{vid}.txt')
            count = 0
            if os.path.exists(stock_file):
                with open(stock_file, 'r', encoding='utf-8') as f:
                    count = len([line for line in f if line.strip()])
            
            stock_data.append({
                'product_id': pid,
                'product_name': product['name'],
                'variant_id': vid,
                'variant_name': variant,
                'stock_count': count
            })
    
    return jsonify(stock_data)

@app.route('/api/stock/<product_id>/<variant_id>', methods=['GET'])
def get_stock(product_id, variant_id):
    """Get stock for specific product variant"""
    if not verify_api_key():
        return jsonify({'error': 'Unauthorized'}), 401
    
    stock_file = os.path.join(DB_DIR, f'stock_{product_id}_{variant_id}.txt')
    
    if not os.path.exists(stock_file):
        return jsonify({'accounts': [], 'count': 0})
    
    with open(stock_file, 'r', encoding='utf-8') as f:
        accounts = [line.strip() for line in f if line.strip()]
    
    return jsonify({'accounts': accounts, 'count': len(accounts)})

@app.route('/api/stock/<product_id>/<variant_id>', methods=['POST'])
def add_stock(product_id, variant_id):
    """Add stock accounts"""
    if not verify_api_key():
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    accounts = data.get('accounts', [])
    
    stock_file = os.path.join(DB_DIR, f'stock_{product_id}_{variant_id}.txt')
    os.makedirs(DB_DIR, exist_ok=True)
    
    with open(stock_file, 'a', encoding='utf-8') as f:
        for account in accounts:
            f.write(account.strip() + '\n')
    
    return jsonify({'success': True, 'added': len(accounts)})

@app.route('/api/stock/<product_id>/<variant_id>', methods=['DELETE'])
def clear_stock(product_id, variant_id):
    """Clear all stock for variant"""
    if not verify_api_key():
        return jsonify({'error': 'Unauthorized'}), 401
    
    stock_file = os.path.join(DB_DIR, f'stock_{product_id}_{variant_id}.txt')
    
    if os.path.exists(stock_file):
        os.remove(stock_file)
    
    return jsonify({'success': True})

# ==================== USERS API ====================

@app.route('/api/users', methods=['GET'])
def get_users():
    """Get all users"""
    if not verify_api_key():
        return jsonify({'error': 'Unauthorized'}), 401
    
    users = load_json_file(USERS_FILE)
    return jsonify(users)

@app.route('/api/users/<user_id>', methods=['GET'])
def get_user(user_id):
    """Get specific user"""
    if not verify_api_key():
        return jsonify({'error': 'Unauthorized'}), 401
    
    users = load_json_file(USERS_FILE)
    
    if user_id in users:
        return jsonify(users[user_id])
    
    return jsonify({'error': 'User not found'}), 404

# ==================== SETTINGS/CONFIG API ====================

@app.route('/api/config', methods=['GET'])
def get_config():
    """Get configuration"""
    if not verify_api_key():
        return jsonify({'error': 'Unauthorized'}), 401
    
    config = load_json_file(CONFIG_FILE)
    return jsonify(config)

@app.route('/api/config', methods=['PUT'])
def update_config():
    """Update configuration"""
    if not verify_api_key():
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    config = load_json_file(CONFIG_FILE)
    config.update(data)
    save_json_file(CONFIG_FILE, config)
    
    return jsonify({'success': True})

# ==================== STATS API ====================

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get dashboard statistics"""
    if not verify_api_key():
        return jsonify({'error': 'Unauthorized'}), 401
    
    products = load_json_file(PRODUCTS_FILE)
    users = load_json_file(USERS_FILE)
    
    # Count total stock
    stock_count = 0
    products_in_stock = 0
    for pid, product in products.items():
        for vid in product.get('variants', {}).keys():
            stock_file = os.path.join(DB_DIR, f'stock_{pid}_{vid}.txt')
            if os.path.exists(stock_file):
                with open(stock_file, 'r', encoding='utf-8') as f:
                    count = len([line for line in f if line.strip()])
                    stock_count += count
                    if count > 0:
                        products_in_stock += 1
    
    # Calculate total revenue
    total_revenue = sum(user.get('total_spent', 0) for user in users.values())
    
    # Count total sold
    total_sold = sum(user.get('purchases', 0) for user in users.values())
    
    return jsonify({
        'total_products': len(products),
        'total_revenue': total_revenue,
        'total_users': len(users),
        'stock_count': stock_count,
        'products_in_stock': products_in_stock,
        'total_sold': total_sold
    })

# ==================== ADMIN AUTH API ====================

@app.route('/api/auth/verify', methods=['POST'])
def verify_admin():
    """Verify admin credentials"""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    # Load admin credentials from config
    config = load_json_file(CONFIG_FILE)
    admin = config.get('admin', {'username': 'admin', 'password': hashlib.sha256('admin123'.encode()).hexdigest()})
    
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    if username == admin['username'] and hashed_password == admin['password']:
        return jsonify({'success': True, 'api_key': API_KEY})
    
    return jsonify({'success': False, 'error': 'Invalid credentials'}), 401

@app.route('/api/auth/change-password', methods=['POST'])
def change_password():
    """Change admin password"""
    if not verify_api_key():
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    new_password = data.get('new_password')
    
    config = load_json_file(CONFIG_FILE)
    if 'admin' not in config:
        config['admin'] = {}
    
    config['admin']['password'] = hashlib.sha256(new_password.encode()).hexdigest()
    save_json_file(CONFIG_FILE, config)
    
    return jsonify({'success': True})

# ==================== HEALTH CHECK ====================

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'service': 'bot-api'})

@app.route('/', methods=['GET'])
def index():
    """API info"""
    return jsonify({
        'service': 'Telegram Store Bot API',
        'version': '1.0',
        'endpoints': [
            'GET /api/products',
            'POST /api/products',
            'PUT /api/products/<id>',
            'DELETE /api/products/<id>',
            'GET /api/stock',
            'GET /api/stock/<pid>/<vid>',
            'POST /api/stock/<pid>/<vid>',
            'DELETE /api/stock/<pid>/<vid>',
            'GET /api/users',
            'GET /api/config',
            'PUT /api/config',
            'GET /api/stats',
            'POST /api/auth/verify',
            'POST /api/auth/change-password'
        ]
    })

if __name__ == '__main__':
    port = int(os.environ.get('API_PORT', 5000))
    print("="*50)
    print(f" Bot API Server Starting on port {port}...")
    print(f" API Key: {API_KEY}")
    print(" CHANGE THE API_KEY IN PRODUCTION!")
    print("="*50)
    app.run(host='0.0.0.0', port=port, debug=False)
