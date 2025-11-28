# 🐘 PostgreSQL Setup Guide

Your bot now supports PostgreSQL database! Much better than JSON files for production use.

---

## 📋 Step 1: Install PostgreSQL on VPS

### **In Termius (connected to your VPS):**

```bash
# Update system
sudo apt update

# Install PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Start PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

---

## 🔧 Step 2: Create Database and User

```bash
# Switch to postgres user
sudo -u postgres psql

# Inside PostgreSQL console, run these commands:
```

```sql
-- Create database
CREATE DATABASE telegram_store_bot;

-- Create user with password
CREATE USER botuser WITH PASSWORD 'your_strong_password_here';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE telegram_store_bot TO botuser;

-- Exit
\q
```

---

## 📝 Step 3: Update Bot Configuration

### **Edit .env file on VPS:**

```bash
cd /root/telegram-store-bot
nano .env
```

### **Add/Update these lines:**

```env
# Enable PostgreSQL
USE_POSTGRESQL=true

# PostgreSQL connection string
POSTGRESQL_URI=postgresql://botuser:your_strong_password_here@localhost:5432/telegram_store_bot

# Disable other databases
USE_MONGODB=false
```

**Save:** `Ctrl+X`, `Y`, `Enter`

---

## 🔄 Step 4: Update Bot and Install Dependencies

```bash
cd /root/telegram-store-bot

# Pull latest code
git pull origin main

# Activate virtual environment
source venv/bin/activate

# Install PostgreSQL library
pip install psycopg2-binary

# Restart bot
systemctl restart storebot

# Check logs
journalctl -u storebot -f
```

You should see: **[OK] Connected to PostgreSQL** ✅

---

## ✨ Benefits of PostgreSQL:

- ✅ **Much faster** than JSON files
- ✅ **Scalable** - handles thousands of products
- ✅ **Reliable** - ACID transactions
- ✅ **Concurrent** - multiple operations at once
- ✅ **Searchable** - fast queries
- ✅ **Backup-friendly** - proper database dumps

---

## 🔍 Database Structure:

### **Tables Created Automatically:**

1. **products** - Product catalog (id, name, description, sold)
2. **variants** - Product variants (product_id, variant_id, name, price, tutorial)
3. **stock** - Account inventory (id, product_id, variant_id, account_data, created_at)
4. **users** - Customer database (user_id, username, spent, joined_at)
5. **config** - Bot configuration (key, value)

---

## 📊 Useful PostgreSQL Commands:

### **Connect to database:**
```bash
sudo -u postgres psql telegram_store_bot
```

### **View all products:**
```sql
SELECT * FROM products;
```

### **View stock count:**
```sql
SELECT product_id, variant_id, COUNT(*) 
FROM stock 
GROUP BY product_id, variant_id;
```

### **View total revenue:**
```sql
SELECT SUM(spent) FROM users;
```

### **View top customers:**
```sql
SELECT username, spent 
FROM users 
ORDER BY spent DESC 
LIMIT 10;
```

### **Exit:**
```sql
\q
```

---

## 💾 Backup Database:

### **Create backup:**
```bash
sudo -u postgres pg_dump telegram_store_bot > backup_$(date +%Y%m%d).sql
```

### **Restore backup:**
```bash
sudo -u postgres psql telegram_store_bot < backup_20251128.sql
```

---

## 🔄 Migrate from JSON to PostgreSQL:

If you have existing data in JSON files, the bot will create empty tables in PostgreSQL.

You can:
1. Start fresh (recommended)
2. Manually re-add products via `/addpd`
3. Manually re-add stock via `/addstock`

Your old JSON files will remain in `database/` folder as backup.

---

## ⚙️ PostgreSQL Configuration (Optional):

### **Allow remote connections (if needed):**

```bash
sudo nano /etc/postgresql/*/main/postgresql.conf
```

Find and change:
```
listen_addresses = 'localhost'
```
to:
```
listen_addresses = '*'
```

Then edit pg_hba.conf:
```bash
sudo nano /etc/postgresql/*/main/pg_hba.conf
```

Add:
```
host    all             all             0.0.0.0/0               md5
```

Restart:
```bash
sudo systemctl restart postgresql
```

---

## 🎯 Connection String Format:

```
postgresql://username:password@host:port/database
```

**Examples:**

**Local:**
```
postgresql://botuser:mypass123@localhost:5432/telegram_store_bot
```

**Remote:**
```
postgresql://botuser:mypass123@157.10.73.90:5432/telegram_store_bot
```

**Cloud (Supabase, Neon, etc):**
```
postgresql://user:pass@db.xxxxx.supabase.co:5432/postgres
```

---

## 🆓 Free PostgreSQL Hosting (Alternative):

If you don't want to run PostgreSQL on your VPS:

1. **Supabase** - https://supabase.com (Free 500MB)
2. **Neon** - https://neon.tech (Free 10GB)
3. **ElephantSQL** - https://www.elephantsql.com (Free 20MB)
4. **Railway** - https://railway.app (Free with limits)

Just use their connection string in your `.env` file!

---

## ✅ Verify Installation:

After setup, test in Telegram:

```
/viewstock
/viewproducts
/viewusers
```

If these work, PostgreSQL is running perfectly! 🎉

---

## 🔒 Security Tips:

1. Use a strong password for `botuser`
2. Don't expose PostgreSQL port (5432) to internet unless needed
3. Regular backups with `pg_dump`
4. Keep PostgreSQL updated: `sudo apt upgrade postgresql`

---

## 🐛 Troubleshooting:

**Bot shows "[FALLBACK] Using local file storage":**
- Check `.env` has `USE_POSTGRESQL=true`
- Verify connection string is correct
- Check PostgreSQL is running: `systemctl status postgresql`
- Check credentials: `sudo -u postgres psql`

**"Connection refused":**
- PostgreSQL not running: `sudo systemctl start postgresql`
- Wrong host/port in connection string
- Firewall blocking connection

**"Authentication failed":**
- Wrong username or password
- User doesn't have permissions
- Database doesn't exist

---

Your bot is now ready for PostgreSQL! 🚀
