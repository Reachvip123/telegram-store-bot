# Telegram Store Bot

A feature-rich Telegram bot for selling digital products (accounts, credentials, tutorials) with KHQR payment integration.

## Features

✅ Product listing and browsing  
✅ KHQR payment QR code generation  
✅ Order confirmation with delivered items  
✅ Tutorial links embedded in deliveries  
✅ Admin commands (add products, manage stock, set banners)  
✅ User transaction tracking  

## Setup

### 1. Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file from .env.example
cp .env.example .env
# Edit .env with your tokens and settings

# Run the bot
python storebot.py
```

### 2. Deploy to Railway

#### Create GitHub Repository

```bash
cd c:\Users\Reach\OneDrive\Desktop\telegrambot
git init
git add .
git commit -m "Initial bot commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/telegram-store-bot.git
git push -u origin main
```

#### Deploy on Railway

1. Go to [railway.app](https://railway.app)
2. Sign in with GitHub
3. Click **New Project** → **Deploy from GitHub**
4. Select `telegram-store-bot` repository
5. Railway auto-detects Python and creates a Worker dyno
6. Go to **Variables** and add:
   - `BOT_TOKEN` = your bot token
   - `BAKONG_TOKEN` = your bakong token
   - `ADMIN_ID` = your admin user ID
   - `ADMIN_USERNAME` = your admin handle
   - `BAKONG_ACCOUNT` = your bakong account
   - `MERCHANT_NAME` = your merchant name
   - `USE_MONGODB` = false (for now, use local storage)
7. Click **Deploy** ✅

Your bot now runs 24/7!

## Database Options

### Option A: Local Storage (Default)
- Uses JSON files in `database/` folder
- No setup needed
- Limited to file-based backups

### Option B: MongoDB (Recommended)

1. Sign up at [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)
2. Create a free cluster
3. Get connection string: `mongodb+srv://user:pass@cluster.mongodb.net/telegram_store_bot`
4. Add to Railway Variables:
   - `USE_MONGODB` = true
   - `MONGODB_URI` = your connection string
5. Restart your bot ✅

## Admin Commands

| Command | Description |
|---------|-------------|
| `/start` | Start the bot |
| `/admin` | Show admin menu |
| `/addpd Name \| Var \| Price \| Desc` | Add product |
| `/addstock` | Interactive stock manager |
| `/tutorial` | Set tutorial links for variants |
| `/broadcast Message` | Send message to all users |
| `/stock` | View stock report |

## Stock Format

When adding stock, use this format:

```
email,password,Pin : 3,Profile : A
```

This will display as:

```
📦 Item Details
💌 : email
🔑 : password

More Info ...
Pin : 3
Profile : A

[Tutorial Sign In](url)
```

## Environment Variables

See `.env.example` for all options.

Key variables:
- `BOT_TOKEN` - Telegram bot token from @BotFather
- `BAKONG_TOKEN` - Your Bakong API token
- `ADMIN_ID` - Your Telegram user ID
- `USE_MONGODB` - Set to `true` to use MongoDB
- `MONGODB_URI` - MongoDB connection string

## Support

For issues or feature requests, contact @dzy4u2 on Telegram.

## License

MIT
