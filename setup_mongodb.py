#!/usr/bin/env python3
"""
Complete MongoDB Setup & Test
This will set up your database with sample data
"""

import pymongo
from datetime import datetime

print("="*60)
print("🚀 MongoDB Setup for Telegram Store Bot")
print("="*60)
print()

# Step 1: Connect to MongoDB
print("Step 1/5: Connecting to MongoDB Atlas...")
MONGODB_URI = "mongodb+srv://dztsorebase:reachvip@cluster0.tbyhuzf.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

try:
    client = pymongo.MongoClient(MONGODB_URI)
    client.admin.command('ping')
    print("✅ Connected successfully!")
except Exception as e:
    print(f"❌ Connection failed: {e}")
    input("\nPress Enter to exit...")
    exit(1)

# Step 2: Select database
print("\nStep 2/5: Setting up database...")
db = client['telegram_store_bot']
print("✅ Database: telegram_store_bot")

# Step 3: Check existing data
print("\nStep 3/5: Checking existing data...")
products_count = db.products.count_documents({})
users_count = db.users.count_documents({})
stock_count = db.stock.count_documents({})

print(f"   Products: {products_count}")
print(f"   Users: {users_count}")
print(f"   Stock items: {stock_count}")

if products_count > 0:
    print("\n⚠️  Database already has data!")
    choice = input("Delete all and start fresh? (yes/no): ").lower()
    if choice == 'yes':
        db.products.delete_many({})
        db.users.delete_many({})
        db.stock.delete_many({})
        db.orders.delete_many({})
        print("✅ Database cleared!")

# Step 4: Add sample product
print("\nStep 4/5: Adding sample product...")

sample_product = {
    'name': 'CAPCUT PRO',
    'desc': 'Premium Video Editor - AI Features, No Watermark, HD Export',
    'sold': 0,
    'variants': {
        '1M': {
            'name': '1 Month',
            'price': 2.99
        },
        '3M': {
            'name': '3 Months', 
            'price': 7.99
        },
        '1Y': {
            'name': '1 Year',
            'price': 19.99
        }
    },
    'created_at': datetime.now()
}

result = db.products.insert_one(sample_product)
product_id = str(result.inserted_id)
print(f"✅ Product added! ID: {product_id}")

# Step 5: Add sample stock
print("\nStep 5/5: Adding sample stock...")

sample_stock = [
    {
        'product_id': product_id,
        'variant_id': '1M',
        'content': 'user1@example.com:password123',
        'sold': False,
        'added_at': datetime.now()
    },
    {
        'product_id': product_id,
        'variant_id': '1M',
        'content': 'user2@example.com:password456',
        'sold': False,
        'added_at': datetime.now()
    },
    {
        'product_id': product_id,
        'variant_id': '3M',
        'content': 'premium1@example.com:pass789',
        'sold': False,
        'added_at': datetime.now()
    },
    {
        'product_id': product_id,
        'variant_id': '1Y',
        'content': 'vip@example.com:vippass',
        'sold': False,
        'added_at': datetime.now()
    }
]

db.stock.insert_many(sample_stock)
print(f"✅ Added {len(sample_stock)} stock items!")

# Add sample user
sample_user = {
    'user_id': 123456789,
    'username': 'TestUser',
    'spent': 0.0,
    'joined_at': datetime.now(),
    'purchases': []
}

db.users.insert_one(sample_user)
print("✅ Added sample user!")

# Summary
print("\n" + "="*60)
print("🎉 Setup Complete!")
print("="*60)
print("\n📊 Database Summary:")
print(f"   Database: telegram_store_bot")
print(f"   Products: {db.products.count_documents({})}")
print(f"   Stock items: {db.stock.count_documents({})}")
print(f"   Users: {db.users.count_documents({})}")

print("\n🔗 View Your Data:")
print("   1. MongoDB Atlas: https://cloud.mongodb.com")
print("      → Browse Collections → telegram_store_bot")
print()
print("   2. Run web admin panel:")
print("      python simple_vps_admin.py")
print("      Then open: http://localhost:5000")
print("      Password: admin123")
print()
print("   3. Use Telegram bot:")
print("      Send /start to your bot")
print()

print("✅ Your MongoDB is ready to use!")
print("="*60)

input("\nPress Enter to exit...")
