# 🇰🇭 Bakong KHQR Payment Guide

## What is KHQR?

**Khmer QR (KHQR)** is Cambodia's official QR payment standard created by the National Bank of Cambodia. It allows customers to pay instantly using any Bakong-enabled banking app.

---

## ✅ Your Bot Generates OFFICIAL Bakong KHQR Codes

When customers click "Pay with KHQR", they get a **real Bakong KHQR code** that works with:

### 🏦 All Bakong-Enabled Apps:
- ✅ **ABA Mobile** (ABA Bank)
- ✅ **Wing Money** (Wing Bank)
- ✅ **TrueMoney** (TrueMoney Cambodia)
- ✅ **Pi Pay** (PPAY)
- ✅ **ACLEDA Mobile**
- ✅ **Sathapana Mobile**
- ✅ **Canadia Mobile**
- ✅ **Any bank app with Bakong QR scanner**

---

## 📱 How Cambodian Customers Pay:

### Step 1: Customer Views Product
- Browses products in your Telegram bot
- Selects product and quantity

### Step 2: Customer Clicks "Pay with KHQR"
- Bot generates official Bakong KHQR code
- Shows QR code with green color (Bakong official)
- Displays amount and payment instructions

### Step 3: Customer Scans with Banking App
Customer opens any banking app (ABA, Wing, etc.):
1. Tap "Scan QR" or "Bakong QR"
2. Scan the QR code from Telegram
3. Confirm payment
4. Done! ✅

### Step 4: Automatic Delivery
- Bot detects payment via Bakong API
- Automatically delivers product to customer
- Sends receipt with transaction ID

---

## 🎨 QR Code Design

Your KHQR codes have:
- ✅ **Official Bakong green color** (#107c42)
- ✅ **Proper KHQR data format**
- ✅ **Merchant information**
- ✅ **Exact amount encoded**
- ✅ **Unique MD5 hash for tracking**

---

## 💡 Why Cambodians Love KHQR:

1. **Fast** - Payment in 3 seconds
2. **Safe** - Official NBC standard
3. **Easy** - Just scan with banking app
4. **Popular** - Everyone in Cambodia uses it
5. **Universal** - Works with any Bakong bank

---

## 🔧 Technical Details

### What the bot does:

```python
# 1. Generate official KHQR code
qr_code = khqr.create_qr(
    bank_account=BAKONG_ACCOUNT,
    merchant_name=MERCHANT_NAME,
    amount=amount,
    currency="USD"
)

# 2. Create unique payment ID
md5 = khqr.generate_md5(qr_code)

# 3. Check payment status
result = khqr.check_payment(md5)
# Returns: "PAID" when customer pays

# 4. Auto-deliver product
```

---

## 📊 Payment Flow

```
Customer Buys → Generate KHQR → Show QR Code
                                      ↓
                                Customer Scans
                                      ↓
                                Banking App Opens
                                      ↓
                                Customer Confirms
                                      ↓
                     ← Bakong API Notifies Bot ←
                                      ↓
                              Bot Delivers Product
                                      ↓
                            Customer Gets Receipt
```

---

## ⚙️ Configuration

Your bot needs:

### Required Environment Variables:
```env
BAKONG_TOKEN=your_bakong_api_token
BAKONG_ACCOUNT=your_account@bank
MERCHANT_NAME=Your Store Name
```

### Optional (for non-Cambodia deployment):
```env
BAKONG_PROXY_URL=http://cambodia-vps:5000
```

---

## 🎯 Benefits for Your Business

1. **Instant Payment** - No waiting for bank transfers
2. **Auto-Verification** - Bot checks payment automatically
3. **No Manual Work** - 100% automated delivery
4. **Trusted** - Official NBC Bakong system
5. **Wide Acceptance** - All major banks support it

---

## 📱 Popular in Cambodia

Almost **everyone in Cambodia** has:
- ABA Mobile
- Wing Money
- TrueMoney
- Or other Bakong-enabled bank apps

So your customers can pay easily! 🇰🇭

---

## 🚀 Your Bot is Ready!

Your bot already generates **100% real Bakong KHQR codes**. Cambodian customers will recognize the green QR and know exactly what to do.

No training needed - it's the same QR they scan at:
- Restaurants 🍜
- Coffee shops ☕
- Markets 🛒
- Gas stations ⛽
- Everywhere in Cambodia! 🇰🇭
