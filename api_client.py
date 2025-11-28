"""
API Client Wrapper for Admin Panel
Handles both local file mode and API mode
"""
import os
import json
import requests

# Configuration
try:
    from admin_config import USE_API, API_URL, API_KEY
except:
    USE_API = os.environ.get('USE_API', 'false').lower() == 'true'
    API_URL = os.environ.get('API_URL', 'http://157.10.73.90:5000')
    API_KEY = os.environ.get('API_KEY', 'your-secret-api-key-change-this')

DB_FOLDER = "database"
PRODUCTS_FILE = f"{DB_FOLDER}/products.json"
USERS_FILE = f"{DB_FOLDER}/users.json"
CONFIG_FILE = f"{DB_FOLDER}/config.json"

class APIClient:
    """Client for both API and local file access"""
    
    @staticmethod
    def _api_call(method, endpoint, data=None):
        """Make API request"""
        headers = {'X-API-Key': API_KEY, 'Content-Type': 'application/json'}
        url = f"{API_URL}{endpoint}"
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=data, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, headers=headers, json=data, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=10)
            
            if response.status_code in [200, 201]:
                return response.json()
            return None
        except Exception as e:
            print(f"API Error: {e}")
            return None
    
    @staticmethod
    def _load_local_json(filepath):
        """Load local JSON file"""
        if not os.path.exists(filepath):
            return {}
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @staticmethod
    def _save_local_json(filepath, data):
        """Save local JSON file"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    # Products
    @staticmethod
    def get_products():
        if USE_API:
            result = APIClient._api_call('GET', '/api/products')
            return result if result else {}
        return APIClient._load_local_json(PRODUCTS_FILE)
    
    @staticmethod
    def save_products(data):
        if USE_API:
            # For now, update individual products via API
            return True
        APIClient._save_local_json(PRODUCTS_FILE, data)
        return True
    
    @staticmethod
    def add_product(product_data):
        if USE_API:
            return APIClient._api_call('POST', '/api/products', product_data)
        products = APIClient.get_products()
        product_id = str(len(products) + 1)
        products[product_id] = product_data
        APIClient.save_products(products)
        return {'success': True, 'product_id': product_id}
    
    @staticmethod
    def update_product(product_id, product_data):
        if USE_API:
            return APIClient._api_call('PUT', f'/api/products/{product_id}', product_data)
        products = APIClient.get_products()
        if product_id in products:
            products[product_id].update(product_data)
            APIClient.save_products(products)
            return {'success': True}
        return {'success': False}
    
    @staticmethod
    def delete_product(product_id):
        if USE_API:
            return APIClient._api_call('DELETE', f'/api/products/{product_id}')
        products = APIClient.get_products()
        if product_id in products:
            del products[product_id]
            APIClient.save_products(products)
            return {'success': True}
        return {'success': False}
    
    # Stock
    @staticmethod
    def get_all_stock():
        if USE_API:
            result = APIClient._api_call('GET', '/api/stock')
            return result if result else []
        # Local implementation
        products = APIClient.get_products()
        stock_data = []
        for pid, product in products.items():
            for vid, variant in product.get('variants', {}).items():
                stock_file = f"{DB_FOLDER}/stock_{pid}_{vid}.txt"
                count = 0
                if os.path.exists(stock_file):
                    with open(stock_file, 'r') as f:
                        count = len([line for line in f if line.strip()])
                stock_data.append({
                    'product_id': pid,
                    'product_name': product['name'],
                    'variant_id': vid,
                    'variant_name': variant,
                    'stock_count': count
                })
        return stock_data
    
    @staticmethod
    def get_stock(product_id, variant_id):
        if USE_API:
            result = APIClient._api_call('GET', f'/api/stock/{product_id}/{variant_id}')
            return result if result else {'accounts': [], 'count': 0}
        stock_file = f"{DB_FOLDER}/stock_{product_id}_{variant_id}.txt"
        if not os.path.exists(stock_file):
            return {'accounts': [], 'count': 0}
        with open(stock_file, 'r') as f:
            accounts = [line.strip() for line in f if line.strip()]
        return {'accounts': accounts, 'count': len(accounts)}
    
    @staticmethod
    def add_stock(product_id, variant_id, accounts):
        if USE_API:
            return APIClient._api_call('POST', f'/api/stock/{product_id}/{variant_id}', {'accounts': accounts})
        stock_file = f"{DB_FOLDER}/stock_{product_id}_{variant_id}.txt"
        os.makedirs(DB_FOLDER, exist_ok=True)
        with open(stock_file, 'a') as f:
            for account in accounts:
                f.write(account.strip() + '\n')
        return {'success': True, 'added': len(accounts)}
    
    @staticmethod
    def clear_stock(product_id, variant_id):
        if USE_API:
            return APIClient._api_call('DELETE', f'/api/stock/{product_id}/{variant_id}')
        stock_file = f"{DB_FOLDER}/stock_{product_id}_{variant_id}.txt"
        if os.path.exists(stock_file):
            os.remove(stock_file)
        return {'success': True}
    
    # Users
    @staticmethod
    def get_users():
        if USE_API:
            result = APIClient._api_call('GET', '/api/users')
            return result if result else {}
        return APIClient._load_local_json(USERS_FILE)
    
    # Config
    @staticmethod
    def get_config():
        if USE_API:
            result = APIClient._api_call('GET', '/api/config')
            return result if result else {}
        return APIClient._load_local_json(CONFIG_FILE)
    
    @staticmethod
    def save_config(data):
        if USE_API:
            return APIClient._api_call('PUT', '/api/config', data)
        APIClient._save_local_json(CONFIG_FILE, data)
        return {'success': True}
    
    # Stats
    @staticmethod
    def get_stats():
        if USE_API:
            result = APIClient._api_call('GET', '/api/stats')
            return result if result else {}
        # Local calculation
        products = APIClient.get_products()
        users = APIClient.get_users()
        
        stock_count = 0
        products_in_stock = 0
        for pid, product in products.items():
            for vid in product.get('variants', {}).keys():
                stock_file = f"{DB_FOLDER}/stock_{pid}_{vid}.txt"
                if os.path.exists(stock_file):
                    with open(stock_file, 'r') as f:
                        count = len([line for line in f if line.strip()])
                        stock_count += count
                        if count > 0:
                            products_in_stock += 1
        
        total_revenue = sum(user.get('total_spent', 0) for user in users.values())
        total_sold = sum(user.get('purchases', 0) for user in users.values())
        
        return {
            'total_products': len(products),
            'total_revenue': total_revenue,
            'total_users': len(users),
            'stock_count': stock_count,
            'products_in_stock': products_in_stock,
            'total_sold': total_sold
        }
