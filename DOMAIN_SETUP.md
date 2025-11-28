# 🌐 Custom Domain Setup Guide
## Domain: dzpremium.store

## 📋 Prerequisites
- Domain: **dzpremium.store** (registered and owned by you)
- VPS IP: **157.10.73.90**
- Admin panel running on port 5000

## 🎯 Recommended Setup

### Option 1: Subdomain (RECOMMENDED)
Use: **admin.dzpremium.store**

**Benefits:**
- Keep main domain for website/landing page
- Professional separation
- Easier to manage

### Option 2: Main Domain
Use: **dzpremium.store**

**Benefits:**
- Simpler URL
- No subdomain needed

---

## 🚀 Quick Setup (Automated)

### Step 1: Configure DNS First

Go to your domain registrar and add an **A Record**:

**For Subdomain (admin.dzpremium.store):**
```
Type: A
Name: admin
Value: 157.10.73.90
TTL: 3600
```

**For Main Domain (dzpremium.store):**
```
Type: A
Name: @ (or leave blank)
Value: 157.10.73.90
TTL: 3600
```

**Wait 5-10 minutes for DNS propagation.**

### Step 2: Run Automated Setup Script

On your VPS, run:

```bash
cd /root/telegram-store-bot
git pull
chmod +x setup-domain.sh
./setup-domain.sh
```

The script will:
- ✅ Install Nginx web server
- ✅ Configure reverse proxy
- ✅ Install SSL certificate (HTTPS)
- ✅ Setup auto-renewal
- ✅ Configure firewall

### Step 3: Access Your Admin Panel

**With SSL (HTTPS):**
```
https://admin.dzpremium.store
```
or
```
https://dzpremium.store
```

🔒 Secure connection with valid SSL certificate!

---

## 🔧 Manual Setup (Alternative)

If you prefer manual setup:

### 1. Install Nginx
```bash
sudo apt update
sudo apt install nginx -y
```

### 2. Create Nginx Configuration
```bash
sudo nano /etc/nginx/sites-available/admin-panel
```

Paste this (replace `admin.dzpremium.store` with your domain):
```nginx
server {
    listen 80;
    server_name admin.dzpremium.store;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### 3. Enable Site
```bash
sudo ln -s /etc/nginx/sites-available/admin-panel /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

### 4. Configure Firewall
```bash
sudo ufw allow 'Nginx Full'
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

### 5. Install SSL Certificate
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d admin.dzpremium.store
```

Follow the prompts:
- Enter email: your@email.com
- Agree to terms: Yes
- Redirect HTTP to HTTPS: Yes (recommended)

---

## ✅ Verification

### Check DNS Propagation
```bash
# On your local computer
nslookup admin.dzpremium.store
```

Should show: `157.10.73.90`

### Check Nginx Status
```bash
sudo systemctl status nginx
```

### Check SSL Certificate
```bash
sudo certbot certificates
```

### Test Admin Panel
Open browser and visit:
```
https://admin.dzpremium.store
```

---

## 🔄 SSL Auto-Renewal

Certbot automatically renews certificates. To test:

```bash
sudo certbot renew --dry-run
```

View renewal timer:
```bash
sudo systemctl status certbot.timer
```

---

## 🛠️ Troubleshooting

### DNS Not Resolving
```bash
# Wait 5-10 minutes for propagation
# Check DNS
dig admin.dzpremium.store
```

### Nginx Not Starting
```bash
# Check configuration
sudo nginx -t

# View logs
sudo tail -f /var/log/nginx/error.log
```

### SSL Certificate Failed
```bash
# Make sure DNS is pointing to VPS
# Make sure ports 80 and 443 are open
sudo ufw status

# Retry SSL
sudo certbot --nginx -d admin.dzpremium.store
```

### Can't Access Admin Panel
```bash
# Check if admin panel is running
systemctl status admin-panel

# Check if it's listening on port 5000
sudo lsof -i :5000

# Restart admin panel
systemctl restart admin-panel
```

---

## 🔐 Security Best Practices

1. **Change default password** immediately after setup
2. **Use strong passwords** (12+ characters)
3. **Keep SSL certificate active** (auto-renewed)
4. **Monitor access logs:**
   ```bash
   sudo tail -f /var/log/nginx/access.log
   ```
5. **Update regularly:**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

---

## 📊 Service Management

### Nginx Commands
```bash
sudo systemctl start nginx      # Start
sudo systemctl stop nginx       # Stop
sudo systemctl restart nginx    # Restart
sudo systemctl status nginx     # Status
sudo nginx -t                   # Test config
```

### Admin Panel Commands
```bash
sudo systemctl start admin-panel
sudo systemctl stop admin-panel
sudo systemctl restart admin-panel
sudo systemctl status admin-panel
```

---

## 🎨 Custom Configurations

### Change Domain Later
```bash
sudo nano /etc/nginx/sites-available/admin-panel
# Update server_name
sudo nginx -t
sudo systemctl restart nginx
```

### Add Multiple Domains
```nginx
server_name admin.dzpremium.store dzpremium.store;
```

### Add Basic Auth (Extra Security)
```bash
sudo apt install apache2-utils -y
sudo htpasswd -c /etc/nginx/.htpasswd admin
sudo nano /etc/nginx/sites-available/admin-panel
```

Add to location block:
```nginx
auth_basic "Admin Area";
auth_basic_user_file /etc/nginx/.htpasswd;
```

---

## 📞 Quick Reference

**Your Domain:** dzpremium.store  
**Subdomain:** admin.dzpremium.store  
**VPS IP:** 157.10.73.90  
**Admin Panel Port:** 5000  
**Nginx Config:** /etc/nginx/sites-available/admin-panel  
**SSL Certs:** /etc/letsencrypt/live/

**Default Login:**
- Username: `admin`
- Password: `admin123`

---

## ✨ Next Steps

1. ✅ Configure DNS (A Record)
2. ✅ Run setup script or manual setup
3. ✅ Access via HTTPS
4. ✅ Change admin password
5. ✅ Start managing your store!

**Enjoy your professional admin panel with custom domain! 🚀**
