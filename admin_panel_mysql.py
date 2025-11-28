#!/usr/bin/env python3
"""
MySQL Web Admin Panel for Telegram Store Bot (Hostinger Compatible)
This version uses MySQL instead of MongoDB for Hostinger hosting
"""

from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import mysql.connector
from mysql.connector import pooling
import json
import os
from datetime import datetime
from dotenv import load_dotenv
import bcrypt

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-change-this')

# MySQL Configuration for Hostinger
MYSQL_HOST = os.getenv("MYSQL_HOST", "")
MYSQL_USER = os.getenv("MYSQL_USER", "")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))

# Admin credentials
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

# Validate MySQL configuration
if not all([MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE]):
    print("ERROR: MySQL configuration incomplete!")
    print("Please set MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE in .env file")
    exit(1)

# Initialize MySQL Connection Pool
try:
    mysql_config = {
        'host': MYSQL_HOST,
        'user': MYSQL_USER,
        'password': MYSQL_PASSWORD,
        'database': MYSQL_DATABASE,
        'port': MYSQL_PORT,
        'autocommit': True,
        'charset': 'utf8mb4',
        'collation': 'utf8mb4_unicode_ci'
    }
    
    mysql_pool = pooling.MySQLConnectionPool(
        pool_name="admin_pool",
        pool_size=3,
        **mysql_config
    )
    
    print(f"✅ Connected to MySQL on Hostinger: {MYSQL_HOST}")
except Exception as e:
    print(f"❌ Failed to connect to MySQL: {e}")
    exit(1)

def get_db_connection():
    """Get database connection from pool"""
    return mysql_pool.get_connection()

def check_password(password):
    """Check if password is correct"""
    return password == ADMIN_PASSWORD

@app.route('/')
def index():
    """Redirect to dashboard"""
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login"""
    if request.method == 'POST':
        password = request.form.get('password', '')
        
        if check_password(password):
            session['admin_logged_in'] = True
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid password!', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Admin logout"""
    session.clear()
    flash('Logged out successfully!', 'info')
    return redirect(url_for('login'))

def login_required(f):
    """Decorator to require login"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash('Please login to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/dashboard')
@login_required
def dashboard():
    """Admin dashboard with statistics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get statistics
        cursor.execute("SELECT COUNT(*) as count FROM products")
        total_products = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM users")
        total_users = cursor.fetchone()['count']
        
        cursor.execute("SELECT SUM(sold) as total FROM products")
        result = cursor.fetchone()
        total_sold = result['total'] or 0
        
        cursor.execute("SELECT COUNT(*) as count FROM stock WHERE sold = FALSE")
        total_stock = cursor.fetchone()['count']
        
        # Get recent orders
        cursor.execute("""
            SELECT o.*, p.name as product_name, u.username 
            FROM orders o
            LEFT JOIN products p ON o.product_id = p.id
            LEFT JOIN users u ON o.user_id = u.user_id
            ORDER BY o.created_at DESC
            LIMIT 5
        """)
        recent_orders = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        stats = {
            'total_products': total_products,
            'total_users': total_users,
            'total_sold': total_sold,
            'total_stock': total_stock,
            'recent_orders': recent_orders
        }
        
        return render_template('dashboard.html', stats=stats)
    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}', 'error')
        return render_template('dashboard.html', stats={})

@app.route('/products')
@login_required
def products():
    """Products management page"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM products ORDER BY id")
        products_list = cursor.fetchall()
        
        # Parse variants JSON and add stock counts
        for product in products_list:
            if product['variants']:
                product['variants'] = json.loads(product['variants'])
            else:
                product['variants'] = {}
            
            # Get stock count for each variant
            product['stock_info'] = {}
            for variant_id, variant_data in product['variants'].items():
                cursor.execute("""
                    SELECT COUNT(*) as count FROM stock 
                    WHERE product_id = %s AND variant_id = %s AND sold = FALSE
                """, (product['id'], variant_id))
                stock_count = cursor.fetchone()['count']
                product['stock_info'][variant_id] = stock_count
        
        cursor.close()
        conn.close()
        
        return render_template('products.html', products=products_list)
    except Exception as e:
        flash(f'Error loading products: {str(e)}', 'error')
        return render_template('products.html', products=[])

@app.route('/add_product', methods=['GET', 'POST'])
@login_required
def add_product():
    """Add new product"""
    if request.method == 'POST':
        try:
            name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip()
            
            if not name:
                flash('Product name is required!', 'error')
                return render_template('add_product.html')
            
            # Create variants structure
            variants = {}
            variant_count = 1
            
            while True:
                variant_name = request.form.get(f'variant_name_{variant_count}', '').strip()
                variant_price = request.form.get(f'variant_price_{variant_count}', '').strip()
                
                if not variant_name or not variant_price:
                    break
                
                try:
                    price = float(variant_price)
                    variants[f"var_{variant_count}"] = {
                        "name": variant_name,
                        "price": price
                    }
                except ValueError:
                    flash(f'Invalid price for variant {variant_count}', 'error')
                    return render_template('add_product.html')
                
                variant_count += 1
            
            if not variants:
                flash('At least one variant is required!', 'error')
                return render_template('add_product.html')
            
            # Save to database
            conn = get_db_connection()
            cursor = conn.cursor()
            
            variants_json = json.dumps(variants)
            cursor.execute("""
                INSERT INTO products (name, description, sold, variants) 
                VALUES (%s, %s, %s, %s)
            """, (name, description, 0, variants_json))
            
            cursor.close()
            conn.close()
            
            flash('Product added successfully!', 'success')
            return redirect(url_for('products'))
            
        except Exception as e:
            flash(f'Error adding product: {str(e)}', 'error')
    
    return render_template('add_product.html')

@app.route('/delete_product/<int:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    """Delete product"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Delete product and related stock
        cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
        cursor.execute("DELETE FROM stock WHERE product_id = %s", (product_id,))
        
        cursor.close()
        conn.close()
        
        flash('Product deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting product: {str(e)}', 'error')
    
    return redirect(url_for('products'))

@app.route('/stock')
@login_required
def stock():
    """Stock management page"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get products with their variants
        cursor.execute("SELECT id, name, variants FROM products ORDER BY id")
        products_list = cursor.fetchall()
        
        # Parse variants and get stock counts
        for product in products_list:
            product['variants'] = json.loads(product['variants']) if product['variants'] else {}
            product['stock_counts'] = {}
            
            for variant_id, variant_data in product['variants'].items():
                cursor.execute("""
                    SELECT COUNT(*) as available, 
                           SUM(CASE WHEN sold = TRUE THEN 1 ELSE 0 END) as sold_count
                    FROM stock 
                    WHERE product_id = %s AND variant_id = %s
                """, (product['id'], variant_id))
                result = cursor.fetchone()
                product['stock_counts'][variant_id] = {
                    'available': result['available'] - (result['sold_count'] or 0),
                    'sold': result['sold_count'] or 0
                }
        
        cursor.close()
        conn.close()
        
        return render_template('stock.html', products=products_list)
    except Exception as e:
        flash(f'Error loading stock: {str(e)}', 'error')
        return render_template('stock.html', products=[])

@app.route('/add_stock', methods=['POST'])
@login_required
def add_stock():
    """Add stock items"""
    try:
        product_id = int(request.form.get('product_id'))
        variant_id = request.form.get('variant_id')
        stock_data = request.form.get('stock_data', '').strip()
        
        if not stock_data:
            flash('Stock data is required!', 'error')
            return redirect(url_for('stock'))
        
        # Split stock data by lines and clean
        lines = [line.strip() for line in stock_data.split('\n') if line.strip()]
        
        if not lines:
            flash('No valid stock items found!', 'error')
            return redirect(url_for('stock'))
        
        # Add each line as a stock item
        conn = get_db_connection()
        cursor = conn.cursor()
        
        for line in lines:
            cursor.execute("""
                INSERT INTO stock (product_id, variant_id, content, sold) 
                VALUES (%s, %s, %s, FALSE)
            """, (product_id, variant_id, line))
        
        cursor.close()
        conn.close()
        
        flash(f'Added {len(lines)} stock items successfully!', 'success')
    except Exception as e:
        flash(f'Error adding stock: {str(e)}', 'error')
    
    return redirect(url_for('stock'))

@app.route('/clear_stock', methods=['POST'])
@login_required
def clear_stock():
    """Clear stock for variant"""
    try:
        product_id = int(request.form.get('product_id'))
        variant_id = request.form.get('variant_id')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM stock 
            WHERE product_id = %s AND variant_id = %s AND sold = FALSE
        """, (product_id, variant_id))
        
        cursor.close()
        conn.close()
        
        flash('Stock cleared successfully!', 'success')
    except Exception as e:
        flash(f'Error clearing stock: {str(e)}', 'error')
    
    return redirect(url_for('stock'))

@app.route('/users')
@login_required
def users():
    """Users management page"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT user_id, username, spent, joined_at, last_purchase
            FROM users 
            ORDER BY spent DESC, joined_at DESC
        """)
        users_list = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return render_template('users.html', users=users_list)
    except Exception as e:
        flash(f'Error loading users: {str(e)}', 'error')
        return render_template('users.html', users=[])

@app.route('/orders')
@login_required
def orders():
    """Orders management page"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT o.*, p.name as product_name, u.username 
            FROM orders o
            LEFT JOIN products p ON o.product_id = p.id
            LEFT JOIN users u ON o.user_id = u.user_id
            ORDER BY o.created_at DESC
            LIMIT 100
        """)
        orders_list = cursor.fetchall()
        
        # Parse accounts JSON for display
        for order in orders_list:
            if order['accounts']:
                try:
                    order['accounts'] = json.loads(order['accounts'])
                except:
                    order['accounts'] = []
            else:
                order['accounts'] = []
        
        cursor.close()
        conn.close()
        
        return render_template('orders.html', orders=orders_list)
    except Exception as e:
        flash(f'Error loading orders: {str(e)}', 'error')
        return render_template('orders.html', orders=[])

@app.route('/api/get_variants/<int:product_id>')
@login_required
def get_variants(product_id):
    """API to get variants for a product"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT variants FROM products WHERE id = %s", (product_id,))
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if result and result['variants']:
            variants = json.loads(result['variants'])
            return jsonify({'success': True, 'variants': variants})
        else:
            return jsonify({'success': False, 'message': 'No variants found'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🌐 MySQL Admin Panel for Hostinger")
    print("="*60)
    print(f"📊 Database: {MYSQL_HOST}")
    print(f"🔑 Admin Password: {ADMIN_PASSWORD}")
    print("🚀 Starting Flask Admin Panel...")
    print("="*60 + "\n")
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=8080, debug=True)