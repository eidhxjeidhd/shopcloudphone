import os
import time
import json
import random
import string
from flask import Flask, render_template_string, jsonify, request, session, redirect

app = Flask(__name__)
app.secret_key = ''.join(random.choices(string.ascii_letters + string.digits, k=32))

DB_FILE = "keys.json"
# Link Blogspot của ông
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
    # Kiểm tra xem đã vượt link thành công chưa qua session
    is_bypassed = session.get('bypassed', False)
    
    btn_class = "active" if is_bypassed else ""
    btn_disabled = "" if is_bypassed else "disabled"
    btn_text = "✨ NHẬN KEY NGAY" if is_bypassed else "🔒 2. TẠO KEY MỚI (CHƯA HOÀN TẤT)"
    note_text = "✅ Đã vượt link thành công! Bấm nhận key ngay." if is_bypassed else "⚠️ Bạn bắt buộc phải hoàn thành vượt link trên Blogspot và bấm quay lại đây!"
    note_color = "#4ade80" if is_bypassed else "#ef4444"

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
            .note {{ font-size: 11px; color: {note_color}; margin-top: 10px; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h2>🔑 Bảo Mật Chống Bypass</h2>
            <p style="font-size: 12px; color: #94a3b8;">Hoàn thành vượt link Blogspot để mở khóa Key.</p>
            
            <!-- Bước 1: Sang Blogspot -->
            <a href="{BLOGSPOT_LINK}" target="_blank" class="btn-link">🔗 1. VƯỢT LINK TRÊN BLOGSPOT</a>
            
            <!-- Bước 2: Nút nhận key chỉ sáng khi callback thành công -->
            <button id="getKeyBtn" class="{btn_class}" onclick="getNewKey()" {btn_disabled}>{btn_text}</button>
            <div class="note" id="noteText">{note_text}</div>
            
            <div style="text-align: left; margin-top: 20px; font-size: 12px; color: #94a3b8;">Key của bạn:</div>
            <div class="key-box" id="keyResult">Chưa có key hợp lệ.</div>
        </div>

        <script>
            function getNewKey() {{
                const keyBox = document.getElementById('keyResult');
                keyBox.innerText = "Đang tạo key...";

                fetch('/api/generate-key', {{ method: 'POST' }})
                    .then(res => res.json())
                    .then(data => {{
                        if(data.success) {{
                            keyBox.innerText = data.key;
                            alert("Thành công! Key có hiệu lực 24 giờ.");
                        }} else {{
                            keyBox.innerText = "❌ Lỗi: " + data.message;
                        }}
                    }})
                    .catch(err => {{
                        keyBox.innerText = "❌ Lỗi kết nối máy chủ.";
                    }});
            }}
        </script>
    </body>
    </html>
    """
    return render_template_string(html_template)

@app.route('/verify-success')
def verify_success():
    # Route này chỉ được gọi khi người dùng thực sự hoàn thành và quay lại từ Blogspot
    session['bypassed'] = True
    session['bypass_time'] = time.time()
    return redirect('/')

@app.route('/api/generate-key', methods=['POST'])
def api_generate_key():
    if not session.get('bypassed'):
        return jsonify({"success": False, "message": "Chưa hoàn tất vượt link! Đừng hòng bypass."}), 403

    try:
        db = load_db()
        new_k = generate_key()
        
        expire_time = time.time() + 86400 # 24 giờ
        db[new_k] = {
            "expires_at": expire_time,
            "created_at": time.time()
        }
        save_db(db)
        
        # Xóa session để bắt buộc lượt sau phải vượt link lại từ đầu
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
