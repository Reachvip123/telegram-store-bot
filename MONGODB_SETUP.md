# MongoDB Atlas Setup Guide

## Why MongoDB Atlas?

MongoDB Atlas is a cloud-based database service that offers:
- **Free Tier**: Up to 512MB storage (perfect for your store bot)
- **Web UI**: Browse, edit, and manage data through their website
- **Global Access**: Access from anywhere, not just Cambodia
- **Automatic Backups**: Data protection included
- **Better Performance**: Query optimization and indexing
- **Scalability**: Easy to upgrade as your business grows

---

## Step 1: Create MongoDB Atlas Account

1. Go to https://www.mongodb.com/cloud/atlas/register
2. Sign up with your email or Google account
3. Choose the **FREE tier** (M0 Sandbox)
4. Select a cloud provider: **AWS**
5. Select region: **Singapore (ap-southeast-1)** (closest to Cambodia for best speed)
6. Cluster Name: `telegram-store-bot` (or any name you like)
7. Click **Create Cluster** (takes 3-5 minutes)

---

## Step 2: Configure Database Access

### Create Database User:
1. In Atlas Dashboard, click **Database Access** (left sidebar)
2. Click **Add New Database User**
3. Authentication Method: **Password**
4. Username: `botadmin` (or your choice)
5. Password: Click **Autogenerate Secure Password** and **COPY IT**
   - Save this password securely!
6. Database User Privileges: **Read and write to any database**
7. Click **Add User**

---

## Step 3: Configure Network Access

### Allow VPS IP Address:
1. Click **Network Access** (left sidebar)
2. Click **Add IP Address**
3. Add your VPS IP: `157.10.73.90/32`
4. Description: `Cambodia VPS`
5. Click **Confirm**

### (Optional) Add Your Computer for Testing:
1. Click **Add IP Address** again
2. Click **Add Current IP Address**
3. Description: `My Computer`
4. Click **Confirm**

---

## Step 4: Get Connection String

1. Click **Database** (left sidebar)
2. Click **Connect** on your cluster
3. Choose **Drivers**
4. Select Driver: **Python**, Version: **3.12 or later**
5. Copy the connection string, it looks like:
   ```
   mongodb+srv://botadmin:<password>@telegram-store-bot.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```
6. **Replace `<password>`** with the password you copied earlier
7. Save this complete connection string - you'll need it!

**Example:**
```
mongodb+srv://botadmin:MySecurePass123@telegram-store-bot.abc123.mongodb.net/?retryWrites=true&w=majority
```

---

## Step 5: Explore MongoDB Atlas Web UI

### Collections View:
1. Click **Database** → **Browse Collections**
2. After your bot runs, you'll see:
   - `products` collection (all your digital products)
   - `users` collection (customer data)
   - `stock` collection (product keys/codes)
   - `orders` collection (purchase history)

### What You Can Do:
- **View Data**: Click any collection to see documents
- **Edit**: Click a document to modify fields
- **Delete**: Remove unwanted entries
- **Search**: Filter and find specific records
- **Export**: Download data as JSON or CSV
- **Charts**: Create visualizations of sales data

---

## Step 6: Add Connection String to .env

On your VPS, edit the `.env` file:

```bash
nano /root/telegram-store-bot/.env
```

Add this line at the bottom:
```
MONGODB_URI=mongodb+srv://botadmin:YourPassword@telegram-store-bot.xxxxx.mongodb.net/?retryWrites=true&w=majority
```

Save and exit (Ctrl+X, Y, Enter)

---

## Benefits for Your Store Bot

### Before (JSON Files):
- Manual file editing via SSH
- Risk of file corruption
- No query capabilities
- Limited to VPS storage

### After (MongoDB Atlas):
- Visual web interface
- Point-and-click editing
- Powerful search queries
- Cloud backup included
- Access from anywhere

---

## Quick Reference Commands

### View database via MongoDB Compass (Desktop App):
1. Download: https://www.mongodb.com/try/download/compass
2. Paste your connection string
3. Connect and browse visually

### Example Queries in Atlas UI:
```javascript
// Find all users who purchased something
{"purchases": {$exists: true}}

// Find products with price > $10
{"price": {$gt: 10}}

// Find out of stock products
{"stock_count": 0}
```

---

## Migration Plan

Once MongoDB is set up:
1. Your existing JSON data will be automatically migrated
2. New purchases will save to MongoDB
3. JSON files will be kept as backup
4. You can delete JSON files after confirming everything works

---

## Next Steps

After completing this setup:
1. Copy your MongoDB connection string
2. Run the migration script (provided separately)
3. Restart your bot on VPS
4. Verify data in Atlas web UI
5. Start managing your store from anywhere!

---

## Support Resources

- MongoDB Atlas Docs: https://docs.atlas.mongodb.com/
- Community Forums: https://www.mongodb.com/community/forums/
- Free Training: https://university.mongodb.com/

---

**Ready to proceed?** Make sure you have:
- ✅ MongoDB Atlas account created
- ✅ Database user created with password saved
- ✅ VPS IP (157.10.73.90) added to Network Access
- ✅ Connection string copied and password replaced
