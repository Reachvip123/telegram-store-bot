#!/usr/bin/env python3
"""
API Bridge for Web Admin Panel
This runs on your Cambodia VPS and provides HTTP API access to MongoDB
Your Hostinger web panel will connect to this API
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import pymongo
import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

# MongoDB connection
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb+srv://dztsorebase:reachvip@cluster0.tbyhuzf.mongodb.net")
DATABASE_NAME = os.getenv("DATABASE_NAME", "storebot")

# Simple API key for security
API_KEY = os.getenv("API_KEY", "your-secret-api-key-change-this")

def get_db():
    """Get MongoDB database connection"""
    try:
        client = pymongo.MongoClient(MONGODB_URI)
        return client[DATABASE_NAME]
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def verify_api_key():
    """Verify API key from request"""
    api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
    return api_key == API_KEY

@app.before_request
def before_request():
    """Check API key for all requests except health check"""
    if request.endpoint == 'health':
        return
    
    if not verify_api_key():
        return jsonify({'error': 'Invalid API key'}), 401

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'service': 'Store Bot API',
        'timestamp': datetime.now().isoformat(),
        'location': 'Cambodia VPS'
    })

@app.route('/api/stats')
def get_stats():
    """Get dashboard statistics"""
    try:
        db = get_db()
        if not db:
            return jsonify({'error': 'Database connection failed'}), 500
        
        # Get product count
        products_count = db.products.count_documents({})
        
        # Get user count
        users_count = db.users.count_documents({})
        
        # Get total sold items
        total_sold_pipeline = [
            {'$group': {'_id': None, 'total_sold': {'$sum': '$sold'}}}
        ]
        sold_result = list(db.products.aggregate(total_sold_pipeline))
        total_sold = sold_result[0]['total_sold'] if sold_result else 0
        
        # Get stock count
        stock_count = db.stock.count_documents({'sold': False})
        
        return jsonify({
            'success': True,
            'products': products_count,
            'users': users_count,
            'sold': total_sold,
            'stock': stock_count,
            'last_updated': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/products')
def get_products():
    """Get all products"""
    try:
        db = get_db()
        if not db:
            return jsonify({'error': 'Database connection failed'}), 500
        
        products_cursor = db.products.find({})
        products = {}
        
        for product in products_cursor:
            product_id = str(product['_id'])
            products[product_id] = {
                'name': product.get('name', ''),
                'desc': product.get('desc', ''),
                'sold': product.get('sold', 0),
                'variants': product.get('variants', {})
            }
        
        return jsonify({
            'success': True,
            'products': products
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/products/<product_id>')
def get_product(product_id):
    """Get specific product"""
    try:
        db = get_db()
        if not db:
            return jsonify({'error': 'Database connection failed'}), 500
        
        from bson import ObjectId
        product = db.products.find_one({'_id': ObjectId(product_id)})
        
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        return jsonify({
            'success': True,
            'product': {
                'id': str(product['_id']),
                'name': product.get('name', ''),
                'desc': product.get('desc', ''),
                'sold': product.get('sold', 0),
                'variants': product.get('variants', {})
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/products', methods=['POST'])
def add_product():
    """Add new product"""
    try:
        db = get_db()
        if not db:
            return jsonify({'error': 'Database connection failed'}), 500
        
        data = request.get_json()
        
        product_doc = {
            'name': data.get('name', ''),
            'desc': data.get('description', ''),
            'sold': 0,
            'variants': json.loads(data.get('variants', '{}')) if isinstance(data.get('variants'), str) else data.get('variants', {}),
            'created_at': datetime.now()
        }
        
        result = db.products.insert_one(product_doc)
        
        return jsonify({
            'success': True,
            'product_id': str(result.inserted_id),
            'message': 'Product added successfully'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/products/<product_id>', methods=['DELETE'])
def delete_product(product_id):
    """Delete product"""
    try:
        db = get_db()
        if not db:
            return jsonify({'error': 'Database connection failed'}), 500
        
        from bson import ObjectId
        
        # Delete product
        result = db.products.delete_one({'_id': ObjectId(product_id)})
        
        if result.deleted_count == 0:
            return jsonify({'error': 'Product not found'}), 404
        
        # Delete related stock
        db.stock.delete_many({'product_id': product_id})
        
        return jsonify({
            'success': True,
            'message': 'Product deleted successfully'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stock/<product_id>/<variant_id>')
def get_stock(product_id, variant_id):
    """Get stock for product variant"""
    try:
        db = get_db()
        if not db:
            return jsonify({'error': 'Database connection failed'}), 500
        
        # Get available stock
        available_count = db.stock.count_documents({
            'product_id': product_id,
            'variant_id': variant_id,
            'sold': False
        })
        
        # Get sold stock
        sold_count = db.stock.count_documents({
            'product_id': product_id,
            'variant_id': variant_id,
            'sold': True
        })
        
        return jsonify({
            'success': True,
            'available': available_count,
            'sold': sold_count
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stock', methods=['POST'])
def add_stock():
    """Add stock items"""
    try:
        db = get_db()
        if not db:
            return jsonify({'error': 'Database connection failed'}), 500
        
        data = request.get_json()
        product_id = data.get('product_id')
        variant_id = data.get('variant_id')
        stock_items = data.get('stock_items', [])
        
        if not all([product_id, variant_id, stock_items]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Add each stock item
        stock_docs = []
        for item in stock_items:
            stock_docs.append({
                'product_id': product_id,
                'variant_id': variant_id,
                'content': item,
                'sold': False,
                'added_at': datetime.now()
            })
        
        result = db.stock.insert_many(stock_docs)
        
        return jsonify({
            'success': True,
            'added_count': len(result.inserted_ids),
            'message': f'Added {len(result.inserted_ids)} stock items'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/users')
def get_users():
    """Get all users"""
    try:
        db = get_db()
        if not db:
            return jsonify({'error': 'Database connection failed'}), 500
        
        users_cursor = db.users.find({}).limit(100)  # Limit for performance
        users = []
        
        for user in users_cursor:
            users.append({
                'user_id': user.get('user_id'),
                'username': user.get('username', 'Unknown'),
                'spent': user.get('spent', 0),
                'joined_at': user.get('joined_at', '').isoformat() if hasattr(user.get('joined_at', ''), 'isoformat') else str(user.get('joined_at', ''))
            })
        
        return jsonify({
            'success': True,
            'users': users,
            'count': len(users)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/orders')
def get_orders():
    """Get recent orders"""
    try:
        db = get_db()
        if not db:
            return jsonify({'error': 'Database connection failed'}), 500
        
        # Get recent orders with user and product info
        orders_cursor = db.orders.find({}).sort('timestamp', -1).limit(50)
        orders = []
        
        for order in orders_cursor:
            # Get product name
            product = db.products.find_one({'_id': order.get('product_id')})
            product_name = product.get('name', 'Unknown Product') if product else 'Unknown Product'
            
            # Get user info
            user = db.users.find_one({'user_id': order.get('user_id')})
            username = user.get('username', 'Unknown') if user else 'Unknown'
            
            orders.append({
                'id': str(order['_id']),
                'user_id': order.get('user_id'),
                'username': username,
                'product_id': str(order.get('product_id', '')),
                'product_name': product_name,
                'variant_id': order.get('variant_id', ''),
                'quantity': order.get('quantity', 0),
                'total': order.get('total', 0),
                'trx_id': order.get('trx_id', ''),
                'timestamp': order.get('timestamp', '').isoformat() if hasattr(order.get('timestamp', ''), 'isoformat') else str(order.get('timestamp', ''))
            })
        
        return jsonify({
            'success': True,
            'orders': orders,
            'count': len(orders)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/clear_stock', methods=['POST'])
def clear_stock():
    """Clear stock for product variant"""
    try:
        db = get_db()
        if not db:
            return jsonify({'error': 'Database connection failed'}), 500
        
        data = request.get_json()
        product_id = data.get('product_id')
        variant_id = data.get('variant_id')
        
        if not all([product_id, variant_id]):
            return jsonify({'error': 'Missing product_id or variant_id'}), 400
        
        result = db.stock.delete_many({
            'product_id': product_id,
            'variant_id': variant_id,
            'sold': False
        })
        
        return jsonify({
            'success': True,
            'deleted_count': result.deleted_count,
            'message': f'Cleared {result.deleted_count} stock items'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/database_info')
def database_info():
    """Get database information"""
    try:
        db = get_db()
        if not db:
            return jsonify({'error': 'Database connection failed'}), 500
        
        # Get collection stats
        collections_info = {}
        for collection_name in ['products', 'users', 'stock', 'orders']:
            try:
                count = db[collection_name].count_documents({})
                collections_info[collection_name] = count
            except:
                collections_info[collection_name] = 0
        
        return jsonify({
            'success': True,
            'database': DATABASE_NAME,
            'collections': collections_info,
            'server_time': datetime.now().isoformat(),
            'connection_status': 'active'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🔗 API Bridge for Web Admin Panel")
    print("="*60)
    print(f"🎯 Purpose: Provide HTTP API access to MongoDB")
    print(f"📡 Location: Cambodia VPS")
    print(f"🌐 Will be accessed by: Hostinger Web Panel")
    print(f"🔑 API Key: {API_KEY}")
    print(f"⚡ Port: 8081")
    print("="*60 + "\n")
    print("📋 Available Endpoints:")
    print("  GET  /health                - Health check")
    print("  GET  /api/stats             - Dashboard statistics") 
    print("  GET  /api/products          - List all products")
    print("  POST /api/products          - Add new product")
    print("  GET  /api/products/<id>     - Get specific product")
    print("  DEL  /api/products/<id>     - Delete product")
    print("  GET  /api/stock/<pid>/<vid> - Get stock for variant")
    print("  POST /api/stock             - Add stock items")
    print("  POST /api/clear_stock       - Clear variant stock")
    print("  GET  /api/users             - List users")
    print("  GET  /api/orders            - List recent orders")
    print("  GET  /api/database_info     - Database information")
    print("\n🚀 Starting API server...")
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=8081, debug=False)