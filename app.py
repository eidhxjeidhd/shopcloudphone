import os
import time
import json
import random
import string
from flask import Flask, render_template_string, jsonify, request, session

app = Flask(__name__)
app.secret_key = ''.join(random.choices(string.ascii_letters + string.digits, k=32)) # Khóa mã hóa session bảo mật

DB_FILE = "keys.json"
BLOGSPOT_LINK = "https://tieb0iedbd8uhsb.blogspot.com/2026/10/gagaming-vuot-link-lay-key-box-sizing_01383317790.html?m=1"

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
    part1 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    part2 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"GA-{part1}-{part2}"

@app.route('/')
def index():
    html_template = f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Hệ Thống Lấy Key 24H - Gà Gaming</title>
        <style>
            body {{ background: #0f172a; color: #f8fafc; font-family: sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }}
            .card {{ background: #1e293b; padding: 25px; border-radius: 16px; width: 100%; max-width: 440px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); box-sizing: border-box; text-align: center; }}
            .btn-link {{ background: #3b82f6; text-decoration: none; display: block; padding: 12px; border-radius: 8px; font-weight: bold; color: white; margin-top: 15px; box-sizing: border-box; transition: 0.2s; }}
            .btn-link:hover {{ background: #2563eb; }}
            
            button {{ background: #475569; color: #94a3b8; border: none; padding: 12px; width: 100%; border-radius: 8px; font-weight: bold; cursor: not-allowed; margin-top: 15px; transition: 0.2s; }}
            button.active {{ background: #22c55e; color: white; cursor: pointer; }}
            button.active:hover {{ background: #16a34a; }}
            
            .key-box {{ margin-top: 15px; font-size: 14px; color: #4ade80; background: #0b0f19; padding: 12px; border-radius: 8px; border: 1px solid #334155; word-break: break-all; user-select: all; }}
            .note {{ font-size: 11px; color: #ef4444; margin-top: 10px; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h2>🔑 Chống Bypass Key 24H</h2>
            <p style="font-size: 12px; color: #94a3b8;">Hệ thống bảo mật chống lách luật. Vui lòng làm đúng các bước!</p>
            
            <!-- Bước 1: Click để sang Blogspot lấy token hợp lệ -->
            <a href="{BLOGSPOT_LINK}" target="_blank" class="btn-link" onclick="triggerBypassCheck()">🔗 1. VƯỢT LINK TRÊN BLOGSPOT</a>
            
            <!-- Bước 2: Nút tạo key, bị khóa chặt nếu chưa kích hoạt token -->
            <button id="getKeyBtn" onclick="getNewKey()" disabled>🔒 2. TẠO KEY MỚI (CHƯA XÁC THỰC)</button>
            <div class="note" id="noteText">⚠️ Cảnh báo: Cố tình bypass API sẽ bị chặn vĩnh viễn!</div>
            
            <div style="text-align: left; margin-top: 20px; font-size: 12px; color: #94a3b8;">Key của bạn:</div>
            <div class="key-box" id="keyResult">Chưa có key hợp lệ.</div>
        </div>

        <script>
            function triggerBypassCheck() {{
                // Gửi request ngầm lên server ghi nhận phiên vượt link hợp lệ
                fetch('/api/set-bypass', {{ method: 'POST' }})
                    .then(res => res.json())
                    .then(data => {{
                        if(data.success) {{
                            const btn = document.getElementById('getKeyBtn');
                            const note = document.getElementById('noteText');
                            
                            btn.removeAttribute('disabled');
                            btn.classList.add('active');
                            btn.innerText = "✨ NHẬN KEY NGAY";
                            note.style.color = "#4ade80";
                            note.innerText = "✅ Đã qua trạm vượt link thành công!";
                        }}
                    }});
            }}

            function getNewKey() {{
                const keyBox = document.getElementById('keyResult');
                keyBox.innerText = "Đang kiểm tra bảo mật chống bypass...";

                fetch('/api/generate-key', {{ method: 'POST' }})
                    .then(res => res.json())
                    .then(data => {{
                        if(data.success) {{
                            keyBox.innerText = data.key;
                            alert("Thành công! Key có hiệu lực 24 giờ.");
                        }} else {{
                            keyBox.innerText = "❌ Chặn Bypass: " + data.message;
                        }}
                    }})
                    .catch(err => {{
                        keyBox.innerText = "❌ Lỗi kết nối hệ thống.";
                    }});
            }}
        </script>
    </body>
    </html>
    """
    return render_template_string(html_template)

@app.route('/api/set-bypass', methods=['POST'])
def api_set_bypass():
    # Đánh dấu session này đã thực hiện qua bước vượt link
    session['bypassed'] = True
    session['bypass_time'] = time.time()
    return jsonify({"success": True})

@app.route('/api/generate-key', methods=['POST'])
def api_generate_key():
    # Kiểm tra xem có dấu vết vượt link chưa (Chống gọi API trực tiếp)
    if not session.get('bypassed'):
        return jsonify({"success": False, "message": "Phát hiện hành vi cố tình Bypass/Cào API! Hãy làm đúng quy trình."}), 403
    
    # Ép thời gian delay chống auto click quá nhanh (Ví dụ phải qua ít nhất 3 giây từ lúc bấm link)
    elapsed = time.time() - session.get('bypass_time', 0)
    if elapsed < 2:
        return jsonify({"success": False, "message": "Thao tác quá nhanh! Vui lòng không spam."}), 403

    try:
        db = load_db()
        new_k = generate_key()
        
        expire_time = time.time() + 86400 # 24 giờ
        db[new_k] = {
            "expires_at": expire_time,
            "created_at": time.time()
        }
        save_db(db)
        
        # Xóa session để chống dùng lại 1 lần vượt link lấy nhiều key liên tục nếu muốn
        session.pop('bypassed', None)
        
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
