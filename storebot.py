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

# Load environment variables from .env file
load_dotenv()

# ==========================================
# 👇 CONFIGURATION (from environment variables)
# ==========================================
BOT_TOKEN = os.getenv("BOT_TOKEN", "")   
BAKONG_TOKEN = os.getenv("BAKONG_TOKEN", "")      
BAKONG_ACCOUNT = os.getenv("BAKONG_ACCOUNT", "vorn_sovannareach@wing")  
MERCHANT_NAME = os.getenv("MERCHANT_NAME", "SOVANNAREACH VORN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "7948968436"))
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "@dzy4u2")
BAKONG_PROXY_URL = os.getenv("BAKONG_PROXY_URL", "")  # optional proxy endpoint hosted in Cambodia

# Validate required tokens
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN must be set in environment variables!")

# BAKONG_TOKEN is optional if using proxy
if not BAKONG_TOKEN and not BAKONG_PROXY_URL:
    print("⚠️ WARNING: Neither BAKONG_TOKEN nor BAKONG_PROXY_URL is set!")
    print("Payment verification will not work properly.")

# --- DATABASE SETUP (Local JSON fallback or MongoDB) ---
USE_MONGODB = os.getenv("USE_MONGODB", "false").lower() == "true"
MONGODB_URI = os.getenv("MONGODB_URI", "")

if USE_MONGODB and MONGODB_URI:
    from pymongo import MongoClient
    mongo_client = MongoClient(MONGODB_URI)
    db = mongo_client['telegram_store_bot']
    products_collection = db['products']
    config_collection = db['config']
    users_collection = db['users']
    print("[OK] Connected to MongoDB")
else:
    # Local file storage fallback
    DB_FOLDER = "database"
    if not os.path.exists(DB_FOLDER):
        os.makedirs(DB_FOLDER)
    PRODUCTS_FILE = f"{DB_FOLDER}/products.json"
    CONFIG_FILE = f"{DB_FOLDER}/config.json"
    USERS_FILE = f"{DB_FOLDER}/users.json"
    products_collection = None
    print("[OK] Using local file storage")

TEMPLATE_FILE = "template.png" # Keep in root folder for easy access

# STATES
SELECT_PROD, SELECT_VAR, INPUT_STOCK = range(3)
# ==========================================

logging.basicConfig(level=logging.INFO)

# Initialize KHQR properly
khqr = None
if BAKONG_TOKEN and not BAKONG_PROXY_URL:
    try:
        khqr = KHQR(BAKONG_TOKEN)
        logging.info("[OK] KHQR Direct mode initialized (WARNING: Requires Cambodia IP)")
    except Exception as e:
        logging.error(f"[ERROR] Failed to initialize KHQR: {e}")
        logging.warning("[WARNING] If you're outside Cambodia, use BAKONG_PROXY_URL instead")
        khqr = None

# If a proxy URL is provided, we'll use HTTP requests to talk to it
if BAKONG_PROXY_URL:
    try:
        import requests
    except Exception:
        requests = None

# --- 1. DATA MANAGERS ---

def load_products():
    try:
        if not os.path.exists(PRODUCTS_FILE):
            data = {
                "1": {
                    "name": "CAPCUT PRO",
                    "desc": "Premium Video Editor",
                    "sold": 0,
                    "variants": {"1M": {"name": "1 Month", "price": 0.01}}
                }
            }
            with open(PRODUCTS_FILE, 'w') as f:
                json.dump(data, f, indent=2)
            
            # Create dummy stock
            stock_path = f"{DB_FOLDER}/stock_1_1M.txt"
            if not os.path.exists(stock_path):
                with open(stock_path, "w") as f:
                    f.write("user: test@gmail.com | pass: 123456\n" * 5)
            return data
        
        with open(PRODUCTS_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error loading products: {e}")
        return {}

def save_products(data):
    try:
        with open(PRODUCTS_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logging.error(f"Error saving products: {e}")

def get_config(key):
    defaults = {
        "welcome": "default", 
        "banner_welcome": None, 
        "banner_products": None
    }
    
    try:
        if not os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'w') as f:
                json.dump(defaults, f, indent=2)
            return defaults.get(key)
        
        with open(CONFIG_FILE, 'r') as f:
            data = json.load(f)
            return data.get(key, defaults.get(key))
    except Exception as e:
        logging.error(f"Error reading config: {e}")
        return defaults.get(key)

def update_config(key, value):
    try:
        config = {}
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
            except Exception as e:
                logging.warning(f"Could not read config file: {e}")
        config[key] = value
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        logging.error(f"Error updating config: {e}")

def get_user_data(user_id):
    try:
        users = {}
        if os.path.exists(USERS_FILE):
            try:
                with open(USERS_FILE, 'r') as f:
                    users = json.load(f)
            except Exception as e:
                logging.warning(f"Could not read users file: {e}")
        
        uid = str(user_id)
        if uid not in users:
            users[uid] = {"username": "Unknown", "spent": 0.0, "joined": str(datetime.now())}
            with open(USERS_FILE, 'w') as f:
                json.dump(users, f, indent=2)
        return users[uid]
    except Exception as e:
        logging.error(f"Error getting user data: {e}")
        return {"username": "Unknown", "spent": 0.0, "joined": str(datetime.now())}

def update_user_spent(user_id, amount, username):
    try:
        users = {}
        if os.path.exists(USERS_FILE):
            try:
                with open(USERS_FILE, 'r') as f:
                    users = json.load(f)
            except Exception as e:
                logging.warning(f"Could not read users file: {e}")
        
        uid = str(user_id)
        if uid not in users:
            users[uid] = {"spent": 0.0, "joined": str(datetime.now())}
        
        users[uid]["spent"] += amount
        users[uid]["username"] = username
        
        with open(USERS_FILE, 'w') as f:
            json.dump(users, f, indent=2)
    except Exception as e:
        logging.error(f"Error updating user spent: {e}")

def get_total_users():
    if not os.path.exists(USERS_FILE): return 0
    try:
        with open(USERS_FILE, 'r') as f:
            return len(json.load(f))
    except:
        return 0

def get_all_users():
    if not os.path.exists(USERS_FILE): return []
    try:
        with open(USERS_FILE, 'r') as f:
            users = json.load(f)
            return [int(uid) for uid in users.keys()]
    except:
        return []

def get_total_sold():
    products = load_products()
    total = 0
    for p in products.values():
        total += p.get('sold', 0)
    return total

# --- STOCK SYSTEM ---
def get_stock_file(pid, vid):
    safe_vid = str(vid).replace(" ", "").upper()
    return f"{DB_FOLDER}/stock_{pid}_{safe_vid}.txt"

def get_stock_count(pid, vid):
    try:
        filename = get_stock_file(pid, vid)
        if not os.path.exists(filename): return 0
        with open(filename, "r") as f:
            lines = [l for l in f.readlines() if l.strip()]
        return len(lines)
    except Exception as e:
        logging.error(f"Error getting stock count: {e}")
        return 0

def add_stock(pid, vid, content):
    try:
        filename = get_stock_file(pid, vid)
        with open(filename, "a") as f:
            f.write(f"{content}\n")
    except Exception as e:
        logging.error(f"Error adding stock: {e}")

def clear_stock(pid, vid):
    filename = get_stock_file(pid, vid)
    if os.path.exists(filename):
        os.remove(filename)

def get_accounts(pid, vid, qty):
    try:
        filename = get_stock_file(pid, vid)
        logging.info(f"[GET ACCOUNTS] Looking for stock file: {filename}")
        if not os.path.exists(filename):
            logging.warning(f"[GET ACCOUNTS] Stock file NOT found: {filename}")
            return None
        
        with open(filename, "r") as f:
            lines = f.readlines()
        
        logging.info(f"[GET ACCOUNTS] Stock file has {len(lines)} lines")
        valid = [l for l in lines if l.strip()]
        logging.info(f"[GET ACCOUNTS] Valid lines after filtering: {len(valid)}")
        
        if len(valid) < qty:
            logging.warning(f"[GET ACCOUNTS] Not enough valid accounts. Need {qty}, have {len(valid)}")
            return None
        
        accounts = [line.strip() for line in valid[:qty]]
        logging.info(f"[GET ACCOUNTS] Got {len(accounts)} accounts, remaining: {len(valid) - qty}")
        
        with open(filename, "w") as f:
            f.writelines(valid[qty:])
        
        logging.info(f"[GET ACCOUNTS] Successfully returned {len(accounts)} accounts")
        return accounts
    except Exception as e:
        logging.error(f"[GET ACCOUNTS] Error getting accounts: {e}")
        return None

def delete_product_files(pid):
    products = load_products()
    if pid in products:
        for vid in products[pid]['variants']:
            fname = get_stock_file(pid, vid)
            if os.path.exists(fname):
                os.remove(fname)

def reindex_products():
    products = load_products()
    new_products = {}
    sorted_keys = sorted(products.keys(), key=lambda x: int(x))
    
    moves = []
    for i, old_id in enumerate(sorted_keys, 1):
        new_id = str(i)
        new_products[new_id] = products[old_id]
        if old_id != new_id:
            for vid in products[old_id]['variants']:
                moves.append((old_id, new_id, vid))
    
    for old_id, new_id, vid in moves:
        old_f = get_stock_file(old_id, vid)
        new_f = get_stock_file(new_id, vid)
        if os.path.exists(old_f):
            try:
                with open(old_f, 'r') as f: content = f.read()
                with open(new_f, 'w') as f: f.write(content)
                os.remove(old_f)
            except: pass
            
    save_products(new_products)

# --- 2. QR GENERATOR ---
def generate_qr_data(amount):
    """Generate official Bakong KHQR code for Cambodia payments"""
    # If a proxy is configured (must be hosted in Cambodia), use it to create QR
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
            # Generate official Bakong KHQR code
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

    # No valid KHQR method available
    logging.error(f"[QR FAILED] No valid KHQR configuration available!")
    return None, None

def create_styled_qr(qr_data, amount):
    """Create Bakong KHQR image with official green color"""
    possible_paths = [TEMPLATE_FILE, f"/storage/emulated/0/Download/{TEMPLATE_FILE}"]
    found_path = None
    for p in possible_paths:
        if os.path.exists(p): found_path = p; break
    
    # Generate basic KHQR image if no template
    if not found_path:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        # Official Bakong green color
        img = qr.make_image(fill_color="#107c42", back_color="white")
        fname = f"qr_{random.randint(1000,9999)}.png"
        img.save(fname)
        logging.info(f"[QR IMAGE] Generated basic Bakong KHQR image: {fname}")
        return fname

    try:
        # Create styled KHQR with template
        card = Image.open(found_path).convert("RGBA")
        W, H = card.size
        qr = qrcode.QRCode(box_size=20, border=0) 
        qr.add_data(qr_data)
        qr.make(fit=True)
        # Official Bakong green color (#107c42)
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
    # If proxy is configured, ask proxy to check payment (proxy should be in Cambodia)
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
            
            # Check if it's an IP restriction error
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
    products = load_products()
    
    logging.info(f"[PAYMENT CHECK] Started for md5={md5_hash}, qr_msg_id={qr_msg_id}, product={pid}, variant={vid}, qty={qty}")

    for attempt in range(120):  # Check for 10 minutes (120 * 5 seconds)
        await asyncio.sleep(5)  # Wait 5 seconds before checking
        
        try:
            # Check if KHQR is available (not in testing mode)
            if not khqr and not BAKONG_PROXY_URL:
                logging.error(f"[PAYMENT CHECK] KHQR not initialized! Cannot verify payment. MD5={md5_hash}")
                try:
                    await context.bot.edit_message_caption(
                        chat_id, qr_msg_id, 
                        caption="[ERROR] Payment system not configured properly. Please contact admin."
                    )
                except:
                    pass
                return
            
            # Verify payment through KHQR or Proxy
            response = await loop.run_in_executor(None, safe_check_payment, md5_hash)
            logging.info(f"[PAYMENT CHECK] Attempt {attempt+1}/120: Response = {response}")
            
            is_paid = False
            
            # Check response format
            if str(response).strip().upper() == "PAID": 
                is_paid = True
                logging.info(f"[PAYMENT CHECK] Payment detected as PAID (string response)")
            elif isinstance(response, dict) and response.get('responseCode') == 0: 
                is_paid = True
                logging.info(f"[PAYMENT CHECK] Payment confirmed via responseCode=0 (dict response)")
            elif isinstance(response, dict) and response.get('data', {}).get('responseCode') == 0:
                is_paid = True
                logging.info(f"[PAYMENT CHECK] Payment confirmed via data.responseCode=0")

            if is_paid:
                logging.info(f"[PAYMENT SUCCESS] Processing confirmed payment")
                try: 
                    await context.bot.delete_message(chat_id, qr_msg_id)
                    logging.info(f"[PAYMENT SUCCESS] QR message deleted")
                except Exception as e: 
                    logging.error(f"[PAYMENT SUCCESS] Could not delete QR message: {e}")

                accounts = get_accounts(pid, vid, qty)
                prod_name = products.get(pid, {}).get('name', 'Unknown')
                var_name = products.get(pid, {}).get('variants', {}).get(vid, {}).get('name', 'Unknown')
                price = products.get(pid, {}).get('variants', {}).get(vid, {}).get('price', 0)
                total = price * qty
                trx_id = generate_trx_id()
                
                logging.info(f"[PAYMENT SUCCESS] Got accounts: {accounts}")

                if accounts:
                    logging.info(f"[PAYMENT SUCCESS] Processing {len(accounts)} accounts")
                    update_user_spent(chat_id, total, update.effective_user.username)
                    if pid in products:
                        products[pid]['sold'] = products[pid].get('sold', 0) + qty
                        save_products(products)

                    acc_text = ""
                    # Build detailed account text with multiple info lines and optional tutorial link
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
                            # each detail part on its own line
                            acc_text += "\n".join(details_parts) + "\n\n"

                        # Add tutorial link if set for this variant
                        if tutorial_url:
                            # Markdown link
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
                    logging.info(f"[PAYMENT SUCCESS] Accounts found and message prepared")
                else:
                    logging.warning(f"[PAYMENT SUCCESS] No accounts found! get_accounts returned None")
                    text = f"[OK] PAID\n[ALERT] OUT OF STOCK!\nAdmin notified."
                    try:
                        await context.bot.send_message(ADMIN_ID, f"[ALERT] OOS: {prod_name} ({qty} pcs) Paid but empty!")
                        logging.info(f"[PAYMENT SUCCESS] Out of stock alert sent to admin")
                    except Exception as e:
                        logging.error(f"[PAYMENT SUCCESS] Failed to notify admin: {e}")

                try:
                    await context.bot.send_message(chat_id, text, parse_mode='Markdown', disable_web_page_preview=True)
                    logging.info(f"[PAYMENT SUCCESS] Confirmation message sent to user")
                except Exception as e:
                    logging.error(f"[PAYMENT SUCCESS] Failed to send confirmation: {e}")
                    # Try sending without markdown if it fails
                    try:
                        await context.bot.send_message(chat_id, text)
                        logging.info(f"[PAYMENT SUCCESS] Confirmation sent (plain text fallback)")
                    except Exception as e2:
                        logging.error(f"[PAYMENT SUCCESS] Failed to send even with fallback: {e2}")
                return
        except Exception as e:
            logging.error(f"[PAYMENT CHECK] Error in loop iteration {attempt+1}: {e}")

    # Timeout - no payment received
    try: 
        await context.bot.edit_message_caption(
            chat_id, qr_msg_id, 
            caption="[EXPIRED] Payment timeout after 10 minutes.\n\nNo payment was detected. Please try again or contact admin if you already paid."
        )
        logging.warning(f"[PAYMENT TIMEOUT] No payment received after 10 minutes for MD5={md5_hash}")
    except Exception as e:
        logging.error(f"[PAYMENT TIMEOUT] Failed to update timeout message: {e}")

# --- 4. UI HANDLERS ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_data = get_user_data(user.id)
    
    now = datetime.now().strftime("%A, %d %B %Y %H:%M:%S")
    sold = get_total_sold()
    total_users = get_total_users()
    
    raw_welcome = get_config("welcome")


async def cmd_forceconfirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin command: force delivery for testing.
    Usage: /forceconfirm <pid> <vid> <qty>
    """
    try:
        user_id = update.effective_user.id
        if user_id != ADMIN_ID:
            await update.message.reply_text("You are not authorized to use this command.")
            return

        args = context.args
        if len(args) < 3:
            await update.message.reply_text("Usage: /forceconfirm <pid> <vid> <qty>")
            return

        pid = args[0]
        vid = args[1]
        try:
            qty = int(args[2])
        except:
            await update.message.reply_text("Quantity must be a number")
            return

        products = load_products()
        if pid not in products:
            await update.message.reply_text(f"Product {pid} not found")
            return

        prod = products[pid]
        var = prod.get('variants', {}).get(vid)
        if not var:
            await update.message.reply_text(f"Variant {vid} not found for product {pid}")
            return

        stock = get_stock_count(pid, vid)
        if stock < qty:
            await update.message.reply_text(f"Not enough stock: have {stock}, need {qty}")
            return

        # Pull accounts and deliver
        accounts = get_accounts(pid, vid, qty)
        if not accounts:
            await update.message.reply_text("No accounts available to deliver")
            return

        # Update spending and product sold
        chat_id = update.effective_chat.id
        total = var.get('price', 0) * qty
        update_user_spent(chat_id, total, update.effective_user.username)
        products[pid]['sold'] = products[pid].get('sold', 0) + qty
        save_products(products)

        # Build message identical to normal delivery
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

        trx_id = generate_trx_id()
        text = (
            "[OK] PAYMENT CONFIRMED (FORCED)\n"
            "This confirmation was forced by admin for testing.\n\n"
            "Order Details:\n"
            "= = = = = = = = = = = = = = = = = = = = = =\n"
            f"Product: {prod.get('name')}\n"
            f"Variant: {var.get('name')}\n"
            f"Quantity: x{qty}\n"
            f"Total: ${total:.2f}\n"
            "= = = = = = = = = = = = = = = = = = = = = =\n"
            f"{acc_text}\n"
            f"Transaction ID: `{trx_id}`"
        )

        await update.message.reply_text("Forced delivery complete. Sending confirmation...")
        await context.bot.send_message(chat_id, text, parse_mode='Markdown', disable_web_page_preview=True)
        logging.info(f"[FORCECONFIRM] Delivered {qty} items for product {pid} variant {vid} to chat {chat_id}")
    except Exception as e:
        logging.error(f"[FORCECONFIRM] Error: {e}")
        try:
            await update.message.reply_text(f"Error forcing confirm: {e}")
        except:
            pass

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_data = get_user_data(user.id)
    
    now = datetime.now().strftime("%A, %d %B %Y %H:%M:%S")
    sold = get_total_sold()
    total_users = get_total_users()
    
    raw_welcome = get_config("welcome")
    
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
    
    banner = get_config("banner_welcome")
    if banner:
        try: await update.message.reply_photo(banner, caption=welcome_text, reply_markup=markup, parse_mode='Markdown')
        except: await update.message.reply_text(welcome_text, reply_markup=markup, parse_mode='Markdown')
    else:
        await update.message.reply_text(welcome_text, reply_markup=markup, parse_mode='Markdown')

async def show_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    products = load_products()
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
    
    banner = get_config("banner_products")
    if banner:
        try: await update.message.reply_photo(banner, caption=list_text, reply_markup=markup, parse_mode='Markdown')
        except: await update.message.reply_text(list_text, reply_markup=markup, parse_mode='Markdown')
    else: await update.message.reply_text(list_text, reply_markup=markup, parse_mode='Markdown')

async def show_stock_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    products = load_products()
    msg = "**PRODUCT STOCK REPORT**\n╭ - - - - - - - - - - - - - - - - - - - - - ╮\n"
    has = False
    for pid in sorted(products.keys(), key=lambda x: int(x)):
        p = products[pid]
        for vid, v in p['variants'].items():
            count = get_stock_count(pid, vid); icon = "✅" if count > 0 else "❌"
            msg += f"┊ {icon} {p['name']} {v['name']} : {count}x\n"; has = True
    if not has: msg += "┊ No products.\n"
    msg += "╰ - - - - - - - - - - - - - - - - - - - - - ╯"
    await update.message.reply_text(msg, parse_mode='Markdown')

async def show_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"For assistance, please contact admin: {ADMIN_USERNAME}")

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer() 
    callback_data = query.data
    logging.info(f"Button clicked: {callback_data}")
    
    if callback_data.startswith("stock"): 
        logging.info("Stock action detected, returning")
        return 

    products = load_products()
    
    # Parse the callback data
    if callback_data == "back_list":
        action = "back_list"
        data = []
    else:
        data = callback_data.split("_")
        action = data[0]
    
    logging.info(f"Action: {action}, Data: {data}")

    if action == "view":
        pid = data[1]
        if pid not in products: return
        prod = products[pid]
        text = f"╭ - - - - - - - - - - - - - - - - - - - ╮\n┊ • **Product:** {prod['name']}\n┊ • **Sold:** {prod['sold']} pcs\n┊ • **Desc:** {prod['desc']}\n╰ - - - - - - - - - - - - - - - - - - - ╯\n╭ - - - - - - - - - - - - - - - - - - - ╮\n┊ **Select Variation:**\n"
        keyboard = []
        if query.from_user.id == ADMIN_ID:
             keyboard.append([InlineKeyboardButton("🗑 DELETE PRODUCT", callback_data=f"delprod_{pid}")])
        for vid, var in prod['variants'].items():
            stock = get_stock_count(pid, vid)
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
    elif action == "tutorial":
        # Admin interactive: set tutorial link for a specific product variant
        if query.from_user.id != ADMIN_ID: return
        if len(data) < 3: return
        pid = data[1]
        vid = data[2]
        context.user_data['tutorial_pid'] = pid
        context.user_data['tutorial_vid'] = vid
        try:
            await query.message.reply_text(f"Send the tutorial link (URL) for product {pid} variant {vid} now.")
        except:
            pass

    elif action == "back_list":
        products = load_products()
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
        prod = products[pid]; var = prod['variants'][vid]; stock = get_stock_count(pid, vid)
        
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
        if get_stock_count(pid, vid) < qty:
            await query.message.reply_text("❌ **Sold Out!** Please check back later.", parse_mode='Markdown'); return
        
        await query.message.reply_text(f"⏳ Generating Bakong KHQR code...")
        qr_text, md5 = generate_qr_data(total)
        
        # Check if QR generation failed
        if not qr_text or not md5:
            error_msg = (
                "❌ **Payment System Error**\n\n"
                "Unable to generate KHQR payment code.\n"
                "This usually means:\n"
                "• BAKONG_TOKEN is not configured\n"
                "• BAKONG_PROXY_URL is not working\n\n"
                f"Please contact admin: {ADMIN_USERNAME}"
            )
            await query.message.reply_text(error_msg, parse_mode='Markdown')
            
            # Notify admin
            try:
                await context.bot.send_message(
                    ADMIN_ID, 
                    f"⚠️ KHQR Generation Failed!\n"
                    f"User: {query.from_user.id}\n"
                    f"Product: {prod['name']}\n"
                    f"Amount: ${total}\n\n"
                    f"Check BAKONG_TOKEN or BAKONG_PROXY_URL configuration!"
                )
            except:
                pass
            return
        
        filename = create_styled_qr(qr_text, total)
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel Transaction", callback_data="cancel")]])
        
        caption = (
            f"💳 **BAKONG KHQR PAYMENT**\n"
            f"Amount: **${total:.2f}**\n"
            f"Product: {prod['name']} x{qty}\n\n"
            f"🇰🇭 Scan with any Bakong app:\n"
            f"• ABA Mobile\n"
            f"• Wing Money\n"
            f"• TrueMoney\n"
            f"• Pi Pay\n"
            f"• Any bank app with Bakong\n\n"
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
        delete_product_files(pid); del products[pid]; reindex_products()
        await query.message.delete(); await context.bot.send_message(query.message.chat_id, f"🗑 Product {pid} Deleted."); await show_products(update, context)

    elif action == "delvar":
        pid, vid = data[1], data[2]
        if query.from_user.id != ADMIN_ID: return
        if pid in products and vid in products[pid]['variants']:
            clear_stock(pid, vid); del products[pid]['variants'][vid]; save_products(products)
            await context.bot.send_message(query.message.chat_id, f"🗑 Variant {vid} Deleted."); await show_products(update, context)

# --- 5. ADMIN LOGIC ---

async def start_add_stock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return ConversationHandler.END
    products = load_products()
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
    products = load_products(); prod = products[pid]
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
    pid = context.user_data['stock_pid']
    await query.message.edit_text(f"📥 Send data for this variant now.\nFormat: `email,pass,info`\n(Send multiple lines to add multiple)", parse_mode='Markdown')
    return INPUT_STOCK

async def receive_stock_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pid = context.user_data.get('stock_pid')
    vid = context.user_data.get('stock_vid')
    text = update.message.text
    lines = text.split('\n'); count = 0
    for line in lines:
        if line.strip(): add_stock(pid, vid, line.strip()); count += 1
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
        
        # Validate inputs
        if not name or not var_name or not price_str:
            await update.message.reply_text("❌ All fields are required and cannot be empty.", parse_mode='Markdown')
            return
        
        try:
            price = float(price_str)
            if price < 0:
                await update.message.reply_text("❌ Price cannot be negative.", parse_mode='Markdown')
                return
        except ValueError:
            await update.message.reply_text("❌ Price must be a valid number.", parse_mode='Markdown')
            return
        
        products = load_products()
        pid = next((k for k, v in products.items() if v['name'].lower() == name.lower()), None)
        if not pid:
            pid = str(max([int(k) for k in products.keys()] or [0]) + 1)
            products[pid] = {"name": name, "desc": desc, "sold": 0, "variants": {}}
        vid = var_name.replace(" ", "").upper()[:3]
        products[pid]['variants'][vid] = {"name": var_name, "price": price}
        save_products(products)
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
    users = get_all_users()
    
    if not users:
        await update.message.reply_text("ℹ️ No users to broadcast to.")
        return
    
    await update.message.reply_text(f"📢 Sending to {len(users)} users...")
    success = 0
    failed = 0
    
    for uid in users:
        try:
            await context.bot.send_message(uid, f"📢 **NOTICE:**\n{msg}", parse_mode='Markdown')
            success += 1
        except Exception as e:
            logging.warning(f"Failed to send message to {uid}: {e}")
            failed += 1
    
    await update.message.reply_text(f"✅ Done. Sent: {success}, Failed: {failed}")

async def cmd_tutorial(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Start interactive tutorial link setup for a product
    if update.effective_user.id != ADMIN_ID: return
    await update.message.reply_text("Enter product id:")
    context.user_data['await_tutorial_pid'] = True

async def cmd_set_banner_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    try:
        if not context.args:
            await update.message.reply_text("⚠️ Usage: `/setbanner_welcome <image_url>`", parse_mode='Markdown')
            return
        update_config("banner_welcome", context.args[0])
        await update.message.reply_text("✅ Welcome Banner Updated!")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def cmd_set_banner_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    try:
        if not context.args:
            await update.message.reply_text("⚠️ Usage: `/setbanner_products <image_url>`", parse_mode='Markdown')
            return
        update_config("banner_products", context.args[0])
        await update.message.reply_text("✅ Products Banner Updated!")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def cmd_admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    await update.message.reply_text(
        "🛠 **ADMIN MENU**\n\n"
        "`/addpd Name | Var | Price | Desc`\n"
        "`/addstock` (Interactive)\n"
        "`/setbanner_welcome URL`\n"
        "`/setbanner_products URL`\n"
        "`/broadcast Msg`\n"
        "`/testkhqr` - Test KHQR generation\n"
        "`/forceconfirm <pid> <vid> <qty>` - Force delivery", 
        parse_mode='Markdown'
    )

async def cmd_test_khqr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Test KHQR generation to verify configuration"""
    if update.effective_user.id != ADMIN_ID: return
    
    await update.message.reply_text("🧪 Testing KHQR generation...")
    
    # Test with $0.01
    test_amount = 0.01
    qr_text, md5 = generate_qr_data(test_amount)
    
    if not qr_text or not md5:
        error_msg = (
            "❌ **KHQR Test FAILED**\n\n"
            "**Configuration Issues:**\n"
        )
        
        if not BAKONG_TOKEN and not BAKONG_PROXY_URL:
            error_msg += "• No BAKONG_TOKEN set\n• No BAKONG_PROXY_URL set\n"
        elif BAKONG_TOKEN and not khqr:
            error_msg += "• BAKONG_TOKEN is set but KHQR failed to initialize\n"
        elif BAKONG_PROXY_URL:
            error_msg += f"• BAKONG_PROXY_URL is set but not responding: {BAKONG_PROXY_URL}\n"
        
        error_msg += "\n**Required:**\n"
        error_msg += "Set either:\n"
        error_msg += "1. `BAKONG_TOKEN` (requires Cambodia IP)\n"
        error_msg += "2. `BAKONG_PROXY_URL` (for non-Cambodia deployment)"
        
        await update.message.reply_text(error_msg, parse_mode='Markdown')
        return
    
    # Success - generate QR image
    filename = create_styled_qr(qr_text, test_amount)
    
    success_msg = (
        "✅ **KHQR Test SUCCESSFUL**\n\n"
        f"**Configuration:**\n"
        f"• Account: `{BAKONG_ACCOUNT}`\n"
        f"• Merchant: `{MERCHANT_NAME}`\n"
        f"• Amount: ${test_amount}\n"
        f"• MD5: `{md5[:16]}...`\n\n"
        f"**Mode:** {'Proxy' if BAKONG_PROXY_URL else 'Direct'}\n\n"
        "Try scanning this test QR with your banking app!"
    )
    
    await update.message.reply_photo(
        photo=open(filename, 'rb'),
        caption=success_msg,
        parse_mode='Markdown'
    )
    
    # Cleanup
    try:
        os.remove(filename)
    except:
        pass

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    # Admin flow: awaiting product id for tutorial setup
    if update.effective_user.id == ADMIN_ID and context.user_data.get('await_tutorial_pid'):
        pid = text.strip()
        products = load_products()
        if pid not in products:
            await update.message.reply_text("❌ Invalid product id. Try again.")
            return
        keyboard = []
        for vid in products[pid].get('variants', {}).keys():
            keyboard.append([InlineKeyboardButton(f"{products[pid]['variants'][vid]['name']}", callback_data=f"tutorial_{pid}_{vid}")])
        keyboard.append([InlineKeyboardButton("❌ Cancel", callback_data="tutorial_cancel")])
        await update.message.reply_text(f"Select variant for product {pid}:", reply_markup=InlineKeyboardMarkup(keyboard))
        context.user_data.pop('await_tutorial_pid', None)
        return

    # Admin flow: awaiting tutorial link for selected variant
    if update.effective_user.id == ADMIN_ID and context.user_data.get('tutorial_pid'):
        link = text.strip()
        pid = context.user_data.pop('tutorial_pid', None)
        vid = context.user_data.pop('tutorial_vid', None)
        products = load_products()
        if not pid or pid not in products or vid not in products[pid].get('variants', {}):
            await update.message.reply_text("❌ Product or variant not found.")
            return
        products[pid]['variants'][vid]['tutorial'] = link
        save_products(products)
        await update.message.reply_text(f"✅ Tutorial link saved for product {pid} variant {vid}.")
        return

    # Regular user actions
    if text == "🛍 List Products": await show_products(update, context)
    elif text == "👤 My Profile": await start(update, context)
    elif text == "🛠 Admin Panel": await cmd_admin_menu(update, context)
    elif text == "❓ Help": await show_help(update, context)
    elif text == "📦 Check Stock": await show_stock_report(update, context)

if __name__ == '__main__':
    # Validate KHQR configuration at startup
    print("\n" + "="*60)
    if BAKONG_PROXY_URL:
        print("✅ KHQR PROXY MODE ENABLED")
        print(f"   Proxy URL: {BAKONG_PROXY_URL}")
        print("   This bypasses Bakong IP restrictions")
    elif khqr:
        print("⚠️  KHQR DIRECT MODE (Cambodia IP Required)")
        print("   WARNING: Bakong API only works from Cambodia IPs")
        print("   If deployed outside Cambodia, payments will FAIL!")
        print("   Solution: Set BAKONG_PROXY_URL to a Cambodia-hosted proxy")
    else:
        print("❌ KHQR NOT CONFIGURED!")
        print("   Payment verification will NOT work.")
        print("   Options:")
        print("   1. Set BAKONG_TOKEN (requires Cambodia IP)")
        print("   2. Set BAKONG_PROXY_URL (for non-Cambodia deployments)")
    print("="*60 + "\n")
    
    load_products()
    
    # Build application with proper error handling
    async def error_handler(update, context):
        """Handle errors in the application."""
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
    application.add_handler(CommandHandler('tutorial', cmd_tutorial))
    application.add_handler(CommandHandler('stock', show_stock_report))
    application.add_handler(CommandHandler('help', show_help))
    application.add_handler(CommandHandler('forceconfirm', cmd_forceconfirm))
    application.add_handler(CommandHandler('testkhqr', cmd_test_khqr))
    application.add_handler(CallbackQueryHandler(button_click))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("[OK] Store Bot Final V33 Running...")
    application.run_polling()