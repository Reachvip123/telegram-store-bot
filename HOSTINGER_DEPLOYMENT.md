# 🚀 Hostinger MySQL Deployment Guide

## Step 1: Prepare Your Hostinger Account

### 1.1 Create MySQL Database
1. Login to your **Hostinger control panel**
2. Navigate to **"Databases" → "MySQL Databases"**
3. Click **"Create Database"**
4. Set database name: `telegram_store_bot`
5. Set username: `bot_user` (or any name you prefer)
6. Set strong password
7. **IMPORTANT**: Note down these details:
   - Host: (usually `localhost` or your domain)
   - Database: `telegram_store_bot`
   - Username: `bot_user`
   - Password: `your_password`
   - Port: `3306`

### 1.2 Get File Manager Access
1. In Hostinger control panel
2. Go to **"File Manager"** 
3. Navigate to `public_html` folder (this is your web root)

## Step 2: Upload Your Bot Files

### 2.1 Create Project Folder
```bash
# In Hostinger File Manager, create:
public_html/telegram_bot/
```

### 2.2 Upload These Files
Upload to `public_html/telegram_bot/`:
- `storebot_mysql.py` (main bot file)
- `admin_panel_mysql.py` (web admin)
- `requirements_mysql.txt` (dependencies)
- `templates/` folder (with all HTML files)

### 2.3 Create Environment File
1. Copy `.env_hostinger_template` to `.env`
2. Edit `.env` with your Hostinger MySQL details:

```env
# Bot Configuration
BOT_TOKEN=your_telegram_bot_token
ADMIN_ID=your_telegram_user_id

# Hostinger MySQL (from Step 1.1)
MYSQL_HOST=localhost
MYSQL_DATABASE=telegram_store_bot
MYSQL_USER=bot_user
MYSQL_PASSWORD=your_mysql_password
MYSQL_PORT=3306

# Bakong Payment
BAKONG_TOKEN=your_bakong_token
BAKONG_ACCOUNT=your_bank_account

# Admin Panel
ADMIN_PASSWORD=admin123
```

## Step 3: Install Dependencies

### 3.1 SSH Access (if available)
If your Hostinger plan has SSH:
```bash
cd public_html/telegram_bot
python -m pip install -r requirements_mysql.txt
```

### 3.2 Alternative: Python App Setup
1. In Hostinger control panel
2. Go to **"Advanced" → "Python App"**
3. Create new Python app
4. Set app directory to `telegram_bot`
5. Upload requirements file
6. Install dependencies through control panel

## Step 4: Test Database Connection

### 4.1 Create Test Script
Create `test_db.py`:
```python
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

try:
    conn = mysql.connector.connect(
        host=os.getenv('MYSQL_HOST'),
        user=os.getenv('MYSQL_USER'),
        password=os.getenv('MYSQL_PASSWORD'),
        database=os.getenv('MYSQL_DATABASE'),
        port=int(os.getenv('MYSQL_PORT', '3306'))
    )
    print("✅ MySQL connection successful!")
    conn.close()
except Exception as e:
    print(f"❌ MySQL connection failed: {e}")
```

### 4.2 Run Test
```bash
python test_db.py
```

## Step 5: Run Your Bot

### 5.1 Start Bot
```bash
cd public_html/telegram_bot
python storebot_mysql.py
```

### 5.2 Setup Background Process
Create `start_bot.sh`:
```bash
#!/bin/bash
cd /home/your_username/public_html/telegram_bot
nohup python storebot_mysql.py > bot.log 2>&1 &
echo $! > bot.pid
```

Make executable and run:
```bash
chmod +x start_bot.sh
./start_bot.sh
```

## Step 6: Setup Web Admin Panel

### 6.1 Start Admin Panel
```bash
cd public_html/telegram_bot
python admin_panel_mysql.py
```

### 6.2 Setup as Service (if SSH available)
Create systemd service or use screen:
```bash
screen -S admin_panel
python admin_panel_mysql.py
# Press Ctrl+A, then D to detach
```

### 6.3 Access Admin Panel
Visit: `http://your-domain.com:8080`
- Username: admin
- Password: admin123 (or what you set in .env)

## Step 7: Configure Domain (Optional)

### 7.1 Subdomain Setup
1. In Hostinger control panel
2. Go to **"Domains" → "Subdomains"**
3. Create: `admin.yourdomain.com`
4. Point to `telegram_bot` folder

### 7.2 Setup Reverse Proxy
Create `.htaccess` in subdomain folder:
```apache
RewriteEngine On
RewriteRule ^(.*)$ http://localhost:8080/$1 [P,L]
```

## Step 8: Monitoring & Logs

### 8.1 Check Bot Status
```bash
# Check if bot is running
ps aux | grep storebot_mysql.py

# Check logs
tail -f bot.log
```

### 8.2 Database Logs
```bash
# MySQL error logs (location varies)
tail -f /var/log/mysql/error.log
```

## Step 9: Security Setup

### 9.1 Secure Database
1. Use strong MySQL password
2. Limit database user privileges
3. Enable MySQL SSL if available

### 9.2 Secure Admin Panel
1. Change default admin password
2. Use strong Flask secret key
3. Consider IP whitelisting

## Troubleshooting

### Common Issues:

**1. MySQL Connection Refused**
```bash
# Check MySQL service
systemctl status mysql

# Check MySQL user privileges
mysql -u root -p
SHOW GRANTS FOR 'bot_user'@'localhost';
```

**2. Port 8080 Access Issues**
```bash
# Check if port is open
netstat -tlnp | grep 8080

# Open port in firewall
ufw allow 8080
```

**3. Dependencies Missing**
```bash
# Install missing packages
pip install mysql-connector-python
pip install flask
```

**4. Permission Errors**
```bash
# Fix file permissions
chmod 755 *.py
chmod 644 .env
```

## Success Indicators

✅ **Bot Working**: Bot responds to `/start` command
✅ **Database Connected**: Products can be added/viewed  
✅ **Admin Panel**: Accessible at your-domain:8080
✅ **Payments**: KHQR codes generate and verify

## Support

If you encounter issues:
1. Check `bot.log` for error messages
2. Verify all `.env` values are correct
3. Test MySQL connection with `test_db.py`
4. Ensure all dependencies are installed

Your bot is now ready for Hostinger hosting! 🎉