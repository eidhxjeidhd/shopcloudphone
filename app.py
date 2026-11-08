import os
import time
import json
import random
import string
from flask import Flask, render_template_string, jsonify, request, session, redirect

app = Flask(__name__)
app.secret_key = ''.join(random.choices(string.ascii_letters + string.digits, k=32))

DB_FILE = "keys_stock_custom.json"
ADMIN_PASSWORD = "admin_gagaming_123" # Mật khẩu admin
BLOGSPOT_LINK = "https://tieb0iedbd8uhsb.blogspot.com/2026/10/gagaming-vuot-link-lay-key-box-sizing_01383317790.html?m=1"

def load_db():
    if not os.path.exists(DB_FILE):
        return {"stock": [], "active": {}}
    try:
        with open(DB_FILE, "r") as f:
            data = json.load(f)
            if "stock" not in data: data["stock"] = []
            if "active" not in data: data["active"] = {}
            return data
    except:
        return {"stock": [], "active": {}}

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

# --- 1. GIAO DIỆN CHÍNH CHO NGƯỜI DÙNG ---
@app.route('/')
def home():
    db = load_db()
    stock_count = len(db["stock"])
    
    html_template = f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Hệ Thống Kho Key - Gà Gaming</title>
        <style>
            body {{ background: #0f172a; color: #f8fafc; font-family: sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }}
            .card {{ background: #1e293b; padding: 25px; border-radius: 16px; width: 100%; max-width: 440px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); box-sizing: border-box; text-align: center; }}
            .btn-link {{ background: #3b82f6; text-decoration: none; display: block; padding: 12px; border-radius: 8px; font-weight: bold; color: white; margin-top: 15px; box-sizing: border-box; transition: 0.2s; }}
            .btn-link:hover {{ background: #2563eb; }}
            
            button {{ background: #475569; color: #94a3b8; border: none; padding: 12px; width: 100%; border-radius: 8px; font-weight: bold; cursor: not-allowed; margin-top: 15px; transition: 0.2s; }}
            button.active {{ background: #22c55e; color: white; cursor: pointer; }}
            button.active:hover {{ background: #16a34a; }}
            
            .stock-badge {{ background: #334155; color: #38bdf8; padding: 6px 12px; border-radius: 20px; font-size: 12px; display: inline-block; margin-bottom: 15px; font-weight: bold; }}
            .key-box {{ margin-top: 15px; font-size: 14px; color: #4ade80; background: #0b0f19; padding: 12px; border-radius: 8px; border: 1px solid #334155; word-break: break-all; user-select: all; }}
            .note {{ font-size: 11px; color: #ef4444; margin-top: 10px; }}
            .admin-link {{ display: block; margin-top: 15px; font-size: 11px; color: #64748b; text-decoration: none; }}
            .admin-link:hover {{ color: #94a3b8; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h2>🔑 Kho Key Tự Động</h2>
            <div class="stock-badge">📦 Số key sẵn sàng trong kho: {stock_count} Key</div>
            <p style="font-size: 12px; color: #94a3b8;">Vượt link Blogspot để rút ngẫu nhiên 1 key từ kho.</p>
            
            <a href="{BLOGSPOT_LINK}" target="_blank" class="btn-link" onclick="markBypass()">🔗 1. VƯỢT LINK TRÊN BLOGSPOT</a>
            
            <button id="getKeyBtn" onclick="getKeyFromStock()" disabled>🔒 2. NHẬN KEY TỪ KHO (CHƯA VƯỢT LINK)</button>
            <div class="note" id="noteText">⚠️ Hãy bấm nút số 1, sau đó quay lại đây để nhận Key!</div>
            
            <div style="text-align: left; margin-top: 20px; font-size: 12px; color: #94a3b8;">Key của bạn:</div>
            <div class="key-box" id="keyResult">Chưa có key được rút.</div>

            <a href="/admin" class="admin-link">⚙️ Quản lý kho (Admin)</a>
        </div>

        <script>
            function markBypass() {{
                localStorage.setItem('ga_bypass_time', Date.now());
                setTimeout(() => {{
                    localStorage.setItem('ga_bypassed', 'true');
                    checkBypassStatus();
                }}, 3000);
            }}

            window.addEventListener('focus', checkBypassStatus);
            window.addEventListener('DOMContentLoaded', checkBypassStatus);

            function checkBypassStatus() {{
                const isBypassed = localStorage.getItem('ga_bypassed');
                if (isBypassed === 'true') {{
                    const btn = document.getElementById('getKeyBtn');
                    const note = document.getElementById('noteText');
                    
                    btn.removeAttribute('disabled');
                    btn.classList.add('active');
                    btn.innerText = "✨ RÚT KEY NGAY TỪ KHO";
                    note.style.color = "#4ade80";
                    note.innerText = "✅ Đã vượt link thành công! Bấm nhận key ngay.";
                }}
            }}

            function getKeyFromStock() {{
                const keyBox = document.getElementById('keyResult');
                keyBox.innerText = "Đang rút key từ kho...";

                fetch('/api/get-key')
                    .then(res => res.json())
                    .then(data => {{
                        if(data.success) {{
                            keyBox.innerText = data.key + " (Hạn: " + data.days + " ngày)";
                            alert("Rút key thành công! Thời hạn: " + data.days + " ngày.");
                            localStorage.removeItem('ga_bypassed');
                            location.reload();
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

# --- 2. API RÚT KEY ---
@app.route('/api/get-key')
def api_get_key():
    db = load_db()
    if not db["stock"]:
        return jsonify({"success": False, "message": "Kho đã hết sạch key! Vui lòng đợi Admin nạp thêm."})
    
    # Rút key đầu tiên trong kho (mỗi item lưu key và số ngày)
    item = db["stock"].pop(0)
    assigned_key = item["key"]
    duration_days = item["days"]
    
    expire_time = time.time() + (duration_days * 86400)
    db["active"][assigned_key] = {
        "expires_at": expire_time,
        "days": duration_days,
        "claimed_at": time.time()
    }
    
    save_db(db)
    return jsonify({"success": True, "key": assigned_key, "days": duration_days})

# --- 3. TRANG ADMIN QUẢN LÝ ---
@app.route('/admin', methods=['GET', 'POST'])
def admin_panel():
    db = load_db()
    message = ""
    
    if request.method == 'POST' and 'password' in request.form and 'keys_input' not in request.form:
        if request.form.get('password') == ADMIN_PASSWORD:
            session['admin_logged'] = True
            return redirect('/admin')
        else:
            message = "❌ Mật khẩu Admin không chính xác!"

    if not session.get('admin_logged'):
        return render_template_string(f"""
        <!DOCTYPE html>
        <html lang="vi">
        <head>
            <meta charset="UTF-8">
            <title>Đăng Nhập Admin</title>
            <style>
                body {{ background: #0f172a; color: #f8fafc; font-family: sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }}
                .card {{ background: #1e293b; padding: 25px; border-radius: 16px; width: 100%; max-width: 360px; text-align: center; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }}
                input {{ width: 100%; padding: 10px; border-radius: 8px; border: 1px solid #334155; background: #0f172a; color: white; box-sizing: border-box; margin-top: 15px; }}
                button {{ background: #3b82f6; color: white; border: none; padding: 10px; width: 100%; border-radius: 8px; font-weight: bold; cursor: pointer; margin-top: 15px; }}
                button:hover {{ background: #2563eb; }}
                .error {{ color: #ef4444; font-size: 12px; margin-top: 10px; }}
            </style>
        </head>
        <body>
            <div class="card">
                <h2>🔐 Đăng Nhập Admin</h2>
                <form method="POST">
                    <input type="password" name="password" placeholder="Nhập mật khẩu Admin..." required>
                    <button type="submit">Đăng Nhập</button>
                </form>
                <div class="error">{message}</div>
                <br><a href="/" style="color: #94a3b8; font-size: 12px; text-decoration: none;">← Quay lại trang chủ</a>
            </div>
        </body>
        </html>
        """)

    # Nạp key kèm chọn số ngày
    if request.method == 'POST' and 'keys_input' in request.form:
        raw_keys = request.form.get('keys_input')
        try:
            days = int(request.form.get('days', 1))
        except:
            days = 1
            
        new_keys = [k.strip() for k in raw_keys.splitlines() if k.strip()]
        
        for k in new_keys:
            db["stock"].append({"key": k, "days": days})
            
        save_db(db)
        message = f"✅ Đã nạp thành công {len(new_keys)} key (Thời hạn: {days} ngày) vào kho!"

    stock_count = len(db["stock"])
    
    return render_template_string(f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <title>Quản Lý Kho Key - Admin</title>
        <style>
            body {{ background: #0f172a; color: #f8fafc; font-family: sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }}
            .card {{ background: #1e293b; padding: 25px; border-radius: 16px; width: 100%; max-width: 500px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); box-sizing: border-box; }}
            textarea {{ width: 100%; height: 120px; background: #0f172a; color: #4ade80; border: 1px solid #334155; border-radius: 8px; padding: 10px; box-sizing: border-box; font-family: monospace; margin-top: 10px; }}
            input, select {{ width: 100%; padding: 10px; border-radius: 8px; border: 1px solid #334155; background: #0f172a; color: white; box-sizing: border-box; margin-top: 10px; }}
            button {{ background: #22c55e; color: white; border: none; padding: 12px; width: 100%; border-radius: 8px; font-weight: bold; cursor: pointer; margin-top: 15px; }}
            button:hover {{ background: #16a34a; }}
            .logout {{ background: #ef4444; margin-top: 10px; }}
            .logout:hover {{ background: #dc2626; }}
            .success {{ color: #4ade80; font-size: 13px; margin-top: 10px; text-align: center; }}
            .stat {{ background: #0b0f19; padding: 10px; border-radius: 8px; margin-bottom: 15px; text-align: center; font-size: 14px; color: #38bdf8; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h2>⚙️ Tùy Chỉnh Kho Key</h2>
            <div class="stat">📦 Tổng số key trong kho: {stock_count} Key</div>
            
            <form method="POST">
                <label style="font-size: 12px; color: #94a3b8;">Chọn số ngày hiệu lực cho lô key này:</label>
                <select name="days">
                    <option value="1">1 Ngày (24 Giờ)</option>
                    <option value="3">3 Ngày</option>
                    <option value="7">7 Ngày (1 Tuần)</option>
                    <option value="30">30 Ngày (1 Tháng)</option>
                    <option value="365">Vĩnh viễn (365 Ngày)</option>
                </select>

                <label style="font-size: 12px; color: #94a3b8; display: block; margin-top: 10px;">Danh sách Key (mỗi key một dòng):</label>
                <textarea name="keys_input" placeholder="GA-ABCD-1234&#10;GA-EFGH-5678"></textarea>
                <button type="submit">📥 Nạp Key Vào Kho</button>
            </form>
            
            <div class="success">{message}</div>

            <form action="/admin/logout" method="POST">
                <button type="submit" class="logout">Đăng Xuất</button>
            </form>
            <div style="text-align: center; margin-top: 15px;">
                <a href="/" style="color: #94a3b8; font-size: 12px; text-decoration: none;">← Về trang chủ lấy key</a>
            </div>
        </div>
    </body>
    </html>
    """, stock_count=stock_count, message=message)

@app.route('/admin/logout', methods=['POST'])
def admin_logout():
    session.pop('admin_logged', None)
    return redirect('/admin')

# --- 4. API KIỂM TRA KEY TRONG SCRIPT ---
@app.route('/api/check-key')
def api_check_key():
    key_input = request.args.get('key')
    if not key_input:
        return jsonify({"success": False, "message": "Thiếu thông tin Key!"})
    
    db = load_db()
    if key_input in db["active"]:
        key_data = db["active"][key_input]
        if time.time() < key_data["expires_at"]:
            remaining_hours = round((key_data["expires_at"] - time.time()) / 3600, 1)
            return jsonify({"success": True, "status": "valid", "message": f"Key hợp lệ! Còn hạn {remaining_hours} giờ."})
        else:
            return jsonify({"success": False, "status": "expired", "message": "Key đã hết hạn!"})
    else:
        return jsonify({"success": False, "status": "invalid", "message": "Key không tồn tại hoặc chưa được rút từ kho!"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
