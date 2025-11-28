# Bakong KHQR Proxy Setup Guide

## Problem
Bakong KHQR API has **IP restrictions** - it only works from **Cambodia IP addresses**. If you deploy your bot on Railway/Heroku/AWS outside Cambodia, payment verification will fail.

## Solution
Deploy this proxy server on a VPS with a **Cambodia IP address**. Your bot calls the proxy, and the proxy calls Bakong.

```
[Your Bot on Railway] → [Proxy in Cambodia] → [Bakong API]
     (Any IP)              (Cambodia IP)        (Accepts request)
```

---

## Step 1: Get a Cambodia VPS

Choose any provider with Cambodia servers:
- **DigitalOcean** - Singapore datacenter (closest)
- **Vultr** - Singapore 
- **Linode** - Singapore
- **Local Cambodia VPS** providers

Minimum specs: 1GB RAM, 1 CPU core ($5-10/month)

---

## Step 2: Deploy the Proxy

### On your Cambodia VPS:

```bash
# Install Python
sudo apt update
sudo apt install python3 python3-pip python3-venv -y

# Create project directory
mkdir bakong-proxy
cd bakong-proxy

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install flask bakong-khqr python-dotenv gunicorn
```

### Upload the proxy files:

**1. Create `proxy.py`:**
```python
from flask import Flask, request, jsonify
from bakong_khqr import KHQR
import os

app = Flask(__name__)
BAKONG_TOKEN = os.getenv("BAKONG_TOKEN", "")
khqr = KHQR(BAKONG_TOKEN)

@app.route('/create_qr', methods=['POST'])
def create_qr():
    try:
        data = request.json
        qr_code = khqr.create_qr(
            bank_account=data['bank_account'],
            merchant_name=data['merchant_name'],
            merchant_city="PP",
            amount=data['amount'],
            currency="USD",
            store_label="Store",
            phone_number="85512345678",
            bill_number=f"INV-{int(data['amount']*1000)}",
            terminal_label="Bot01"
        )
        md5 = khqr.generate_md5(qr_code)
        return jsonify({"qr_code": qr_code, "md5": md5})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/check/<md5>', methods=['GET'])
def check_payment(md5):
    try:
        result = khqr.check_payment(md5)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

**2. Create `.env`:**
```bash
BAKONG_TOKEN=your_bakong_token_here
```

**3. Run with Gunicorn:**
```bash
export BAKONG_TOKEN="your_token_here"
gunicorn -w 2 -b 0.0.0.0:5000 proxy:app
```

**4. Keep it running with systemd:**

Create `/etc/systemd/system/bakong-proxy.service`:
```ini
[Unit]
Description=Bakong KHQR Proxy
After=network.target

[Service]
User=root
WorkingDirectory=/root/bakong-proxy
Environment="BAKONG_TOKEN=your_token_here"
ExecStart=/root/bakong-proxy/venv/bin/gunicorn -w 2 -b 0.0.0.0:5000 proxy:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable bakong-proxy
sudo systemctl start bakong-proxy
sudo systemctl status bakong-proxy
```

---

## Step 3: Configure Your Bot

On Railway, add this environment variable:

```
BAKONG_PROXY_URL=http://your-cambodia-vps-ip:5000
```

Example:
```
BAKONG_PROXY_URL=http://123.45.67.89:5000
```

**Important:** 
- Use HTTP (not HTTPS) unless you setup SSL
- Include port `:5000`
- No trailing slash

---

## Step 4: Test

### Test the proxy:
```bash
# Health check
curl http://your-vps-ip:5000/health

# Create QR (test)
curl -X POST http://your-vps-ip:5000/create_qr \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 1.00,
    "bank_account": "your@account",
    "merchant_name": "Test Store"
  }'
```

### Test the bot:
1. Redeploy your Railway bot
2. Try buying a product
3. Check logs - should see `[PROXY KHQR CHECK]` messages

---

## Security (Optional but Recommended)

### Add API Key Authentication:

**proxy.py:**
```python
API_KEY = os.getenv("API_KEY", "secret123")

@app.before_request
def check_auth():
    if request.endpoint in ['create_qr', 'check_payment']:
        key = request.headers.get('X-API-Key')
        if key != API_KEY:
            return jsonify({"error": "unauthorized"}), 401
```

**In your bot's .env:**
```python
BAKONG_PROXY_URL=http://your-vps:5000
BAKONG_PROXY_KEY=secret123
```

---

## Troubleshooting

**Bot shows "KHQR not configured":**
- Make sure `BAKONG_PROXY_URL` is set in Railway

**Proxy returns errors:**
- Check if VPS has Cambodia IP: `curl ipinfo.io`
- Verify BAKONG_TOKEN is valid
- Check proxy logs: `journalctl -u bakong-proxy -f`

**Connection timeout:**
- Check firewall allows port 5000
- Try: `sudo ufw allow 5000`

---

## Cost Estimate

- **Cambodia VPS**: $5-10/month
- **Railway Bot**: Free tier ($5 credit/month)
- **Total**: ~$10/month for fully working bot

---

## Alternative: All-in-Cambodia Setup

Deploy BOTH the bot AND proxy on the same Cambodia VPS:
- No proxy needed
- Set BAKONG_TOKEN directly
- Costs the same (~$10/month)
- Simpler setup

Choose this if you're comfortable with VPS management!
