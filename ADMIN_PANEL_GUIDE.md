# 🎯 Admin Panel Setup Guide

## 📋 Overview
Professional web-based admin panel to manage your Telegram Store Bot with a beautiful, modern interface.

## ✨ Features

### Dashboard
- 📊 Real-time statistics (products, revenue, users, stock)
- 📈 Quick overview cards with icons
- 🔄 Auto-refresh stats every 30 seconds

### Product Management
- ➕ Add/Edit/Delete products
- 🏷️ Manage product variants
- 💰 Set prices for each variant
- 📚 Add tutorial links
- 👁️ View stock counts

### Stock Management
- 📦 View all stock levels
- ➕ Add bulk stock (paste multiple accounts)
- 🔍 View stock details
- 🗑️ Clear stock
- 🎨 Color-coded status (Green: In Stock, Yellow: Low, Red: Out)

### User Management
- 👥 View all customers
- 💵 See total spent per user
- 📅 Join dates
- 🏆 Sorted by spending

### Settings
- 🔐 Change admin password
- ✉️ Customize welcome message
- ℹ️ System information

## 🚀 Installation on VPS

### 1. Pull latest code
```bash
cd /root/telegram-store-bot
git pull
```

### 2. Install Flask dependencies
```bash
pip install -r requirements-admin.txt
```

### 3. Run the admin panel
```bash
python3 admin_panel.py
```

### 4. Access the panel
Open your browser and go to:
```
http://157.10.73.90:5000
```

**Default credentials:**
- Username: `admin`
- Password: `admin123`

⚠️ **IMPORTANT:** Change the password immediately after first login!

## 🔒 Security Setup

### Change Default Password
1. Login with default credentials
2. Go to **Settings** page
3. Click **Change Password**
4. Enter current password: `admin123`
5. Enter new strong password
6. Confirm and save

### Firewall Configuration (Optional)
To allow external access, open port 5000:
```bash
sudo ufw allow 5000/tcp
sudo ufw reload
```

## 🌐 Running as Background Service

Create systemd service file:
```bash
sudo nano /etc/systemd/system/admin-panel.service
```

Paste this configuration:
```ini
[Unit]
Description=Store Bot Admin Panel
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/telegram-store-bot
ExecStart=/root/telegram-store-bot/venv/bin/python admin_panel.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable admin-panel
sudo systemctl start admin-panel
sudo systemctl status admin-panel
```

View logs:
```bash
journalctl -u admin-panel -f
```

## 📱 Usage Guide

### Adding a Product
1. Go to **Products** page
2. Click **Add Product** button
3. Fill in:
   - Product ID (e.g., `1`, `NETFLIX`)
   - Product Name (e.g., `Netflix Premium`)
   - Description
4. Click **Save Product**

### Adding Variants
1. On the product card, click **Add Variant**
2. Fill in:
   - Variant ID (e.g., `1M`, `1YEAR`)
   - Variant Name (e.g., `1 Month`, `1 Year`)
   - Price (e.g., `9.99`)
   - Tutorial Link (optional)
3. Click **Save Variant**

### Adding Stock
1. Go to **Stock Management** page
2. Find the variant you want to add stock to
3. Click **Add** button
4. Paste your accounts (one per line):
   ```
   email1@gmail.com,password123,PIN: 1234,Profile: A
   email2@gmail.com,password456,PIN: 5678,Profile: B
   ```
5. Click **Add Stock**

### Viewing Stock
1. Go to **Stock Management**
2. Click **View** button on any variant
3. See all available accounts

### Managing Users
1. Go to **Users** page
2. See all customers sorted by spending
3. View usernames, total spent, join dates

## 🎨 Features Walkthrough

### Dashboard Stats
- **Total Products**: Number of unique products
- **Total Revenue**: Sum of all customer spending
- **Total Users**: Registered customers
- **Total Stock**: Available accounts across all variants
- **Total Sold**: Number of completed orders

### Stock Status Colors
- 🟢 **Green (In Stock)**: More than 10 accounts
- 🟡 **Yellow (Low Stock)**: 1-10 accounts
- 🔴 **Red (Out of Stock)**: 0 accounts

### Product Card Actions
- ✏️ **Edit**: Modify product name/description
- 🗑️ **Delete**: Remove product and all variants
- ➕ **Add Variant**: Add new pricing option

### Variant Actions
- ✏️ **Edit**: Modify variant name/price/tutorial
- 🗑️ **Delete**: Remove variant and its stock

## 🔧 Troubleshooting

### Admin panel won't start
```bash
# Check if port 5000 is already in use
sudo lsof -i :5000

# Kill the process if needed
sudo kill -9 <PID>
```

### Can't access from browser
```bash
# Make sure the service is running
systemctl status admin-panel

# Check firewall
sudo ufw status

# Open port if needed
sudo ufw allow 5000/tcp
```

### Forgot admin password
```bash
# Reset to default
cd /root/telegram-store-bot
rm database/admin.json
# Restart admin panel - password will reset to admin123
```

## 🌟 Tips

1. **Bookmark the URL** for quick access
2. **Change password regularly** for security
3. **Use strong passwords** (mix of letters, numbers, symbols)
4. **Check stock levels daily** to avoid running out
5. **Monitor user spending** to identify top customers
6. **Add tutorial links** to reduce customer support

## 📊 Quick Commands

```bash
# Start admin panel
sudo systemctl start admin-panel

# Stop admin panel
sudo systemctl stop admin-panel

# Restart admin panel
sudo systemctl restart admin-panel

# View logs
journalctl -u admin-panel -f

# Check status
systemctl status admin-panel
```

## 🎯 Next Steps

1. ✅ Login and change default password
2. ✅ Add your products
3. ✅ Add variants with prices
4. ✅ Upload stock
5. ✅ Customize welcome message
6. ✅ Monitor dashboard regularly

## 🆘 Support

If you encounter any issues:
1. Check the logs: `journalctl -u admin-panel -f`
2. Restart the service: `sudo systemctl restart admin-panel`
3. Verify database folder exists: `ls -la /root/telegram-store-bot/database`

---

**Enjoy your professional admin panel! 🚀**
