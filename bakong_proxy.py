"""
Bakong KHQR Proxy Server
Deploy this in Cambodia (VPS with Cambodia IP) to bypass IP restrictions
"""
from flask import Flask, request, jsonify
from bakong_khqr import KHQR
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
BAKONG_TOKEN = os.getenv("BAKONG_TOKEN", "")
khqr = KHQR(BAKONG_TOKEN)

@app.route('/create_qr', methods=['POST'])
def create_qr():
    """Create KHQR QR code"""
    try:
        data = request.json
        amount = data.get('amount')
        bank_account = data.get('bank_account')
        merchant_name = data.get('merchant_name')
        
        qr_code = khqr.create_qr(
            bank_account=bank_account,
            merchant_name=merchant_name,
            merchant_city="PP",
            amount=amount,
            currency="USD",
            store_label="Store",
            phone_number="85512345678",
            bill_number=f"INV-{int(amount*1000)}",
            terminal_label="Bot01"
        )
        
        md5 = khqr.generate_md5(qr_code)
        
        return jsonify({
            "qr_code": qr_code,
            "md5": md5,
            "status": "success"
        })
    except Exception as e:
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500

@app.route('/check/<md5>', methods=['GET'])
def check_payment(md5):
    """Check payment status"""
    try:
        result = khqr.check_payment(md5)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "service": "bakong-khqr-proxy"
    })

if __name__ == '__main__':
    print("[OK] Bakong KHQR Proxy Server Starting...")
    print(f"[INFO] Make sure this runs on a Cambodia IP address")
    app.run(host='0.0.0.0', port=5000)
