import os
import time
import json
import random
import string
from flask import Flask, render_template_string, jsonify, request, session, redirect

app = Flask(__name__)
app.secret_key = ''.join(random.choices(string.ascii_letters + string.digits, k=32))

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS'
    return response

DB_FILE = "keys_stock_custom.json"
ADMIN_PASSWORD = "admin_gagaming_123"

def load_db():
    if not os.path.exists(DB_FILE):
        return {"stock": [], "active": {}, "current_link": ""}
    try:
        with open(DB_FILE, "r") as f:
            data = json.load(f)
            if "stock" not in data: data["stock"] = []
            if "active" not in data: data["active"] = {}
            if "current_link" not in data: data["current_link"] = ""
            return data
    except:
        return {"stock": [], "active": {}, "current_link": ""}

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

# --- 1. GIAO DIỆN CHÍNH CHO NGƯỜI DÙNG (KHÓA ĐƠ VĨNH VIỄN NẾU KHÔNG VƯỢT LINK) ---
@app.route('/')
def home():
    db = load_db()
    stock_count = len(db["stock"])
    current_link = db.get("current_link", "")
    
    if not current_link:
        btn_html = '<div style="background: #334155; color: #ef4444; padding: 12px; border-radius: 8px; font-weight: bold; margin-top: 15px; font-size: 13px;">⚠️ Admin chưa thiết lập Link vượt key!</div>'
    else:
        btn_html = f'<a href="{current_link}" target="_blank" class="btn-link" onclick="markTargetClicked()">🔗 BƯỚC 1: MỞ TRANG VƯỢT LINK</a>'

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
            button.locked {{ background: #7f1d1d !important; color: #fca5a5 !important; cursor: not-allowed !important; }}
            
            .stock-badge {{ background: #334155; color: #38bdf8; padding: 6px 12px; border-radius: 20px; font-size: 12px; display: inline-block; margin-bottom: 15px; font-weight: bold; }}
            .key-box {{ margin-top: 15px; font-size: 14px; color: #4ade80; background: #0b0f19; padding: 12px; border-radius: 8px; border: 1px solid #334155; word-break: break-all; user-select: all; }}
            .history-box {{ margin-top: 15px; text-align: left; background: #0b0f19; padding: 10px; border-radius: 8px; border: 1px solid #334155; max-height: 120px; overflow-y: auto; font-size: 12px; }}
            .note {{ font-size: 11px; color: #ef4444; margin-top: 10px; }}
            .admin-link {{ display: block; margin-top: 15px; font-size: 11px; color: #64748b; text-decoration: none; }}
            .admin-link:hover {{ color: #94a3b8; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h2>🔑 Kho Key Tự Động</h2>
            <div class="stock-badge">📦 Số key sẵn sàng trong kho: {stock_count} Key</div>
            <p style="font-size: 12px; color: #94a3b8;">Bắt buộc phải qua trang vượt link mới được mở khóa lấy key.</p>
            
            {btn_html}
            
            <button id="getKeyBtn" onclick="getKeyFromStock()" disabled>🔒 BƯỚC 2: NHẬN KEY TỪ KHO (CHƯA VƯỢT LINK)</button>
            <div class="note" id="noteText">⚠️ Hãy bấm nút vượt link ở trên trước! Nếu không vượt, nút này sẽ khóa vĩnh viễn.</div>
            
            <div style="text-align: left; margin-top: 20px; font-size: 12px; color: #94a3b8;">Key của bạn vừa rút:</div>
            <div class="key-box" id="keyResult">Chưa có key được rút.</div>

            <div style="text-align: left; margin-top: 15px; font-size: 12px; color: #38bdf8; font-weight: bold;">📜 Lịch sử key đã rút trên máy này:</div>
            <div class="history-box" id="historyList">
                <span style="color: #64748b;">Chưa có lịch sử rút key nào.</span>
            </div>

            <a href="/admin" class="admin-link">⚙️ Quản lý kho (Admin)</a>
        </div>

        <script>
            let isLockedPermanent = false;

            function markTargetClicked() {{
                // Đánh dấu người dùng đã bấm đi vượt link
                localStorage.setItem('ga_clicked_link', 'true');
                localStorage.removeItem('ga_passed_verify');
            }}

            // Khi người dùng rời khỏi trang web sang tab vượt link
            window.addEventListener('blur', function() {{
                if (localStorage.getItem('ga_clicked_link') === 'true') {{
                    // Đã qua trang vượt, đánh dấu đã hoàn thành bước đi tương tác
                    localStorage.setItem('ga_passed_verify', 'true');
                }}
            }});

            // Khi người dùng quay lại trang web
            window.addEventListener('focus', function() {{
                const clicked = localStorage.getItem('ga_clicked_link');
                const passed = localStorage.getItem('ga_passed_verify');

                const btn = document.getElementById('getKeyBtn');
                const note = document.getElementById('noteText');

                if (clicked === 'true' && passed === 'true') {{
                    // Đã vượt link thành công và quay lại -> Mở khóa xanh
                    btn.removeAttribute('disabled');
                    btn.classList.add('active');
                    btn.classList.remove('locked');
                    btn.innerText = "✨ BƯỚC 2: RÚT KEY NGAY TỪ KHO";
                    note.style.color = "#4ade80";
                    note.innerText = "✅ Đã vượt link thành công! Bấm nhận key ngay.";
                }} else if (clicked === 'true' && passed !== 'true') {{
                    // Bấm nhầm hoặc lách luật -> Khóa đơ vĩnh viễn không mở nữa
                    lockPermanently("🚫 Phát hiện gian lận hoặc chưa hoàn thành vượt link! Khóa vĩnh viễn.");
                }}
            }});

            window.addEventListener('DOMContentLoaded', function() {{
                const clicked = localStorage.getItem('ga_clicked_link');
                const passed = localStorage.getItem('ga_passed_verify');
                
                if (clicked === 'true' && passed === 'true') {{
                    const btn = document.getElementById('getKeyBtn');
                    const note = document.getElementById('noteText');
                    btn.removeAttribute('disabled');
                    btn.classList.add('active');
                    btn.innerText = "✨ BƯỚC 2: RÚT KEY NGAY TỪ KHO";
                    note.style.color = "#4ade80";
                    note.innerText = "✅ Đã vượt link thành công! Bấm nhận key ngay.";
                }}
                loadUserHistory();
            }});

            function lockPermanently(reason) {{
                isLockedPermanent = true;
                localStorage.setItem('ga_perm_locked', 'true');
                const btn = document.getElementById('getKeyBtn');
                const note = document.getElementById('noteText');
                
                btn.setAttribute('disabled', 'true');
                btn.classList.remove('active');
                btn.classList.add('locked');
                btn.innerText = "❌ HỆ THỐNG ĐÃ KHÓA VĨNH VIỄN";
                note.style.color = "#ef4444";
                note.innerText = reason;
            }}

            function getKeyFromStock() {{
                if (isLockedPermanent || localStorage.getItem('ga_perm_locked') === 'true') {{
                    alert("Hệ thống đã bị khóa do không vượt link hợp lệ!");
                    return;
                }}

                const passed = localStorage.getItem('ga_passed_verify');
                if (passed !== 'true') {{
                    alert("Bạn chưa vượt link! Nút bấm đang bị khóa.");
                    return;
                }}

                const keyBox = document.getElementById('keyResult');
                keyBox.innerText = "Đang rút key từ kho...";

                fetch('/api/get-key')
                    .then(res => res.json())
                    .then(data => {{
                        if(data.success) {{
                            const fullKeyInfo = data.key + " (Hạn: " + (data.days == 365 ? "Vĩnh viễn" : data.days + " ngày") + ")";
                            keyBox.innerText = fullKeyInfo;
                            
                            saveToUserHistory(fullKeyInfo);
                            
                            alert("Rút key thành công!");
                            localStorage.removeItem('ga_clicked_link');
                            localStorage.removeItem('ga_passed_verify');
                            localStorage.removeItem('ga_perm_locked');
                            location.reload();
                        }} else {{
                            keyBox.innerText = "❌ Lỗi: " + data.message;
                        }}
                    }})
                    .catch(err => {{
                        keyBox.innerText = "❌ Lỗi kết nối máy chủ.";
                    }});
            }}

            function saveToUserHistory(keyStr) {{
                let history = JSON.parse(localStorage.getItem('ga_user_key_history') || '[]');
                history.unshift(keyStr);
                if (history.length > 5) history.pop();
                localStorage.setItem('ga_user_key_history', JSON.stringify(history));
                loadUserHistory();
            }}

            function loadUserHistory() {{
                const historyBox = document.getElementById('historyList');
                let history = JSON.parse(localStorage.getItem('ga_user_key_history') || '[]');
                
                if (history.length === 0) {{
                    historyBox.innerHTML = '<span style="color: #64748b;">Chưa có lịch sử rút key nào.</span>';
                    return;
                }}

                let html = '';
                history.forEach((k, index) => {{
                    html += `<div style="padding: 4px 0; border-bottom: 1px solid #1e293b; color: #4ade80; font-family: monospace;">🔑 ${{(index + 1)}}. ${k}</div>`;
                }});
                historyBox.innerHTML = html;
            }}
        </script>
    </body>
    </html>
    """
    return render_template_string(html_template)

# --- 2. API RÚT KEY TỪ KHO ---
@app.route('/api/get-key')
def api_get_key():
    db = load_db()
    if not db["stock"]:
        return jsonify({"success": False, "message": "Kho đã hết sạch key! Vui lòng đợi Admin nạp thêm."})
    
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

# --- 3. TRANG ADMIN QUẢN LÝ & LỊCH SỬ HỆ THỐNG ---
@app.route('/admin', methods=['GET', 'POST'])
def admin_panel():
    db = load_db()
    message = ""
    
    if request.method == 'POST' and 'password' in request.form and 'keys_input' not in request.form and 'new_link' not in request.form and 'delete_key' not in request.form:
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

    if request.method == 'POST':
        if 'new_link' in request.form:
            new_link = request.form.get('new_link').strip()
            db["current_link"] = new_link
            save_db(db)
            message = "✅ Đã cập nhật Link vượt thành công!"
                
        if 'keys_input' in request.form and request.form.get('keys_input').strip():
            raw_keys = request.form.get('keys_input')
            try:
                days = int(request.form.get('days', 1))
            except:
                days = 1
                
            new_keys = [k.strip() for k in raw_keys.splitlines() if k.strip()]
            for k in new_keys:
                db["stock"].append({"key": k, "days": days})
                
            save_db(db)
            message = f"✅ Đã nạp thành công {len(new_keys)} key vào kho!"

        if 'delete_key' in request.form:
            del_key = request.form.get('delete_key')
            if del_key in db["active"]:
                del db["active"][del_key]
                save_db(db)
                message = f"✅ Đã xóa key '{del_key}' khỏi lịch sử hoạt động!"

    stock_count = len(db["stock"])
    active_count = len(db["active"])
    current_link = db.get("current_link", "")
    
    history_html = ""
    for k, info in list(db["active"].items()):
        time_left = round((info["expires_at"] - time.time()) / 3600, 1)
        status_text = f"Còn hạn ({time_left}h)" if time_left > 0 else "Đã hết hạn"
        status_color = "#4ade80" if time_left > 0 else "#ef4444"
        
        history_html += f"""
        <div style="background: #0b0f19; padding: 10px; border-radius: 8px; margin-top: 8px; display: flex; justify-content: space-between; align-items: center; font-size: 12px;">
            <div>
                <span style="color: #4ade80; font-family: monospace; font-weight: bold;">{k}</span><br>
                <span style="color: {status_color}; font-size: 11px;">⏱️ Hạn: {info['days']} ngày | Trạng thái: {status_text}</span>
            </div>
            <form method="POST" style="margin: 0;">
                <input type="hidden" name="delete_key" value="{k}">
                <button type="submit" style="background: #ef4444; padding: 5px 10px; font-size: 11px; margin: 0; width: auto;">Xóa</button>
            </form>
        </div>
        """
    
    if not history_html:
        history_html = '<div style="color: #64748b; font-size: 12px; text-align: center; margin-top: 10px;">Chưa có key nào được rút từ kho.</div>'

    return render_template_string(f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <title>Quản Lý Kho Key - Admin</title>
        <style>
            body {{ background: #0f172a; color: #f8fafc; font-family: sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }}
            .card {{ background: #1e293b; padding: 25px; border-radius: 16px; width: 100%; max-width: 550px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); box-sizing: border-box; max-height: 90vh; overflow-y: auto; }}
            textarea, input, select {{ width: 100%; padding: 10px; border-radius: 8px; border: 1px solid #334155; background: #0f172a; color: white; box-sizing: border-box; margin-top: 8px; }}
            textarea {{ height: 80px; font-family: monospace; color: #4ade80; }}
            button {{ background: #22c55e; color: white; border: none; padding: 10px; width: 100%; border-radius: 8px; font-weight: bold; cursor: pointer; margin-top: 12px; }}
            button:hover {{ background: #16a34a; }}
            .btn-link-update {{ background: #3b82f6; }}
            .btn-link-update:hover {{ background: #2563eb; }}
            .logout {{ background: #ef4444; margin-top: 15px; }}
            .logout:hover {{ background: #dc2626; }}
            .success {{ color: #4ade80; font-size: 13px; margin-top: 10px; text-align: center; font-weight: bold; }}
            .stat-box {{ display: flex; gap: 10px; margin-bottom: 15px; }}
            .stat {{ flex: 1; background: #0b0f19; padding: 10px; border-radius: 8px; text-align: center; font-size: 13px; color: #38bdf8; font-weight: bold; }}
            .section {{ border-top: 1px solid #334155; margin-top: 20px; padding-top: 15px; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h2>⚙️ Cài Đặt Hệ Thống & Lịch Sử</h2>
            <div class="stat-box">
                <div class="stat">📦 Kho: {stock_count} Key</div>
                <div class="stat">🔑 Đã cấp: {active_count} Key</div>
            </div>
            
            <form method="POST">
                <label style="font-size: 12px; color: #38bdf8; font-weight: bold;">🔗 Link Vượt Hiện Tại:</label>
                <input type="text" name="new_link" value="{current_link}" placeholder="Dán link vượt vào đây...">
                <button type="submit" class="btn-link-update">💾 Lưu Link Vượt</button>
            </form>

            <form method="POST" class="section">
                <label style="font-size: 12px; color: #38bdf8; font-weight: bold;">📥 Nạp Lô Key Mới Vào Kho:</label>
                <label style="font-size: 11px; color: #94a3b8; display: block; margin-top: 6px;">Thời hạn:</label>
                <select name="days">
                    <option value="1">1 Ngày</option>
                    <option value="3">3 Ngày</option>
                    <option value="7">7 Ngày</option>
                    <option value="30">30 Ngày</option>
                    <option value="365">Vĩnh viễn</option>
                </select>
                <label style="font-size: 11px; color: #94a3b8; display: block; margin-top: 6px;">Danh sách Key (mỗi key một dòng):</label>
                <textarea name="keys_input" placeholder="GA-KEY-01&#10;GA-KEY-02"></textarea>
                <button type="submit">➕ Thêm Key Vào Kho</button>
            </form>

            <div class="section">
                <label style="font-size: 12px; color: #38bdf8; font-weight: bold;">📜 Lịch Sử Key Đang Hoạt Động ({active_count}):</label>
                <div style="max-height: 180px; overflow-y: auto; margin-top: 8px;">
                    {history_html}
                </div>
            </div>
            
            <div class="success">{message}</div>

            <form action="/admin/logout" method="POST">
                <button type="submit" class="logout">Đăng Xuất Admin</button>
            </form>
            
            <div style="text-align: center; margin-top: 15px;">
                <a href="/" style="color: #94a3b8; font-size: 12px; text-decoration: none;">← Về trang chủ lấy key</a>
            </div>
        </div>
    </body>
    </html>
    """, stock_count=stock_count, active_count=active_count, current_link=current_link, history_html=history_html, message=message)

@app.route('/admin/logout', methods=['POST'])
def admin_logout():
    session.pop('admin_logged', None)
    return redirect('/admin')

# --- 4. API KIỂM TRA KEY ---
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
