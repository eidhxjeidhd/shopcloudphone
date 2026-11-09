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
        with open(DB_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, dict):
                return {"stock": [], "active": {}, "current_link": ""}
            if "stock" not in data: data["stock"] = []
            if "active" not in data: data["active"] = {}
            if "current_link" not in data: data["current_link"] = ""
            return data
    except Exception:
        return {"stock": [], "active": {}, "current_link": ""}

def save_db(data):
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print("Lỗi lưu DB:", e)

# --- 1. GIAO DIỆN CHÍNH CHO NGƯỜI DÙNG & NHẬN KEY ---
@app.route('/')
def home():
    try:
        db = load_db()
        stock_count = len(db.get("stock", []))
        current_link = db.get("current_link", "")
        
        if not current_link:
            btn_html = '<div style="background: #334155; color: #ef4444; padding: 12px; border-radius: 8px; font-weight: bold; margin-top: 15px; font-size: 13px;">⚠️ Admin chưa thiết lập Link vượt key!</div>'
        else:
            btn_html = f'<a href="{current_link}" target="_blank" id="linkBtn" class="btn-link" onclick="markTargetClicked()">🔗 MỞ TRANG VƯỢT LINK (LẤY KEY)</a>'

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
                .btn-link {{ background: #3b82f6; text-decoration: none; display: block; padding: 14px; border-radius: 8px; font-weight: bold; color: white; margin-top: 15px; box-sizing: border-box; transition: 0.2s; }}
                .btn-link:hover {{ background: #2563eb; }}
                
                .stock-badge {{ background: #334155; color: #38bdf8; padding: 6px 12px; border-radius: 20px; font-size: 12px; display: inline-block; margin-bottom: 15px; font-weight: bold; }}
                .key-box {{ margin-top: 15px; background: #0b0f19; padding: 15px; border-radius: 8px; border: 1px solid #22c55e; display: none; }}
                .note {{ font-size: 11px; color: #94a3b8; margin-top: 12px; line-height: 1.4; }}
                .admin-link {{ display: block; margin-top: 15px; font-size: 11px; color: #64748b; text-decoration: none; }}
                .admin-link:hover {{ color: #94a3b8; }}
            </style>
        </head>
        <body>
            <div class="card" id="mainCard">
                <h2>🔑 Lấy Key Hệ Thống</h2>
                <div class="stock-badge">📦 Kho sẵn sàng: {stock_count} Key</div>
                <p style="font-size: 12px; color: #94a3b8;">Bấm vào nút bên dưới để sang trang trạm trung gian lấy Key.</p>
                
                <div id="actionContainer">
                    {btn_html}
                </div>

                <div class="key-box" id="keyResultBox">
                    <div style="font-size: 12px; color: #4ade80; font-weight: bold; margin-bottom: 5px;">🎉 Key của bạn đây:</div>
                    <input type="text" id="obtainedKey" readonly style="width: 100%; padding: 8px; background: #1e293b; border: 1px solid #334155; color: #fff; text-align: center; font-family: monospace; border-radius: 6px; box-sizing: border-box;">
                    <button onclick="copyKey()" style="background: #22c55e; color: white; border: none; padding: 8px; width: 100%; border-radius: 6px; font-weight: bold; cursor: pointer; margin-top: 8px;">📋 SAO CHÉP KEY</button>
                </div>

                <div class="note" id="noteText">⚠️ <b>Lưu ý:</b> Sau khi bấm mở link, hãy thực hiện hoàn tất trạm trung gian rồi quay lại đây để nhận key!</div>

                <a href="/admin" class="admin-link">⚙️ Quản lý kho (Admin)</a>
            </div>

            <script>
                function markTargetClicked() {{
                    localStorage.setItem('ga_clicked_link', 'true');
                    localStorage.removeItem('ga_passed_verify');
                }}

                window.addEventListener('blur', function() {{
                    if (localStorage.getItem('ga_clicked_link') === 'true') {{
                        localStorage.setItem('ga_passed_verify', 'true');
                    }}
                }});

                window.addEventListener('focus', function() {{
                    const clicked = localStorage.getItem('ga_clicked_link');
                    const passed = localStorage.getItem('ga_passed_verify');

                    if (clicked === 'true' && passed === 'true') {{
                        // Đã đi qua link vượt và quay lại -> Gọi API lấy key từ kho
                        fetch('/api/get-key')
                            .then(res => res.json())
                            .then(data => {{
                                if (data.success) {{
                                    document.getElementById('actionContainer').style.display = 'none';
                                    const box = document.getElementById('keyResultBox');
                                    box.style.display = 'block';
                                    document.getElementById('obtainedKey').value = data.key;
                                    localStorage.removeItem('ga_clicked_link');
                                    localStorage.removeItem('ga_passed_verify');
                                }}
                            }});
                    }}
                }});

                function copyKey() {{
                    const copyText = document.getElementById("obtainedKey");
                    copyText.select();
                    document.execCommand("copy");
                    alert("Đã copy key: " + copyText.value);
                }}
            </script>
        </body>
        </html>
        """
        return render_template_string(html_template)
    except Exception as e:
        return f"Lỗi giao diện: {str(e)}", 500

# --- 2. API TỰ ĐỘNG BỐC KEY TỪ KHO KHI HOÀN THÀNH VƯỢT LINK ---
@app.route('/api/get-key')
def api_get_key():
    db = load_db()
    stock = db.get("stock", [])
    
    if not stock:
        return jsonify({"success": False, "message": "Kho đã hết key! Vui lòng báo Admin nạp thêm."})
    
    # Lấy key đầu tiên trong kho ra
    item = stock.pop(0)
    key_val = item["key"]
    days = item.get("days", 1)
    
    # Tính thời gian hết hạn
    expires_at = time.time() + (days * 86400)
    
    # Chuyển vào danh sách active để game check hợp lệ
    if "active" not in db: db["active"] = {}
    db["active"][key_val] = {
        "expires_at": expires_at,
        "days": days,
        "banned": False
    }
    
    save_db(db)
    return jsonify({"success": True, "key": key_val})

# --- 3. API KIỂM TRA KEY CHO GAME (HỖ TRỢ TỰ ĐỘNG BỐC NẾU CẦN) ---
@app.route('/api/check-key')
def api_check_key():
    try:
        key_input = request.args.get('key')
        if not key_input:
            return jsonify({"success": False, "message": "Thiếu thông tin Key!"})
        
        db = load_db()
        active_dict = db.get("active", {})
        
        # Trường hợp 1: Key đã được kích hoạt và nằm trong active
        if key_input in active_dict:
            key_data = active_dict[key_input]
            
            if key_data.get("banned", False):
                return jsonify({"success": False, "status": "banned", "message": "Key này đã bị Admin khóa vĩnh viễn!"})
                
            if time.time() < key_data.get("expires_at", 0):
                return jsonify({"success": True, "status": "valid", "message": "Key hợp lệ!"})
            else:
                return jsonify({"success": False, "status": "expired", "message": "Key đã hết hạn!"})
                
        # Trường hợp 2: Key vẫn đang nằm trong KHO (nếu người chơi nhập trực tiếp key trong kho) -> Tự động kích hoạt luôn
        stock_list = db.get("stock", [])
        for item in stock_list:
            if item["key"] == key_input:
                stock_list.remove(item)
                days = item.get("days", 1)
                expires_at = time.time() + (days * 86400)
                
                active_dict[key_input] = {
                    "expires_at": expires_at,
                    "days": days,
                    "banned": False
                }
                save_db(db)
                return jsonify({"success": True, "status": "valid", "message": "Kích hoạt và xác nhận key thành công!"})

        return jsonify({"success": False, "status": "invalid", "message": "Key sai hoặc không tồn tại trong hệ thống!"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Lỗi server: {str(e)}"})

# --- 4. TRANG ADMIN QUẢN LÝ ---
@app.route('/admin', methods=['GET', 'POST'])
def admin_panel():
    try:
        db = load_db()
        message = ""
        
        if request.method == 'POST' and 'password' in request.form and 'keys_input' not in request.form and 'new_link' not in request.form and 'delete_key' not in request.form and 'toggle_ban' not in request.form:
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
                db["current_link"] = request.form.get('new_link', '').strip()
                save_db(db)
                message = "✅ Đã cập nhật Link vượt thành công!"
                    
            if 'keys_input' in request.form and request.form.get('keys_input').strip():
                raw_keys = request.form.get('keys_input')
                try:
                    days = int(request.form.get('days', 1))
                except:
                    days = 1
                    
                new_keys = [k.strip() for k in raw_keys.splitlines() if k.strip()]
                if "stock" not in db: db["stock"] = []
                for k in new_keys:
                    db["stock"].append({"key": k, "days": days})
                    
                save_db(db)
                message = f"✅ Đã nạp thành công {len(new_keys)} key vào kho!"

            if 'toggle_ban' in request.form:
                target_key = request.form.get('toggle_ban')
                if "active" in db and target_key in db["active"]:
                    current_status = db["active"][target_key].get("banned", False)
                    db["active"][target_key]["banned"] = not current_status
                    save_db(db)
                    message = f"✅ Đã đổi trạng thái key '{target_key}'!"

            if 'delete_key' in request.form:
                del_key = request.form.get('delete_key')
                if "active" in db and del_key in db["active"]:
                    del db["active"][del_key]
                    save_db(db)
                    message = f"✅ Đã xóa key '{del_key}'!"

        stock_count = len(db.get("stock", []))
        active_dict = db.get("active", {})
        active_count = len(active_dict)
        current_link = db.get("current_link", "")
        
        history_html = ""
        for k, info in list(active_dict.items()):
            try:
                time_left = round((info.get("expires_at", 0) - time.time()) / 3600, 1)
                is_banned = info.get("banned", False)
                status_text = "🚫 ĐÃ KHÓA" if is_banned else (f"Còn hạn ({time_left}h)" if time_left > 0 else "Hết hạn")
                status_color = "#ef4444" if is_banned or time_left <= 0 else "#4ade80"
                ban_btn_text = "Mở Khóa" if is_banned else "Khóa"
                d_val = info.get('days', 1)
            except:
                status_text = "Lỗi"
                status_color = "#ef4444"
                ban_btn_text = "Khóa"
                d_val = 1
            
            history_html += f"""
            <div style="background: #0b0f19; padding: 10px; border-radius: 8px; margin-top: 8px; display: flex; justify-content: space-between; align-items: center; font-size: 12px;">
                <div>
                    <span style="color: #4ade80; font-family: monospace; font-weight: bold;">{k}</span><br>
                    <span style="color: {status_color}; font-size: 11px;">⏱️ Hạn: {d_val} ngày | {status_text}</span>
                </div>
                <div style="display: flex; gap: 5px;">
                    <form method="POST" style="margin: 0;">
                        <input type="hidden" name="toggle_ban" value="{k}">
                        <button type="submit" style="background: #eab308; color: #0f172a; padding: 5px 8px; font-size: 11px; margin: 0; width: auto; font-weight: bold; cursor: pointer;">{ban_btn_text}</button>
                    </form>
                    <form method="POST" style="margin: 0;">
                        <input type="hidden" name="delete_key" value="{k}">
                        <button type="submit" style="background: #ef4444; color: white; padding: 5px 8px; font-size: 11px; margin: 0; width: auto; font-weight: bold; cursor: pointer;">Xóa</button>
                    </form>
                </div>
            </div>
            """
        
        if not history_html:
            history_html = '<div style="color: #64748b; font-size: 12px; text-align: center; margin-top: 10px;">Chưa có key hoạt động.</div>'

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
                .btn-link-update {{ background: #3b82f6; }}
                .logout {{ background: #ef4444; margin-top: 15px; }}
                .success {{ color: #4ade80; font-size: 13px; margin-top: 10px; text-align: center; font-weight: bold; }}
                .stat-box {{ display: flex; gap: 10px; margin-bottom: 15px; }}
                .stat {{ flex: 1; background: #0b0f19; padding: 10px; border-radius: 8px; text-align: center; font-size: 13px; color: #38bdf8; font-weight: bold; }}
                .section {{ border-top: 1px solid #334155; margin-top: 20px; padding-top: 15px; }}
            </style>
        </head>
        <body>
            <div class="card">
                <h2>⚙️ Quản Lý Kho Key</h2>
                <div class="stat-box">
                    <div class="stat">📦 Kho: {stock_count} Key</div>
                    <div class="stat">🔑 Hoạt động: {active_count} Key</div>
                </div>
                
                <form method="POST">
                    <label style="font-size: 12px; color: #38bdf8; font-weight: bold;">🔗 Link Vượt:</label>
                    <input type="text" name="new_link" value="{current_link}" placeholder="Dán link vào đây...">
                    <button type="submit" class="btn-link-update">💾 Lưu Link Vượt</button>
                </form>

                <form method="POST" class="section">
                    <label style="font-size: 12px; color: #38bdf8; font-weight: bold;">📥 Nạp Key Vào Kho:</label>
                    <select name="days">
                        <option value="1">1 Ngày</option>
                        <option value="3">3 Ngày</option>
                        <option value="7">7 Ngày</option>
                        <option value="30">30 Ngày</option>
                    </select>
                    <textarea name="keys_input" placeholder="GA-KEY-01&#10;GA-KEY-02"></textarea>
                    <button type="submit">➕ Thêm Key Vào Kho</button>
                </form>

                <div class="section">
                    <label style="font-size: 12px; color: #38bdf8; font-weight: bold;">📜 Key Đang Hoạt Động ({active_count}):</label>
                    <div style="max-height: 180px; overflow-y: auto; margin-top: 8px;">
                        {history_html}
                    </div>
                </div>
                
                <div class="success">{message}</div>

                <form action="/admin/logout" method="POST">
                    <button type="submit" class="logout">Đăng Xuất Admin</button>
                </form>
                
                <div style="text-align: center; margin-top: 15px;">
                    <a href="/" style="color: #94a3b8; font-size: 12px; text-decoration: none;">← Về trang chủ</a>
                </div>
            </div>
        </body>
        </html>
        """, stock_count=stock_count, active_count=active_count, current_link=current_link, history_html=history_html, message=message)
    except Exception as e:
        return f"Lỗi Admin: {str(e)}", 500

@app.route('/admin/logout', methods=['POST'])
def admin_logout():
    session.pop('admin_logged', None)
    return redirect('/admin')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
