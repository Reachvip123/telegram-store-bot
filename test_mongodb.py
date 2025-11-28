#!/usr/bin/env python3
"""
Quick MongoDB Test & Sample Data Creator
Run this to check MongoDB connection and add sample data
"""

import pymongo
from datetime import datetime

# MongoDB connection
MONGODB_URI = "mongodb+srv://dztsorebase:reachvip@cluster0.tbyhuzf.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DATABASE_NAME = "telegram_store_bot"

print("="*60)
print("🔍 Testing MongoDB Connection...")
print("="*60)

try:
    # Connect to MongoDB
    client = pymongo.MongoClient(MONGODB_URI)
    db = client[DATABASE_NAME]
    
    # Test connection
    client.admin.command('ping')
    print("✅ Connected to MongoDB successfully!\n")
    
    # Check existing data
    print("📊 Current Database Status:")
    print(f"  Products: {db.products.count_documents({})}")
    print(f"  Users: {db.users.count_documents({})}")
    print(f"  Stock: {db.stock.count_documents({})}")
    print(f"  Orders: {db.orders.count_documents({})}")
    print()
    
    # Ask to add sample data
    add_sample = input("❓ Want to add sample product? (yes/no): ").lower()
    
    if add_sample == 'yes':
        # Add sample product
        sample_product = {
            'name': 'CAPCUT PRO',
            'desc': 'Premium Video Editor with AI Features',
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
        print(f"\n✅ Added sample product! ID: {product_id}")
        
        # Add sample stock
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
            }
        ]
        
        db.stock.insert_many(sample_stock)
        print(f"✅ Added {len(sample_stock)} stock items!")
        
        # Add sample user
        sample_user = {
            'user_id': 123456789,
            'username': 'SampleUser',
            'spent': 0.0,
            'joined_at': datetime.now(),
            'purchases': []
        }
        
        db.users.insert_one(sample_user)
        print("✅ Added sample user!")
        
        print("\n" + "="*60)
        print("🎉 Sample data added successfully!")
        print("="*60)
        print("\n📱 Now check your MongoDB:")
        print("  1. MongoDB Atlas: https://cloud.mongodb.com")
        print("  2. Or run web admin: python simple_vps_admin.py")
        print("  3. Or use Telegram bot: /start")
        print()
    else:
        print("\n📋 Database checked. No changes made.")
    
    # Show all products
    print("\n📦 Current Products:")
    products = list(db.products.find({}))
    if products:
        for p in products:
            print(f"  - {p.get('name', 'Unknown')} (ID: {p['_id']})")
            for vid, variant in p.get('variants', {}).items():
                stock_count = db.stock.count_documents({
                    'product_id': str(p['_id']),
                    'variant_id': vid,
                    'sold': False
                })
                print(f"    • {variant['name']}: ${variant['price']} ({stock_count} in stock)")
    else:
        print("  (No products yet)")
    
    print("\n" + "="*60)
    print("✅ MongoDB is working perfectly!")
    print("="*60)
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nTroubleshooting:")
    print("  1. Check your internet connection")
    print("  2. Verify MongoDB Atlas credentials")
    print("  3. Make sure MongoDB Atlas IP whitelist allows your IP")

print()
