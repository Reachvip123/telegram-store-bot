import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from functools import wraps
import json
import os
from datetime import datetime
import hashlib

app = Flask(__name__)
app.secret_key = "change-this-secret-key-in-production"

# Configuration - Same as storebot.py
DB_FOLDER = "database"
PRODUCTS_FILE = f"{DB_FOLDER}/products.json"
CONFIG_FILE = f"{DB_FOLDER}/config.json"
USERS_FILE = f"{DB_FOLDER}/users.json"
ADMIN_FILE = f"{DB_FOLDER}/admin.json"

# Default admin credentials
DEFAULT_ADMIN = {
    "username": "admin",
    "password": hashlib.sha256("admin123".encode()).hexdigest()
}

if not os.path.exists(DB_FOLDER):
    os.makedirs(DB_FOLDER)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_admin():
    if not os.path.exists(ADMIN_FILE):
        with open(ADMIN_FILE, 'w') as f:
            json.dump(DEFAULT_ADMIN, f, indent=2)
        return DEFAULT_ADMIN
    with open(ADMIN_FILE, 'r') as f:
        return json.load(f)

def load_products():
    if not os.path.exists(PRODUCTS_FILE):
        return {}
    with open(PRODUCTS_FILE, 'r') as f:
        return json.load(f)

def save_products(data):
    with open(PRODUCTS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, 'r') as f:
        return json.load(f)

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {}
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def save_config(data):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def get_stock_file(pid, vid):
    safe_vid = str(vid).replace(" ", "").upper()
    return f"{DB_FOLDER}/stock_{pid}_{safe_vid}.txt"

def get_stock_count(pid, vid):
    filename = get_stock_file(pid, vid)
    if not os.path.exists(filename):
        return 0
    with open(filename, 'r') as f:
        lines = [l for l in f.readlines() if l.strip()]
    return len(lines)

def get_stock_lines(pid, vid):
    filename = get_stock_file(pid, vid)
    if not os.path.exists(filename):
        return []
    with open(filename, 'r') as f:
        return [l.strip() for l in f.readlines() if l.strip()]

def save_stock_lines(pid, vid, lines):
    filename = get_stock_file(pid, vid)
    with open(filename, 'w') as f:
        for line in lines:
            f.write(f"{line}\n")

def get_dashboard_stats():
    products = load_products()
    users = load_users()
    
    total_products = len(products)
    total_variants = sum(len(p.get('variants', {})) for p in products.values())
    total_users = len(users)
    total_sold = sum(p.get('sold', 0) for p in products.values())
    total_revenue = sum(u.get('spent', 0) for u in users.values())
    
    total_stock = 0
    for pid, product in products.items():
        for vid in product.get('variants', {}).keys():
            total_stock += get_stock_count(pid, vid)
    
    return {
        'total_products': total_products,
        'total_variants': total_variants,
        'total_users': total_users,
        'total_sold': total_sold,
        'total_revenue': round(total_revenue, 2),
        'total_stock': total_stock
    }

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/health')
def health():
    return 'OK', 200

@app.route('/')
@login_required
def index():
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        admin = verify_admin()
        hashed_password = hash_password(password)
        
        if username == admin['username'] and hashed_password == admin['password']:
            session['logged_in'] = True
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials!', 'danger')
    
    error = request.args.get('error')
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    stats = get_dashboard_stats()
    return render_template('dashboard.html', stats=stats)

@app.route('/products')
@login_required
def products():
    products = load_products()
    for pid, product in products.items():
        for vid, variant in product.get('variants', {}).items():
            variant['stock_count'] = get_stock_count(pid, vid)
    return render_template('products.html', products=products)

@app.route('/api/products', methods=['GET', 'POST', 'PUT', 'DELETE'])
@login_required
def api_products():
    products = load_products()
    
    if request.method == 'POST':
        data = request.json
        pid = data.get('id')
        if not pid or pid in products:
            return jsonify({'error': 'Invalid or duplicate product ID'}), 400
        products[pid] = {'name': data.get('name', ''), 'desc': data.get('desc', ''), 'sold': 0, 'variants': {}}
        save_products(products)
        return jsonify({'success': True})
    
    elif request.method == 'PUT':
        data = request.json
        pid = data.get('id')
        if pid not in products:
            return jsonify({'error': 'Product not found'}), 404
        products[pid]['name'] = data.get('name', products[pid]['name'])
        products[pid]['desc'] = data.get('desc', products[pid]['desc'])
        save_products(products)
        return jsonify({'success': True})
    
    elif request.method == 'DELETE':
        pid = request.json.get('id')
        if pid not in products:
            return jsonify({'error': 'Product not found'}), 404
        for vid in products[pid].get('variants', {}).keys():
            filename = get_stock_file(pid, vid)
            if os.path.exists(filename):
                os.remove(filename)
        del products[pid]
        save_products(products)
        return jsonify({'success': True})

@app.route('/api/variants', methods=['POST', 'PUT', 'DELETE'])
@login_required
def api_variants():
    products = load_products()
    
    if request.method == 'POST':
        data = request.json
        pid = data.get('product_id')
        vid = data.get('variant_id')
        if pid not in products:
            return jsonify({'error': 'Product not found'}), 404
        if vid in products[pid].get('variants', {}):
            return jsonify({'error': 'Variant already exists'}), 400
        if 'variants' not in products[pid]:
            products[pid]['variants'] = {}
        products[pid]['variants'][vid] = {
            'name': data.get('name', ''),
            'price': float(data.get('price', 0)),
            'tutorial': data.get('tutorial')
        }
        save_products(products)
        return jsonify({'success': True})
    
    elif request.method == 'PUT':
        data = request.json
        pid = data.get('product_id')
        vid = data.get('variant_id')
        if pid not in products or vid not in products[pid].get('variants', {}):
            return jsonify({'error': 'Variant not found'}), 404
        products[pid]['variants'][vid]['name'] = data.get('name')
        products[pid]['variants'][vid]['price'] = float(data.get('price'))
        products[pid]['variants'][vid]['tutorial'] = data.get('tutorial')
        save_products(products)
        return jsonify({'success': True})
    
    elif request.method == 'DELETE':
        data = request.json
        pid = data.get('product_id')
        vid = data.get('variant_id')
        if pid not in products or vid not in products[pid].get('variants', {}):
            return jsonify({'error': 'Variant not found'}), 404
        filename = get_stock_file(pid, vid)
        if os.path.exists(filename):
            os.remove(filename)
        del products[pid]['variants'][vid]
        save_products(products)
        return jsonify({'success': True})

@app.route('/stock')
@login_required
def stock():
    products = load_products()
    stock_data = []
    for pid, product in products.items():
        for vid, variant in product.get('variants', {}).items():
            count = get_stock_count(pid, vid)
            stock_data.append({
                'product_id': pid,
                'product_name': product['name'],
                'variant_id': vid,
                'variant_name': variant['name'],
                'count': count
            })
    return render_template('stock.html', stock_data=stock_data, products=products)

@app.route('/api/stock/<pid>/<vid>', methods=['GET', 'POST', 'DELETE'])
@login_required
def api_stock(pid, vid):
    products = load_products()
    if pid not in products or vid not in products[pid].get('variants', {}):
        return jsonify({'error': 'Product or variant not found'}), 404
    
    if request.method == 'GET':
        lines = get_stock_lines(pid, vid)
        return jsonify({'stock': lines, 'count': len(lines)})
    
    elif request.method == 'POST':
        data = request.json
        stock_text = data.get('stock', '')
        if not stock_text:
            return jsonify({'error': 'No stock provided'}), 400
        new_lines = [line.strip() for line in stock_text.split('\n') if line.strip()]
        existing_lines = get_stock_lines(pid, vid)
        all_lines = existing_lines + new_lines
        save_stock_lines(pid, vid, all_lines)
        return jsonify({'success': True, 'count': len(all_lines), 'added': len(new_lines)})
    
    elif request.method == 'DELETE':
        filename = get_stock_file(pid, vid)
        if os.path.exists(filename):
            os.remove(filename)
        return jsonify({'success': True})

@app.route('/users')
@login_required
def users():
    users = load_users()
    users_list = []
    for uid, user in users.items():
        users_list.append({
            'user_id': uid,
            'username': user.get('username', 'Unknown'),
            'spent': user.get('spent', 0),
            'joined': user.get('joined', 'N/A')
        })
    users_list.sort(key=lambda x: x['spent'], reverse=True)
    return render_template('users.html', users=users_list)

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'change_password':
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')
            admin = verify_admin()
            if hash_password(current_password) != admin['password']:
                flash('Current password is incorrect!', 'danger')
            elif new_password != confirm_password:
                flash('New passwords do not match!', 'danger')
            elif len(new_password) < 6:
                flash('Password must be at least 6 characters!', 'danger')
            else:
                admin['password'] = hash_password(new_password)
                with open(ADMIN_FILE, 'w') as f:
                    json.dump(admin, f, indent=2)
                flash('Password changed successfully!', 'success')
        elif action == 'update_welcome':
            welcome_message = request.form.get('welcome_message')
            config = load_config()
            config['welcome'] = welcome_message
            save_config(config)
            flash('Welcome message updated!', 'success')
    config = load_config()
    return render_template('settings.html', config=config)

@app.route('/api/stats')
@login_required
def api_stats():
    stats = get_dashboard_stats()
    return jsonify(stats)

if __name__ == '__main__':
    print("="*50)
    print(" Admin Panel Starting...")
    print("="*50)
    print(" URL: http://0.0.0.0:5000")
    print(" Username: admin")
    print(" Password: admin123")
    print("  CHANGE PASSWORD AFTER LOGIN!")
    print("="*50)
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)), debug=False)



