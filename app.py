import os
import time
import json
import random
import string
from flask import Flask, render_template_string, jsonify, request

app = Flask(__name__)

DB_FILE = "keys.json"

# Hàm đọc/ghi database JSON đơn giản cho Render
def load_db():
    if not os.path.exists(DB_FILE):
        return {}
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

def generate_key():
    # Tạo mã key ngẫu nhiên dạng GA-xxxx-xxxx
    part1 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    part2 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"GA-{part1}-{part2}"

@app.route('/')
def index():
    html_template = """
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Hệ Thống Lấy Key 24H</title>
        <style>
            body { background: #0f172a; color: #f8fafc; font-family: sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }
            .card { background: #1e293b; padding: 25px; border-radius: 16px; width: 100%; max-width: 440px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); box-sizing: border-box; text-align: center; }
            button { background: #22c55e; color: white; border: none; padding: 12px; width: 100%; border-radius: 8px; font-weight: bold; cursor: pointer; margin-top: 15px; transition: 0.2s; }
            button:hover { background: #16a34a; }
            .key-box { margin-top: 15px; font-size: 14px; color: #4ade80; background: #0b0f19; padding: 12px; border-radius: 8px; border: 1px solid #334155; word-break: break-all; user-select: all; }
        </style>
    </head>
    <body>
        <div class="card">
            <h2>🔑 Hệ Thống Key 24H</h2>
            <p style="font-size: 12px; color: #94a3b8;">Vượt link rút gọn để nhận key sử dụng trong 24 giờ</p>
            
            <button onclick="getNewKey()">Lấy Key Mới Ngay</button>
            
            <div style="text-align: left; margin-top: 20px; font-size: 12px; color: #94a3b8;">Key của bạn:</div>
            <div class="key-box" id="keyResult">Chưa có key được tạo.</div>
        </div>

        <script>
            function getNewKey() {
                const keyBox = document.getElementById('keyResult');
                keyBox.innerText = "Đang khởi tạo key trên hệ thống...";

                fetch('/api/generate-key')
                    .then(res => res.json())
                    .then(data => {
                        if(data.success) {
                            keyBox.innerText = data.key;
                            alert("Đã tạo key thành công! Key có hiệu lực 24 giờ.");
                        } else {
                            keyBox.innerText = "❌ Lỗi: " + data.message;
                        }
                    })
                    .catch(err => {
                        keyBox.innerText = "❌ Lỗi kết nối đến máy chủ.";
                    });
            }
        </script>
    </body>
    </html>
    """
    return render_template_string(html_template)

@app.route('/api/generate-key')
def api_generate_key():
    try:
        db = load_db()
        new_k = generate_key()
        
        # Thời hạn 24 giờ tính bằng giây (24 * 3600 = 86400 giây)
        expire_time = time.time() + 86400 
        
        db[new_k] = {
            "expires_at": expire_time,
            "created_at": time.time()
        }
        save_db(db)
        
        return jsonify({"success": True, "key": new_k})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@app.route('/api/check-key')
def api_check_key():
    key_input = request.args.get('key')
    if not key_input:
        return jsonify({"success": False, "message": "Thiếu thông tin Key!"})
    
    db = load_db()
    if key_input in db:
        key_data = db[key_input]
        if time.time() < key_data["expires_at"]:
            remaining_hours = round((key_data["expires_at"] - time.time()) / 3600, 1)
            return jsonify({"success": True, "status": "valid", "message": f"Key hợp lệ! Còn hạn {remaining_hours} giờ."})
        else:
            return jsonify({"success": False, "status": "expired", "message": "Key đã hết hạn 24h!"})
    else:
        return jsonify({"success": False, "status": "invalid", "message": "Key không tồn tại trên hệ thống!"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
