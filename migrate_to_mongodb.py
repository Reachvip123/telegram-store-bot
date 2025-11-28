#!/usr/bin/env python3
"""
Migration script to transfer data from JSON files to MongoDB Atlas
Run this script ONCE after setting up MongoDB to migrate your existing data
"""

import os
import json
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "")

if not MONGODB_URI:
    print("❌ ERROR: MONGODB_URI not found in .env file!")
    print("Please add your MongoDB connection string to .env")
    exit(1)

# Database configuration
DB_FOLDER = "database"
PRODUCTS_FILE = f"{DB_FOLDER}/products.json"
USERS_FILE = f"{DB_FOLDER}/users.json"
CONFIG_FILE = f"{DB_FOLDER}/config.json"

# Connect to MongoDB
print("🔌 Connecting to MongoDB Atlas...")
try:
    client = MongoClient(MONGODB_URI)
    # Test connection
    client.admin.command('ping')
    print("✅ Connected to MongoDB successfully!")
except Exception as e:
    print(f"❌ Failed to connect to MongoDB: {e}")
    exit(1)

# Get database and collections
db = client['telegram_store_bot']
products_coll = db['products']
users_coll = db['users']
config_coll = db['config']
stock_coll = db['stock']

# Statistics
stats = {
    'products': 0,
    'variants': 0,
    'users': 0,
    'config': 0,
    'stock_items': 0
}

print("\n" + "="*60)
print("📦 Starting Data Migration")
print("="*60)

# 1. Migrate Products
print("\n1️⃣ Migrating products...")
if os.path.exists(PRODUCTS_FILE):
    with open(PRODUCTS_FILE, 'r') as f:
        products = json.load(f)
    
    for pid, product in products.items():
        # Insert product to MongoDB
        product_doc = {
            '_id': int(pid),
            'name': product.get('name', ''),
            'desc': product.get('desc', ''),
            'sold': product.get('sold', 0),
            'variants': product.get('variants', {}),
            'migrated_at': datetime.now()
        }
        
        products_coll.update_one(
            {'_id': int(pid)},
            {'$set': product_doc},
            upsert=True
        )
        stats['products'] += 1
        stats['variants'] += len(product.get('variants', {}))
        
        print(f"   ✅ Migrated product {pid}: {product.get('name')}")
        
        # 2. Migrate Stock Files for each variant
        for vid in product.get('variants', {}).keys():
            # Find stock file
            stock_file = f"{DB_FOLDER}/stock_{pid}_{vid}.txt"
            if os.path.exists(stock_file):
                with open(stock_file, 'r') as f:
                    lines = f.readlines()
                
                for line in lines:
                    content = line.strip()
                    if content:
                        stock_doc = {
                            'product_id': int(pid),
                            'variant_id': vid,
                            'content': content,
                            'sold': False,
                            'added_at': datetime.now()
                        }
                        stock_coll.insert_one(stock_doc)
                        stats['stock_items'] += 1
                
                print(f"      📦 Migrated {len(lines)} stock items for variant {vid}")
    
    print(f"✅ Migrated {stats['products']} products with {stats['variants']} variants")
else:
    print("⚠️  No products.json found - skipping product migration")

# 3. Migrate Users
print("\n2️⃣ Migrating users...")
if os.path.exists(USERS_FILE):
    with open(USERS_FILE, 'r') as f:
        users = json.load(f)
    
    for user_id, user_data in users.items():
        user_doc = {
            'user_id': int(user_id),
            'username': user_data.get('username', 'Unknown'),
            'spent': user_data.get('spent', 0.0),
            'joined': user_data.get('joined', str(datetime.now())),
            'purchases': [],
            'migrated_at': datetime.now()
        }
        
        users_coll.update_one(
            {'user_id': int(user_id)},
            {'$set': user_doc},
            upsert=True
        )
        stats['users'] += 1
    
    print(f"✅ Migrated {stats['users']} users")
else:
    print("⚠️  No users.json found - skipping user migration")

# 4. Migrate Config
print("\n3️⃣ Migrating configuration...")
if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
    
    for key, value in config.items():
        config_doc = {
            'key': key,
            'value': value,
            'updated_at': datetime.now()
        }
        
        config_coll.update_one(
            {'key': key},
            {'$set': config_doc},
            upsert=True
        )
        stats['config'] += 1
        print(f"   ✅ Migrated config: {key}")
    
    print(f"✅ Migrated {stats['config']} config items")
else:
    print("⚠️  No config.json found - skipping config migration")

# Summary
print("\n" + "="*60)
print("📊 Migration Summary")
print("="*60)
print(f"Products:      {stats['products']}")
print(f"Variants:      {stats['variants']}")
print(f"Stock Items:   {stats['stock_items']}")
print(f"Users:         {stats['users']}")
print(f"Config Items:  {stats['config']}")
print("="*60)

# Verification
print("\n🔍 Verifying migration...")
db_products = products_coll.count_documents({})
db_users = users_coll.count_documents({})
db_stock = stock_coll.count_documents({})

print(f"MongoDB Products: {db_products}")
print(f"MongoDB Users: {db_users}")
print(f"MongoDB Stock: {db_stock}")

print("\n✅ Migration complete!")
print("\n📌 Next Steps:")
print("1. Verify your data in MongoDB Atlas web interface")
print("2. Update your .env file to use the new MongoDB bot:")
print("3. On VPS, replace storebot.py with storebot_mongodb.py")
print("4. Install new requirements: pip install -r requirements.txt")
print("5. Restart the bot service")
print("\n⚠️  Keep your JSON files as backup until you confirm everything works!")

client.close()
