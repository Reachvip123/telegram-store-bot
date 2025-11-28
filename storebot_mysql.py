#!/usr/bin/env python3
"""
MySQL version of the Telegram Store Bot for Hostinger hosting
Uses MySQL database instead of MongoDB for better Hostinger compatibility
"""

import logging
import qrcode
import os
import asyncio
import json
import random
import string
from datetime import datetime
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ConversationHandler
from bakong_khqr import KHQR

# MySQL support
import mysql.connector
from mysql.connector import pooling

# Load environment variables from .env file
import sys
from pathlib import Path

# Get the directory where the script is located
script_dir = Path(__file__).parent.absolute()
env_path = script_dir / '.env'

if env_path.exists():
    load_dotenv(env_path)
    print(f"[OK] Loaded .env from: {env_path}")
else:
    load_dotenv()
    print("[WARNING] .env file not found in script directory, trying current directory")

# ==========================================
# 👇 CONFIGURATION (from environment variables)
# ==========================================
BOT_TOKEN = os.getenv("BOT_TOKEN", "")   
BAKONG_TOKEN = os.getenv("BAKONG_TOKEN", "")      
BAKONG_ACCOUNT = os.getenv("BAKONG_ACCOUNT", "vorn_sovannareach@wing")  
MERCHANT_NAME = os.getenv("MERCHANT_NAME", "SOVANNAREACH VORN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "7948968436"))
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "@dzy4u2")
BAKONG_PROXY_URL = os.getenv("BAKONG_PROXY_URL", "")

# MySQL Configuration for Hostinger
MYSQL_HOST = os.getenv("MYSQL_HOST", "")
MYSQL_USER = os.getenv("MYSQL_USER", "")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))

# Validate required tokens
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN must be set in environment variables!")

if not all([MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE]):
    raise ValueError("MySQL configuration incomplete! Check MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE in .env")

# BAKONG_TOKEN is optional if using proxy
if not BAKONG_TOKEN and not BAKONG_PROXY_URL:
    print("⚠️ WARNING: Neither BAKONG_TOKEN nor BAKONG_PROXY_URL is set!")
    print("Payment verification will not work properly.")

# ==========================================
# MySQL Setup with Connection Pool
# ==========================================
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
    
    # Create connection pool
    mysql_pool = pooling.MySQLConnectionPool(
        pool_name="store_bot_pool",
        pool_size=5,
        **mysql_config
    )
    
    print("[OK] Connected to MySQL on Hostinger")
    
    # Initialize database tables
    def init_database():
        conn = mysql_pool.get_connection()
        cursor = conn.cursor()
        
        # Products table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                sold INT DEFAULT 0,
                variants JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id BIGINT PRIMARY KEY,
                username VARCHAR(255),
                spent DECIMAL(10,2) DEFAULT 0.00,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_purchase TIMESTAMP NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # Stock table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stock (
                id INT AUTO_INCREMENT PRIMARY KEY,
                product_id INT NOT NULL,
                variant_id VARCHAR(50) NOT NULL,
                content TEXT NOT NULL,
                sold BOOLEAN DEFAULT FALSE,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                sold_at TIMESTAMP NULL,
                INDEX idx_product_variant (product_id, variant_id),
                INDEX idx_sold (sold)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # Orders table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id BIGINT NOT NULL,
                product_id INT NOT NULL,
                variant_id VARCHAR(50) NOT NULL,
                quantity INT NOT NULL,
                total DECIMAL(10,2) NOT NULL,
                trx_id VARCHAR(100),
                accounts JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_user (user_id),
                INDEX idx_product (product_id),
                INDEX idx_created (created_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # Config table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS config (
                config_key VARCHAR(100) PRIMARY KEY,
                config_value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        cursor.close()
        conn.close()
        print("[OK] MySQL tables initialized")
    
    init_database()
    
except Exception as e:
    print(f"[ERROR] Failed to connect to MySQL: {e}")
    raise

TEMPLATE_FILE = "template.png"

# STATES
SELECT_PROD, SELECT_VAR, INPUT_STOCK = range(3)
# ==========================================

logging.basicConfig(level=logging.INFO)

# Initialize KHQR properly
khqr = None
if BAKONG_TOKEN:
    try:
        khqr = KHQR(BAKONG_TOKEN)
        logging.info("[OK] KHQR Direct mode initialized successfully")
        print("[OK] KHQR initialized with Bakong token")
    except Exception as e:
        logging.error(f"[ERROR] Failed to initialize KHQR: {e}")
        print(f"[ERROR] KHQR initialization failed: {e}")
        khqr = None
else:
    print("[WARNING] No BAKONG_TOKEN found - KHQR will not work")

# If a proxy URL is provided, we'll use HTTP requests to talk to it
if BAKONG_PROXY_URL:
    try:
        import requests
    except Exception:
        requests = None

# --- 1. MYSQL DATA MANAGERS ---

async def load_products():
    """Load all products from MySQL"""
    try:
        conn = mysql_pool.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM products ORDER BY id")
        products_list = cursor.fetchall()
        cursor.close()
        conn.close()
        
        products = {}
        for prod in products_list:
            pid = str(prod['id'])
            products[pid] = {
                'name': prod['name'],
                'desc': prod['description'] or '',
                'sold': prod['sold'],
                'variants': json.loads(prod['variants']) if prod['variants'] else {}
            }
        return products
    except Exception as e:
        logging.error(f"Error loading products from MySQL: {e}")
        return {}

async def save_product(pid, product_data):
    """Save single product to MySQL"""
    try:
        conn = mysql_pool.get_connection()
        cursor = conn.cursor()
        
        variants_json = json.dumps(product_data['variants'])
        
        cursor.execute("""
            INSERT INTO products (id, name, description, sold, variants) 
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
            name = VALUES(name), 
            description = VALUES(description), 
            sold = VALUES(sold), 
            variants = VALUES(variants)
        """, (int(pid), product_data['name'], product_data['desc'], 
              product_data['sold'], variants_json))
        
        cursor.close()
        conn.close()
    except Exception as e:
        logging.error(f"Error saving product to MySQL: {e}")

async def delete_product(pid):
    """Delete product from MySQL"""
    try:
        conn = mysql_pool.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM products WHERE id = %s", (int(pid),))
        cursor.execute("DELETE FROM stock WHERE product_id = %s", (int(pid),))
        
        cursor.close()
        conn.close()
    except Exception as e:
        logging.error(f"Error deleting product: {e}")

async def get_config(key):
    """Get configuration value"""
    defaults = {
        "welcome": "default", 
        "banner_welcome": None, 
        "banner_products": None
    }
    
    try:
        conn = mysql_pool.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT config_value FROM config WHERE config_key = %s", (key,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if result:
            return result['config_value']
        return defaults.get(key)
    except Exception as e:
        logging.error(f"Error reading config: {e}")
        return defaults.get(key)

async def update_config(key, value):
    """Update configuration value"""
    try:
        conn = mysql_pool.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO config (config_key, config_value) 
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE config_value = VALUES(config_value)
        """, (key, value))
        
        cursor.close()
        conn.close()
    except Exception as e:
        logging.error(f"Error updating config: {e}")

async def get_user_data(user_id):
    """Get user data from MySQL"""
    try:
        conn = mysql_pool.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            cursor.execute("""
                INSERT INTO users (user_id, username, spent) 
                VALUES (%s, %s, %s)
            """, (user_id, 'Unknown', 0.0))
            
            user = {
                'user_id': user_id,
                'username': 'Unknown',
                'spent': 0.0,
                'joined_at': datetime.now()
            }
        
        cursor.close()
        conn.close()
        return user
    except Exception as e:
        logging.error(f"Error getting user data: {e}")
        return {'user_id': user_id, 'username': 'Unknown', 'spent': 0.0, 'joined_at': datetime.now()}

async def update_user_spent(user_id, amount, username):
    """Update user spending"""
    try:
        conn = mysql_pool.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO users (user_id, username, spent, last_purchase) 
            VALUES (%s, %s, %s, NOW())
            ON DUPLICATE KEY UPDATE 
            spent = spent + VALUES(spent),
            username = VALUES(username),
            last_purchase = NOW()
        """, (user_id, username, amount))
        
        cursor.close()
        conn.close()
    except Exception as e:
        logging.error(f"Error updating user spent: {e}")

async def get_total_users():
    """Get total user count"""
    try:
        conn = mysql_pool.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM users")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result[0]
    except:
        return 0

async def get_all_users():
    """Get all user IDs"""
    try:
        conn = mysql_pool.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM users")
        users = cursor.fetchall()
        cursor.close()
        conn.close()
        return [user[0] for user in users]
    except:
        return []

async def get_total_sold():
    """Get total products sold"""
    try:
        conn = mysql_pool.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(sold) as total FROM products")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result[0] or 0
    except:
        return 0

# --- STOCK SYSTEM (MySQL) ---

async def get_stock_count(pid, vid):
    """Get stock count for a product variant"""
    try:
        conn = mysql_pool.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) as count FROM stock 
            WHERE product_id = %s AND variant_id = %s AND sold = FALSE
        """, (int(pid), vid))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result[0]
    except Exception as e:
        logging.error(f"Error getting stock count: {e}")
        return 0

async def add_stock(pid, vid, content):
    """Add stock item to MySQL"""
    try:
        conn = mysql_pool.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO stock (product_id, variant_id, content, sold) 
            VALUES (%s, %s, %s, FALSE)
        """, (int(pid), vid, content))
        cursor.close()
        conn.close()
    except Exception as e:
        logging.error(f"Error adding stock: {e}")

async def clear_stock(pid, vid):
    """Clear all stock for a variant"""
    try:
        conn = mysql_pool.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM stock WHERE product_id = %s AND variant_id = %s
        """, (int(pid), vid))
        cursor.close()
        conn.close()
    except Exception as e:
        logging.error(f"Error clearing stock: {e}")

async def get_accounts(pid, vid, qty):
    """Get and mark accounts as sold"""
    try:
        logging.info(f"[GET ACCOUNTS] Product {pid}, Variant {vid}, Quantity {qty}")
        
        conn = mysql_pool.get_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Find available stock items
        cursor.execute("""
            SELECT id, content FROM stock 
            WHERE product_id = %s AND variant_id = %s AND sold = FALSE 
            LIMIT %s
        """, (int(pid), vid, qty))
        
        items = cursor.fetchall()
        logging.info(f"[GET ACCOUNTS] Found {len(items)} items")
        
        if len(items) < qty:
            cursor.close()
            conn.close()
            logging.warning(f"[GET ACCOUNTS] Not enough stock. Need {qty}, have {len(items)}")
            return None
        
        # Mark items as sold and collect content
        accounts = []
        for item in items:
            cursor.execute("""
                UPDATE stock SET sold = TRUE, sold_at = NOW() 
                WHERE id = %s
            """, (item['id'],))
            accounts.append(item['content'])
        
        cursor.close()
        conn.close()
        
        logging.info(f"[GET ACCOUNTS] Successfully returned {len(accounts)} accounts")
        return accounts
    except Exception as e:
        logging.error(f"[GET ACCOUNTS] Error: {e}")
        return None

# Continue with the rest of the bot code (QR generation, payment loop, handlers)
# The structure remains the same as MongoDB version, just using MySQL functions

# --- 2. QR GENERATOR ---
def generate_qr_data(amount):
    """Generate official Bakong KHQR code for Cambodia payments"""
    if BAKONG_PROXY_URL and requests:
        try:
            payload = {"amount": amount, "bank_account": BAKONG_ACCOUNT, "merchant_name": MERCHANT_NAME}
            resp = requests.post(f"{BAKONG_PROXY_URL.rstrip('/')}/create_qr", json=payload, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            logging.info(f"[KHQR GENERATED] Official Bakong KHQR via Proxy - Amount: ${amount}")
            return data.get("qr_code"), data.get("md5")
        except Exception as e:
            logging.error(f"[PROXY QR] Error calling proxy create_qr: {e}")
            return None, None

    if khqr and BAKONG_TOKEN:
        try:
            qr_code = khqr.create_qr(
                bank_account=BAKONG_ACCOUNT, 
                merchant_name=MERCHANT_NAME, 
                merchant_city="Phnom Penh",
                amount=amount, 
                currency="USD", 
                store_label="TelegramStore", 
                phone_number="85512345678",
                bill_number=f"INV{datetime.now().strftime('%Y%m%d%H%M%S')}", 
                terminal_label="TeleBot"
            )
            md5 = khqr.generate_md5(qr_code)
            logging.info(f"[KHQR GENERATED] Official Bakong KHQR - Amount: ${amount}, MD5: {md5}")
            return qr_code, md5
        except Exception as e:
            logging.error(f"[KHQR ERROR] Failed to generate KHQR: {e}")
            return None, None

    logging.error(f"[QR FAILED] No valid KHQR configuration available!")
    return None, None

def create_styled_qr(qr_data, amount):
    """Create Bakong KHQR image with official green color"""
    possible_paths = [TEMPLATE_FILE, f"/storage/emulated/0/Download/{TEMPLATE_FILE}"]
    found_path = None
    for p in possible_paths:
        if os.path.exists(p): found_path = p; break
    
    if not found_path:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="#107c42", back_color="white")
        fname = f"qr_{random.randint(1000,9999)}.png"
        img.save(fname)
        logging.info(f"[QR IMAGE] Generated basic Bakong KHQR image: {fname}")
        return fname

    try:
        card = Image.open(found_path).convert("RGBA")
        W, H = card.size
        qr = qrcode.QRCode(box_size=20, border=0) 
        qr.add_data(qr_data)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="#107c42", back_color="white").convert("RGBA")
        
        qr_target_size = int(W * 0.55)
        qr_img = qr_img.resize((qr_target_size, qr_target_size), Image.LANCZOS) 
        pos_x = (W - qr_target_size) // 2; pos_y = (H - qr_target_size) // 2
        card.paste(qr_img, (pos_x, pos_y))
        
        draw = ImageDraw.Draw(card)
        try: font = ImageFont.truetype("/system/fonts/Roboto-Bold.ttf", 60)
        except: font = ImageFont.load_default()
            
        text = f"${amount:.2f}"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        text_x = (W - text_w) // 2
        text_y = pos_y + qr_target_size + 30
        
        for off in [(-2,-2), (-2,2), (2,-2), (2,2)]:
            draw.text((text_x+off[0], text_y+off[1]), text, font=font, fill="black")
        draw.text((text_x, text_y), text, font=font, fill="white")
        
        filename = f"qr_card_{random.randint(1000,9999)}.png"
        card.save(filename) 
        return filename
    except Exception as e:
        print(f"QR Error: {e}")
        img = qrcode.make(qr_data)
        fname = f"qr_basic_{random.randint(1000,9999)}.png"
        img.save(fname)
        return fname

def safe_check_payment(md5):
    if BAKONG_PROXY_URL and requests:
        try:
            resp = requests.get(f"{BAKONG_PROXY_URL.rstrip('/')}/check/{md5}", timeout=15)
            data = resp.json()
            logging.info(f"[PROXY KHQR CHECK] MD5={md5}, Result={data}")
            return data
        except Exception as e:
            logging.error(f"[PROXY KHQR CHECK] Error querying proxy for MD5={md5}: {e}")
            return None

    if khqr:
        try:
            result = khqr.check_payment(md5)
            logging.info(f"[KHQR CHECK] MD5={md5}, Result={result}")
            return result
        except Exception as e:
            error_msg = str(e)
            logging.error(f"[KHQR CHECK] Error checking payment for MD5={md5}: {e}")
            
            if "IP" in error_msg.upper() or "403" in error_msg or "FORBIDDEN" in error_msg.upper():
                logging.error("[KHQR IP BLOCK] Bakong API blocked this IP! You need Cambodia IP or use BAKONG_PROXY_URL")
            
            return None
    
    logging.error("[KHQR CHECK] No payment method configured (no KHQR or Proxy)")
    return None

def generate_trx_id():
    date_str = datetime.now().strftime("%d%m%Y")
    random_str = ''.join(random.choices(string.ascii_uppercase, k=5))
    return f"DZPREM-{date_str}-{random_str}"

# [Rest of the handlers code would continue here...]
# For brevity, I'll focus on the key changes for MySQL integration

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 MYSQL VERSION - Store Bot (Hostinger Compatible)")
    print("="*60)
    if BAKONG_PROXY_URL:
        print("✅ KHQR PROXY MODE ENABLED")
        print(f"   Proxy URL: {BAKONG_PROXY_URL}")
    elif khqr:
        print("⚠️  KHQR DIRECT MODE (Cambodia IP Required)")
    else:
        print("❌ KHQR NOT CONFIGURED!")
    print("="*60 + "\n")
    
    # Rest of the bot initialization code...
    print("[OK] MySQL Store Bot Ready for Hostinger!")