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

# MongoDB support
from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient

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

# MongoDB Configuration
MONGODB_URI = os.getenv("MONGODB_URI", "")

# Validate required tokens
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN must be set in environment variables!")

if not MONGODB_URI:
    raise ValueError("MONGODB_URI must be set in environment variables for MongoDB version!")

# BAKONG_TOKEN is optional if using proxy
if not BAKONG_TOKEN and not BAKONG_PROXY_URL:
    print("⚠️ WARNING: Neither BAKONG_TOKEN nor BAKONG_PROXY_URL is set!")
    print("Payment verification will not work properly.")

# ==========================================
# MongoDB Setup
# ==========================================
try:
    # Synchronous client for initialization
    mongo_client = MongoClient(MONGODB_URI)
    # Test connection
    mongo_client.admin.command('ping')
    print("[OK] Connected to MongoDB Atlas")
    
    # Async client for async operations
    async_mongo_client = AsyncIOMotorClient(MONGODB_URI)
    
    # Database and collections
    db = async_mongo_client['telegram_store_bot']
    products_coll = db['products']
    users_coll = db['users']
    config_coll = db['config']
    stock_coll = db['stock']
    orders_coll = db['orders']
    
    print("[OK] MongoDB collections initialized")
except Exception as e:
    print(f"[ERROR] Failed to connect to MongoDB: {e}")
    print("Please check your MONGODB_URI in .env file")
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

# --- 1. MONGODB DATA MANAGERS ---

async def load_products():
    """Load all products from MongoDB"""
    try:
        products_list = await products_coll.find({}).to_list(length=1000)
        products = {}
        for prod in products_list:
            pid = str(prod['_id'])
            products[pid] = {
                'name': prod.get('name', ''),
                'desc': prod.get('desc', ''),
                'sold': prod.get('sold', 0),
                'variants': prod.get('variants', {})
            }
        return products
    except Exception as e:
        logging.error(f"Error loading products from MongoDB: {e}")
        return {}

async def save_product(pid, product_data):
    """Save single product to MongoDB"""
    try:
        await products_coll.update_one(
            {'_id': int(pid)},
            {'$set': product_data},
            upsert=True
        )
    except Exception as e:
        logging.error(f"Error saving product to MongoDB: {e}")

async def delete_product(pid):
    """Delete product from MongoDB"""
    try:
        await products_coll.delete_one({'_id': int(pid)})
        # Also delete associated stock
        await stock_coll.delete_many({'product_id': int(pid)})
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
        config = await config_coll.find_one({'key': key})
        if config:
            return config.get('value', defaults.get(key))
        return defaults.get(key)
    except Exception as e:
        logging.error(f"Error reading config: {e}")
        return defaults.get(key)

async def update_config(key, value):
    """Update configuration value"""
    try:
        await config_coll.update_one(
            {'key': key},
            {'$set': {'value': value, 'updated_at': datetime.now()}},
            upsert=True
        )
    except Exception as e:
        logging.error(f"Error updating config: {e}")

async def get_user_data(user_id):
    """Get user data from MongoDB"""
    try:
        user = await users_coll.find_one({'user_id': user_id})
        if not user:
            # Create new user
            new_user = {
                'user_id': user_id,
                'username': 'Unknown',
                'spent': 0.0,
                'joined': datetime.now(),
                'purchases': []
            }
            await users_coll.insert_one(new_user)
            return new_user
        return user
    except Exception as e:
        logging.error(f"Error getting user data: {e}")
        return {'user_id': user_id, 'username': 'Unknown', 'spent': 0.0, 'joined': datetime.now(), 'purchases': []}

async def update_user_spent(user_id, amount, username):
    """Update user spending and add purchase record"""
    try:
        await users_coll.update_one(
            {'user_id': user_id},
            {
                '$inc': {'spent': amount},
                '$set': {'username': username, 'last_purchase': datetime.now()},
                '$push': {'purchases': {
                    'amount': amount,
                    'timestamp': datetime.now()
                }}
            },
            upsert=True
        )
    except Exception as e:
        logging.error(f"Error updating user spent: {e}")

async def get_total_users():
    """Get total user count"""
    try:
        return await users_coll.count_documents({})
    except:
        return 0

async def get_all_users():
    """Get all user IDs"""
    try:
        users = await users_coll.find({}, {'user_id': 1}).to_list(length=10000)
        return [user['user_id'] for user in users]
    except:
        return []

async def get_total_sold():
    """Get total products sold"""
    try:
        products = await load_products()
        total = sum(p.get('sold', 0) for p in products.values())
        return total
    except:
        return 0

# --- STOCK SYSTEM (MongoDB) ---

async def get_stock_count(pid, vid):
    """Get stock count for a product variant"""
    try:
        count = await stock_coll.count_documents({
            'product_id': int(pid),
            'variant_id': vid,
            'sold': False
        })
        return count
    except Exception as e:
        logging.error(f"Error getting stock count: {e}")
        return 0

async def add_stock(pid, vid, content):
    """Add stock item to MongoDB"""
    try:
        stock_item = {
            'product_id': int(pid),
            'variant_id': vid,
            'content': content,
            'sold': False,
            'added_at': datetime.now()
        }
        await stock_coll.insert_one(stock_item)
    except Exception as e:
        logging.error(f"Error adding stock: {e}")

async def clear_stock(pid, vid):
    """Clear all stock for a variant"""
    try:
        await stock_coll.delete_many({
            'product_id': int(pid),
            'variant_id': vid
        })
    except Exception as e:
        logging.error(f"Error clearing stock: {e}")

async def get_accounts(pid, vid, qty):
    """Get and mark accounts as sold"""
    try:
        logging.info(f"[GET ACCOUNTS] Product {pid}, Variant {vid}, Quantity {qty}")
        
        # Find available stock items
        cursor = stock_coll.find({
            'product_id': int(pid),
            'variant_id': vid,
            'sold': False
        }).limit(qty)
        
        items = await cursor.to_list(length=qty)
        logging.info(f"[GET ACCOUNTS] Found {len(items)} items")
        
        if len(items) < qty:
            logging.warning(f"[GET ACCOUNTS] Not enough stock. Need {qty}, have {len(items)}")
            return None
        
        # Mark items as sold and collect content
        accounts = []
        for item in items:
            await stock_coll.update_one(
                {'_id': item['_id']},
                {'$set': {'sold': True, 'sold_at': datetime.now()}}
            )
            accounts.append(item['content'])
        
        logging.info(f"[GET ACCOUNTS] Successfully returned {len(accounts)} accounts")
        return accounts
    except Exception as e:
        logging.error(f"[GET ACCOUNTS] Error: {e}")
        return None

async def reindex_products():
    """Reindex products in MongoDB"""
    try:
        products = await load_products()
        sorted_keys = sorted(products.keys(), key=lambda x: int(x))
        
        # Delete all and re-insert with new IDs
        await products_coll.delete_many({})
        
        for i, old_id in enumerate(sorted_keys, 1):
            product = products[old_id]
            product['_id'] = i
            await products_coll.insert_one(product)
            
            # Update stock product_ids
            if old_id != str(i):
                await stock_coll.update_many(
                    {'product_id': int(old_id)},
                    {'$set': {'product_id': i}}
                )
    except Exception as e:
        logging.error(f"Error reindexing products: {e}")

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

# --- 3. BACKGROUND PAYMENT LOOP ---
async def check_payment_loop(update, context, md5_hash, qr_msg_id, pid, vid, qty):
    chat_id = update.effective_chat.id
    loop = asyncio.get_running_loop()
    products = await load_products()
    
    logging.info(f"[PAYMENT CHECK] Started for md5={md5_hash}, product={pid}, variant={vid}, qty={qty}")

    for attempt in range(120):
        await asyncio.sleep(5)
        
        try:
            if not khqr and not BAKONG_PROXY_URL:
                logging.error(f"[PAYMENT CHECK] KHQR not initialized! Cannot verify payment.")
                try:
                    await context.bot.edit_message_caption(
                        chat_id, qr_msg_id, 
                        caption="[ERROR] Payment system not configured properly. Please contact admin."
                    )
                except:
                    pass
                return
            
            response = await loop.run_in_executor(None, safe_check_payment, md5_hash)
            logging.info(f"[PAYMENT CHECK] Attempt {attempt+1}/120: Response = {response}")
            
            is_paid = False
            
            if str(response).strip().upper() == "PAID": 
                is_paid = True
            elif isinstance(response, dict) and response.get('responseCode') == 0: 
                is_paid = True
            elif isinstance(response, dict) and response.get('data', {}).get('responseCode') == 0:
                is_paid = True

            if is_paid:
                logging.info(f"[PAYMENT SUCCESS] Processing confirmed payment")
                try: 
                    await context.bot.delete_message(chat_id, qr_msg_id)
                except Exception as e: 
                    logging.error(f"Could not delete QR message: {e}")

                accounts = await get_accounts(pid, vid, qty)
                prod_name = products.get(pid, {}).get('name', 'Unknown')
                var_name = products.get(pid, {}).get('variants', {}).get(vid, {}).get('name', 'Unknown')
                price = products.get(pid, {}).get('variants', {}).get(vid, {}).get('price', 0)
                total = price * qty
                trx_id = generate_trx_id()

                if accounts:
                    await update_user_spent(chat_id, total, update.effective_user.username)
                    
                    # Update product sold count
                    await products_coll.update_one(
                        {'_id': int(pid)},
                        {'$inc': {'sold': qty}}
                    )
                    
                    # Save order to MongoDB
                    order = {
                        'user_id': chat_id,
                        'product_id': int(pid),
                        'variant_id': vid,
                        'quantity': qty,
                        'total': total,
                        'trx_id': trx_id,
                        'timestamp': datetime.now(),
                        'accounts': accounts
                    }
                    await orders_coll.insert_one(order)

                    acc_text = ""
                    tutorial_url = products.get(pid, {}).get('variants', {}).get(vid, {}).get('tutorial')
                    for i, acc in enumerate(accounts):
                        acc_text += f"\nItem Details #{i+1}\n"
                        if "," in acc:
                            parts = [p.strip() for p in acc.split(",")]
                            u = parts[0] if len(parts) > 0 else "N/A"
                            p = parts[1] if len(parts) > 1 else "N/A"
                            details_parts = parts[2:]
                        else:
                            parts = [acc.strip()]
                            u = parts[0]
                            p = "N/A"
                            details_parts = []

                        acc_text += f"Email/Username : `{u}`\n"
                        acc_text += f"Password : `{p}`\n\n"
                        if details_parts:
                            acc_text += "Additional Information:\n"
                            acc_text += "\n".join(details_parts) + "\n\n"

                        if tutorial_url:
                            acc_text += f"[Tutorial Sign In]({tutorial_url})\n"
                        acc_text += "\n"

                    text = (
                        "[OK] PAYMENT CONFIRMED\n"
                        "Thank you, your payment has been received!\n\n"
                        "Order Details:\n"
                        "= = = = = = = = = = = = = = = = = = = = = =\n"
                        f"Product: {prod_name}\n"
                        f"Variant: {var_name}\n"
                        f"Quantity: x{qty}\n"
                        f"Total: ${total:.2f}\n"
                        "= = = = = = = = = = = = = = = = = = = = = =\n"
                        f"{acc_text}\n"
                        f"Transaction ID: `{trx_id}`"
                    )
                else:
                    text = f"[OK] PAID\n[ALERT] OUT OF STOCK!\nAdmin notified."
                    try:
                        await context.bot.send_message(ADMIN_ID, f"[ALERT] OOS: {prod_name} ({qty} pcs) Paid but empty!")
                    except Exception as e:
                        logging.error(f"Failed to notify admin: {e}")

                try:
                    await context.bot.send_message(chat_id, text, parse_mode='Markdown', disable_web_page_preview=True)
                except Exception as e:
                    logging.error(f"Failed to send confirmation: {e}")
                    try:
                        await context.bot.send_message(chat_id, text)
                    except:
                        pass
                return
        except Exception as e:
            logging.error(f"[PAYMENT CHECK] Error in loop iteration {attempt+1}: {e}")

    # Timeout
    try: 
        await context.bot.edit_message_caption(
            chat_id, qr_msg_id, 
            caption="[EXPIRED] Payment timeout after 10 minutes.\n\nNo payment was detected. Please try again or contact admin if you already paid."
        )
    except Exception as e:
        logging.error(f"Failed to update timeout message: {e}")

# --- 4. UI HANDLERS ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_data = await get_user_data(user.id)
    
    now = datetime.now().strftime("%A, %d %B %Y %H:%M:%S")
    sold = await get_total_sold()
    total_users = await get_total_users()
    
    raw_welcome = await get_config("welcome")
    
    if raw_welcome == "default":
         welcome_text = (
            f"Hello {user.first_name} 👋🏼\n"
            f"{now}\n\n"
            "**User Info :**\n"
            f"└ ID : `{user.id}`\n"
            f"└ Username : @{user.username}\n"
            f"└ Transactions : ${user_data['spent']:.2f}\n\n"
            "**BOT Stats :**\n"
            f"└ Sold : {sold:,} pcs\n"
            f"└ Total Users : {total_users:,}\n\n"
            "**Shortcuts :**\n"
            "/start – Start bot\n"
            "/stock – Check product stock\n"
            "/help – how to use bot"
        )
    else:
        welcome_text = raw_welcome.replace("{name}", user.first_name)

    keyboard = [["🛍 List Products", "👤 My Profile"], ["❓ Help", "📦 Check Stock"]]
    if user.id == ADMIN_ID: keyboard.append(["🛠 Admin Panel"])
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    banner = await get_config("banner_welcome")
    if banner:
        try: await update.message.reply_photo(banner, caption=welcome_text, reply_markup=markup, parse_mode='Markdown')
        except: await update.message.reply_text(welcome_text, reply_markup=markup, parse_mode='Markdown')
    else:
        await update.message.reply_text(welcome_text, reply_markup=markup, parse_mode='Markdown')

async def show_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    products = await load_products()
    list_text = "╭ - - - - - - - - - - - - - - - - - - - ╮\n┊  **PRODUCT LIST**\n┊  _page 1 / 1_\n┊- - - - - - - - - - - - - - - - - - - - -\n"
    keyboard = []; row = []
    
    sorted_pids = sorted(products.keys(), key=lambda x: int(x))

    for pid in sorted_pids:
        data = products[pid]
        list_text += f"┊ [{pid}] {data['name'].upper()}\n"
        row.append(InlineKeyboardButton(f"{pid}", callback_data=f"view_{pid}"))
        if len(row) == 4: keyboard.append(row); row = []
    if row: keyboard.append(row)
    list_text += "╰ - - - - - - - - - - - - - - - - - - - ╯"
    markup = InlineKeyboardMarkup(keyboard)
    
    banner = await get_config("banner_products")
    if banner:
        try: await update.message.reply_photo(banner, caption=list_text, reply_markup=markup, parse_mode='Markdown')
        except: await update.message.reply_text(list_text, reply_markup=markup, parse_mode='Markdown')
    else: await update.message.reply_text(list_text, reply_markup=markup, parse_mode='Markdown')

async def show_stock_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    products = await load_products()
    msg = "**PRODUCT STOCK REPORT**\n╭ - - - - - - - - - - - - - - - - - - - - - ╮\n"
    has = False
    for pid in sorted(products.keys(), key=lambda x: int(x)):
        p = products[pid]
        for vid, v in p['variants'].items():
            count = await get_stock_count(pid, vid)
            icon = "✅" if count > 0 else "❌"
            msg += f"┊ {icon} {p['name']} {v['name']} : {count}x\n"
            has = True
    if not has: msg += "┊ No products.\n"
    msg += "╰ - - - - - - - - - - - - - - - - - - - - - ╯"
    await update.message.reply_text(msg, parse_mode='Markdown')

async def show_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"For assistance, please contact admin: {ADMIN_USERNAME}")

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer() 
    callback_data = query.data
    
    if callback_data.startswith("stock"): 
        return 

    products = await load_products()
    
    if callback_data == "back_list":
        action = "back_list"
        data = []
    else:
        data = callback_data.split("_")
        action = data[0]

    if action == "view":
        pid = data[1]
        if pid not in products: return
        prod = products[pid]
        text = f"╭ - - - - - - - - - - - - - - - - - - - ╮\n┊ • **Product:** {prod['name']}\n┊ • **Sold:** {prod['sold']} pcs\n┊ • **Desc:** {prod['desc']}\n╰ - - - - - - - - - - - - - - - - - - - ╯\n╭ - - - - - - - - - - - - - - - - - - - ╮\n┊ **Select Variation:**\n"
        keyboard = []
        if query.from_user.id == ADMIN_ID:
             keyboard.append([InlineKeyboardButton("🗑 DELETE PRODUCT", callback_data=f"delprod_{pid}")])
        for vid, var in prod['variants'].items():
            stock = await get_stock_count(pid, vid)
            status = "🟢" if stock > 0 else "🔴"
            text += f"┊ • {var['name']} (${var['price']:.2f}) - {status}\n"
            row = [InlineKeyboardButton(f"{var['name']} - ${var['price']:.2f}", callback_data=f"confirm_{pid}_{vid}_1")]
            if query.from_user.id == ADMIN_ID:
                row.append(InlineKeyboardButton("🗑", callback_data=f"delvar_{pid}_{vid}"))
            keyboard.append(row)
        text += "╰ - - - - - - - - - - - - - - - - - - - ╯"
        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="back_list")])
        markup = InlineKeyboardMarkup(keyboard)
        try:
            if query.message.photo: await query.edit_message_caption(caption=text, reply_markup=markup, parse_mode='Markdown')
            else: await query.edit_message_text(text=text, reply_markup=markup, parse_mode='Markdown')
        except: await query.message.reply_text(text, reply_markup=markup, parse_mode='Markdown')

    elif action == "back_list":
        products = await load_products()
        list_text = "╭ - - - - - - - - - - - - - - - - - - - ╮\n┊  **PRODUCT LIST**\n┊  _page 1 / 1_\n┊- - - - - - - - - - - - - - - - - - - - -\n"
        keyboard = []; row = []
        
        sorted_pids = sorted(products.keys(), key=lambda x: int(x))

        for pid in sorted_pids:
            prod_data = products[pid]
            list_text += f"┊ [{pid}] {prod_data['name'].upper()}\n"
            row.append(InlineKeyboardButton(f"{pid}", callback_data=f"view_{pid}"))
            if len(row) == 4: keyboard.append(row); row = []
        if row: keyboard.append(row)
        list_text += "╰ - - - - - - - - - - - - - - - - - - - ╯"
        markup = InlineKeyboardMarkup(keyboard)
        
        try:
            if query.message.photo:
                await query.edit_message_caption(caption=list_text, reply_markup=markup, parse_mode='Markdown')
            else:
                await query.edit_message_text(text=list_text, reply_markup=markup, parse_mode='Markdown')
        except Exception as e:
            logging.error(f"Error editing message: {e}")
            await query.message.reply_text(list_text, reply_markup=markup, parse_mode='Markdown')

    elif action == "confirm":
        if len(data) < 4: return
        pid, vid, qty = data[1], data[2], int(data[3])
        prod = products[pid]; var = prod['variants'][vid]
        stock = await get_stock_count(pid, vid)
        
        if qty > stock and stock > 0:
             await query.answer(f"⚠️ Max available is {stock}", show_alert=True)
             qty = stock
        if qty < 1:
             await query.answer("⚠️ Minimum 1", show_alert=True)
             qty = 1

        total = var['price'] * qty
        text = f"**ORDER CONFIRMATION** 🛒\n╭ - - - - - - - - - - - - - - - - - - - - - ╮\n┊・Product: {prod['name']}\n┊・Variation: {var['name']}\n┊・Unit Price: ${var['price']:.2f}\n┊・Available Stock: {stock}\n┊ - - - - - - - - - - - - - - - - - - - - - \n┊・Order Quantity: x{qty}\n┊・Total Payment: ${total:.2f}\n╰ - - - - - - - - - - - - - - - - - - - - - ╯"
        minus = max(1, qty - 1); plus = min(stock, qty + 1) if stock > 0 else qty + 1
        keyboard = [
            [InlineKeyboardButton(f"- 1", callback_data=f"confirm_{pid}_{vid}_{minus}"), InlineKeyboardButton(f"+ 1", callback_data=f"confirm_{pid}_{vid}_{plus}")],
            [InlineKeyboardButton(f"✅ Pay with KHQR (${total:.2f})", callback_data=f"pay_{pid}_{vid}_{qty}")],
            [InlineKeyboardButton("🔙 Back", callback_data=f"view_{pid}"), InlineKeyboardButton("🔄 Refresh", callback_data=f"confirm_{pid}_{vid}_{qty}")]
        ]
        try:
            if query.message.photo: await query.edit_message_caption(caption=text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
            else: await query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
        except: pass

    elif action == "cancel":
        try: await query.message.delete(); await context.bot.send_message(query.message.chat_id, "❌ Order Cancelled.", parse_mode='Markdown')
        except: pass

    elif action == "pay":
        if len(data) < 4: return
        pid, vid, qty = data[1], data[2], int(data[3])
        prod = products[pid]; var = prod['variants'][vid]; total = var['price'] * qty
        stock_count = await get_stock_count(pid, vid)
        if stock_count < qty:
            await query.message.reply_text("❌ **Sold Out!** Please check back later.", parse_mode='Markdown')
            return
        
        await query.message.reply_text(f"⏳ Generating Bakong KHQR code...")
        qr_text, md5 = generate_qr_data(total)
        
        if not qr_text or not md5:
            error_msg = (
                "❌ **Payment System Error**\n\n"
                "Unable to generate KHQR payment code.\n"
                f"Please contact admin: {ADMIN_USERNAME}"
            )
            await query.message.reply_text(error_msg, parse_mode='Markdown')
            try:
                await context.bot.send_message(ADMIN_ID, f"⚠️ KHQR Generation Failed!\nUser: {query.from_user.id}\nProduct: {prod['name']}\nAmount: ${total}")
            except:
                pass
            return
        
        filename = create_styled_qr(qr_text, total)
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel Transaction", callback_data="cancel")]])
        
        caption = (
            f"💳 **BAKONG KHQR PAYMENT**\n"
            f"Amount: **${total:.2f}**\n"
            f"Product: {prod['name']} x{qty}\n\n"
            f"🇰🇭 Scan with any Bakong app\n"
            f"⏳ _Waiting for payment..._"
        )
        
        msg = await query.message.reply_photo(
            photo=open(filename, 'rb'), 
            caption=caption,
            parse_mode='Markdown', 
            reply_markup=markup
        )
        os.remove(filename)
        asyncio.create_task(check_payment_loop(update, context, md5, msg.message_id, pid, vid, qty))

    elif action == "delprod":
        pid = data[1]
        if query.from_user.id != ADMIN_ID: return
        await delete_product(pid)
        await reindex_products()
        await query.message.delete()
        await context.bot.send_message(query.message.chat_id, f"🗑 Product {pid} Deleted.")
        await show_products(update, context)

    elif action == "delvar":
        pid, vid = data[1], data[2]
        if query.from_user.id != ADMIN_ID: return
        if pid in products and vid in products[pid]['variants']:
            await clear_stock(pid, vid)
            products[pid]['variants'].pop(vid, None)
            await save_product(pid, products[pid])
            await context.bot.send_message(query.message.chat_id, f"🗑 Variant {vid} Deleted.")
            await show_products(update, context)

# --- 5. ADMIN LOGIC ---

async def start_add_stock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return ConversationHandler.END
    products = await load_products()
    if not products: await update.message.reply_text("❌ No products."); return ConversationHandler.END
    keyboard = []
    for pid in sorted(products.keys(), key=lambda x: int(x)):
        p = products[pid]
        keyboard.append([InlineKeyboardButton(p['name'], callback_data=f"stock_prod_{pid}")])
    keyboard.append([InlineKeyboardButton("❌ Cancel", callback_data="stock_cancel")])
    await update.message.reply_text("📦 **Select Product:**", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    return SELECT_PROD

async def select_product_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query; await query.answer()
    if query.data == "stock_cancel": await query.message.edit_text("❌ Cancelled."); return ConversationHandler.END
    pid = query.data.split("_")[2]
    context.user_data['stock_pid'] = pid
    products = await load_products(); prod = products[pid]
    keyboard = []
    for vid, var in prod['variants'].items():
        keyboard.append([InlineKeyboardButton(f"{var['name']}", callback_data=f"stock_var_{vid}")])
    keyboard.append([InlineKeyboardButton("❌ Cancel", callback_data="stock_cancel")])
    await query.message.edit_text(f"📦 **{prod['name']}**\nSelect Variant:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    return SELECT_VAR

async def select_variant_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query; await query.answer()
    if query.data == "stock_cancel": await query.message.edit_text("❌ Cancelled."); return ConversationHandler.END
    vid = query.data.split("_")[2]
    context.user_data['stock_vid'] = vid
    await query.message.edit_text(f"📥 Send data now.\nFormat: `email,pass,info`\n(Send multiple lines)", parse_mode='Markdown')
    return INPUT_STOCK

async def receive_stock_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pid = context.user_data.get('stock_pid')
    vid = context.user_data.get('stock_vid')
    text = update.message.text
    lines = text.split('\n'); count = 0
    for line in lines:
        if line.strip(): 
            await add_stock(pid, vid, line.strip())
            count += 1
    await update.message.reply_text(f"✅ **Success!** Added {count} items.", parse_mode='Markdown')
    return ConversationHandler.END

async def cancel_op(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Cancelled.")
    return ConversationHandler.END

async def cmd_add_product_easy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    try:
        if not context.args:
            await update.message.reply_text("⚠️ Usage: `/addpd Name | Variant | Price | Desc`", parse_mode='Markdown')
            return
        raw = " ".join(context.args)
        parts = [p.strip() for p in raw.split("|")]
        if len(parts) < 4:
            await update.message.reply_text("⚠️ Usage: `/addpd Name | Variant | Price | Desc`", parse_mode='Markdown')
            return
        name, var_name, price_str, desc = parts[0], parts[1], parts[2], parts[3]
        
        try:
            price = float(price_str)
        except:
            await update.message.reply_text("❌ Price must be a number.", parse_mode='Markdown')
            return
        
        products = await load_products()
        pid = next((k for k, v in products.items() if v['name'].lower() == name.lower()), None)
        if not pid:
            pid = str(max([int(k) for k in products.keys()] or [0]) + 1)
            product_data = {"name": name, "desc": desc, "sold": 0, "variants": {}}
        else:
            product_data = products[pid]
        
        vid = var_name.replace(" ", "").upper()[:3]
        product_data['variants'][vid] = {"name": var_name, "price": price}
        await save_product(pid, product_data)
        await update.message.reply_text(f"✅ Added! **{name}** ({var_name}) - ${price:.2f}", parse_mode='Markdown')
    except Exception as e:
        logging.error(f"Error adding product: {e}")
        await update.message.reply_text(f"❌ Error: {e}")

async def cmd_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    
    if not context.args:
        await update.message.reply_text("⚠️ Usage: `/broadcast <message>`", parse_mode='Markdown')
        return
    
    msg = " ".join(context.args)
    users = await get_all_users()
    
    if not users:
        await update.message.reply_text("ℹ️ No users to broadcast to.")
        return
    
    await update.message.reply_text(f"📢 Sending to {len(users)} users...")
    success = 0; failed = 0
    
    for uid in users:
        try:
            await context.bot.send_message(uid, f"📢 **NOTICE:**\n{msg}", parse_mode='Markdown')
            success += 1
        except Exception as e:
            failed += 1
    
    await update.message.reply_text(f"✅ Done. Sent: {success}, Failed: {failed}")

async def cmd_admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    await update.message.reply_text(
        "🛠 **ADMIN MENU (MongoDB Version)**\n\n"
        "`/addpd Name | Var | Price | Desc`\n"
        "`/addstock` (Interactive)\n"
        "`/setbanner_welcome URL`\n"
        "`/setbanner_products URL`\n"
        "`/broadcast Msg`\n"
        "`/testkhqr` - Test KHQR generation\n"
        "`/stats` - View MongoDB stats", 
        parse_mode='Markdown'
    )

async def cmd_test_khqr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    
    await update.message.reply_text("🧪 Testing KHQR generation...")
    test_amount = 0.01
    qr_text, md5 = generate_qr_data(test_amount)
    
    if not qr_text or not md5:
        await update.message.reply_text("❌ **KHQR Test FAILED**\nCheck configuration!", parse_mode='Markdown')
        return
    
    filename = create_styled_qr(qr_text, test_amount)
    success_msg = f"✅ **KHQR Test SUCCESS**\n• Amount: ${test_amount}\n• MD5: `{md5[:16]}...`"
    
    await update.message.reply_photo(photo=open(filename, 'rb'), caption=success_msg, parse_mode='Markdown')
    try: os.remove(filename)
    except: pass

async def cmd_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show MongoDB database statistics"""
    if update.effective_user.id != ADMIN_ID: return
    
    try:
        total_products = await products_coll.count_documents({})
        total_users_count = await users_coll.count_documents({})
        total_stock = await stock_coll.count_documents({'sold': False})
        total_orders = await orders_coll.count_documents({})
        sold_stock = await stock_coll.count_documents({'sold': True})
        
        stats_text = (
            "📊 **MongoDB Database Stats**\n\n"
            f"Products: {total_products}\n"
            f"Users: {total_users_count}\n"
            f"Available Stock: {total_stock}\n"
            f"Sold Items: {sold_stock}\n"
            f"Total Orders: {total_orders}\n\n"
            f"🌐 **MongoDB Atlas**: View detailed stats at https://cloud.mongodb.com"
        )
        
        await update.message.reply_text(stats_text, parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"❌ Error fetching stats: {e}")

async def cmd_set_banner_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    try:
        if not context.args:
            await update.message.reply_text("⚠️ Usage: `/setbanner_welcome <image_url>`", parse_mode='Markdown')
            return
        await update_config("banner_welcome", context.args[0])
        await update.message.reply_text("✅ Welcome Banner Updated!")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def cmd_set_banner_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    try:
        if not context.args:
            await update.message.reply_text("⚠️ Usage: `/setbanner_products <image_url>`", parse_mode='Markdown')
            return
        await update_config("banner_products", context.args[0])
        await update.message.reply_text("✅ Products Banner Updated!")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "🛍 List Products": await show_products(update, context)
    elif text == "👤 My Profile": await start(update, context)
    elif text == "🛠 Admin Panel": await cmd_admin_menu(update, context)
    elif text == "❓ Help": await show_help(update, context)
    elif text == "📦 Check Stock": await show_stock_report(update, context)

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 MONGODB VERSION - Store Bot")
    print("="*60)
    if BAKONG_PROXY_URL:
        print("✅ KHQR PROXY MODE ENABLED")
        print(f"   Proxy URL: {BAKONG_PROXY_URL}")
    elif khqr:
        print("⚠️  KHQR DIRECT MODE (Cambodia IP Required)")
    else:
        print("❌ KHQR NOT CONFIGURED!")
    print("="*60 + "\n")
    
    async def error_handler(update, context):
        logging.error(f"[BOT ERROR] Update: {update}", exc_info=context.error)
    
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_error_handler(error_handler)
    
    stock_conv = ConversationHandler(
        entry_points=[CommandHandler('addstock', start_add_stock)],
        states={
            SELECT_PROD: [CallbackQueryHandler(select_product_callback, pattern="^stock_prod_")],
            SELECT_VAR: [CallbackQueryHandler(select_variant_callback, pattern="^stock_var_")],
            INPUT_STOCK: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_stock_data)]
        },
        fallbacks=[CommandHandler('cancel', cancel_op), CallbackQueryHandler(select_product_callback, pattern="^stock_cancel$")]
    )

    application.add_handler(stock_conv)
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('admin', cmd_admin_menu))
    application.add_handler(CommandHandler('addpd', cmd_add_product_easy))
    application.add_handler(CommandHandler('setbanner_welcome', cmd_set_banner_welcome))
    application.add_handler(CommandHandler('setbanner_products', cmd_set_banner_products))
    application.add_handler(CommandHandler('broadcast', cmd_broadcast))
    application.add_handler(CommandHandler('stock', show_stock_report))
    application.add_handler(CommandHandler('help', show_help))
    application.add_handler(CommandHandler('testkhqr', cmd_test_khqr))
    application.add_handler(CommandHandler('stats', cmd_stats))
    application.add_handler(CallbackQueryHandler(button_click))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("[OK] MongoDB Store Bot Running...")
    application.run_polling()
