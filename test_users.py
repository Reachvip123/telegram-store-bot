"""
Test Script - Verify User Registration Fixes
Run this after starting the bot to verify all fixes are working
"""

import json
import os

DB_FOLDER = "database"
USERS_FILE = f"{DB_FOLDER}/users.json"

def check_users():
    """Check if users.json exists and show content"""
    print("="*60)
    print("USER DATABASE CHECK")
    print("="*60)
    
    if not os.path.exists(USERS_FILE):
        print("❌ No users.json file found!")
        print(f"Expected location: {USERS_FILE}")
        return False
    
    try:
        with open(USERS_FILE, 'r') as f:
            users = json.load(f)
        
        print(f"✅ Found {len(users)} users in database\n")
        
        if len(users) == 0:
            print("⚠️  Database is empty - no users registered yet")
            print("\nTo test, have a user:")
            print("1. Click /start")
            print("2. OR click 'List Products'")
            print("3. OR click any button")
            return True
        
        print("USER LIST:")
        print("-"*60)
        
        for user_id, data in users.items():
            username = data.get('username', 'Unknown')
            spent = data.get('spent', 0)
            joined = data.get('joined', 'N/A')[:19]
            
            print(f"\nUser ID: {user_id}")
            print(f"  Username: @{username}")
            print(f"  Spent: ${spent:.2f}")
            print(f"  Joined: {joined}")
        
        print("\n" + "="*60)
        
        # Check for "Unknown" usernames
        unknown_count = sum(1 for u in users.values() if u.get('username') == 'Unknown')
        if unknown_count > 0:
            print(f"⚠️  Found {unknown_count} users with 'Unknown' username")
            print("   These users may not have a Telegram username set")
        else:
            print("✅ All users have proper usernames!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading users file: {e}")
        return False

def test_checklist():
    """Print test checklist"""
    print("\n" + "="*60)
    print("TESTING CHECKLIST")
    print("="*60)
    print("""
Test these scenarios with a test account:

1. ✅ New user clicks /start
   - Should auto-register with username
   - Check with: /viewusers

2. ✅ New user clicks 'List Products' WITHOUT /start
   - Should still register the user
   - Username should be saved

3. ✅ User without Telegram username
   - Should get username like "user_123456789"
   - Should not show "Unknown"

4. ✅ Make a test purchase
   - Username should be recorded
   - Spending should be tracked

5. ✅ Admin checks users
   - /viewusers should list all users
   - No "Unknown" usernames

6. ✅ Existing users
   - Should continue working normally
   - Old data should be preserved
    """)

if __name__ == "__main__":
    print("\n🔍 TESTING BOT USER REGISTRATION FIXES\n")
    
    if check_users():
        test_checklist()
    
    print("\n✅ Verification complete!")
    print("Run this script again after users interact with the bot.\n")
