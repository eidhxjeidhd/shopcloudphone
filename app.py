import time
import threading
from flask import Flask, render_template_string, jsonify, request
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)

bot_status = "Đang chờ khởi động..."
services_list = {}
driver = None
bot_thread = None
selected_service_url = None
target_video_url = ""

def run_zefoy_bot():
    global bot_status, driver, services_list, selected_service_url, target_video_url
    try:
        bot_status = "Đang khởi động trình duyệt..."
        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get("https://zefoy.com/")
        
        bot_status = "⚠️ HÃY TỰ GIẢI CAPTCHA TRÊN TRÌNH DUYỆT!"
        
        # Chờ người dùng tự vượt Captcha (khi xuất hiện các ô dịch vụ trên trang chính)
        while True:
            try:
                # Zefoy thường chứa các thẻ chứa dịch vụ (ví dụ các nút chọn Views, Hearts, Followers...)
                elements = driver.find_elements(By.CSSSelector, "h5.card-title")
                if len(elements) > 0:
                    break
            except:
                pass
            time.sleep(2)
            
        bot_status = "Đã vượt Captcha thành công! Đang quét trạng thái các dịch vụ..."
        time.sleep(2)
        
        # Quét danh sách dịch vụ và trạng thái (Hoạt động / Bảo trì)
        while True:
            try:
                services_list = {}
                cards = driver.find_elements(By.CSSSelector, "div.col-sm-3.col-xs-12, div.t-card")
                for card in cards:
                    try:
                        title_elem = card.find_element(By.TAG_NAME, "h5")
                        btn_elem = card.find_element(By.TAG_NAME, "button")
                        name = title_elem.text.strip()
                        btn_text = btn_elem.text.strip().lower()
                        
                        # Kiểm tra xem có đang bảo trì hay không (thường Zefoy ghi 'Soon', 'Update' hoặc nút bị disable)
                        if "soon" in btn_text or "update" in btn_text or not btn_elem.is_enabled():
                            services_list[name] = {"status": "Đang bảo trì 🛑", "active": False}
                        else:
                            services_list[name] = {"status": "Hoạt động ✅", "active": True}
                    except:
                        continue
                if services_list:
                    break
            except:
                pass
            time.sleep(2)

        bot_status = "✅ Đã quét xong! Vui lòng chọn dịch vụ và nhập link trên web."
        
        # Chờ người dùng chọn dịch vụ và nhập link video từ giao diện web
        while not selected_service_url or not target_video_url:
            time.sleep(1)
            
        bot_status = f"Đang truy cập vào dịch vụ đã chọn..."
        driver.get(selected_service_url)
        time.sleep(2)
        
        # Nhập link video và bắt đầu vòng lặp auto buff
        while True:
            try:
                input_box = driver.find_element(By.XPATH, "//input[contains(@placeholder, 'Enter Video URL')]")
                input_box.clear()
                input_box.send_keys(target_video_url)
                time.sleep(1)
                
                search_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Search')]")
                search_btn.click()
                time.sleep(3)
                
                # Vòng lặp gửi yêu cầu liên tục theo thời gian cooldown
                while True:
                    try:
                        send_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Send') or contains(text(), 'Submit')]")
                        if send_btn.is_enabled():
                            send_btn.click()
                            bot_status = "🎉 Đã buff thành công một lượt! Đang chờ cooldown..."
                            time.sleep(5)
                        else:
                            # Đọc thời gian cooldown nếu có
                            bot_status = "⏳ Đang trong thời gian chờ (Cooldown) của Zefoy..."
                    except:
                        bot_status = "Đang xử lý lượt tiếp theo..."
                    time.sleep(10)
            except Exception as e:
                bot_status = f"Lỗi vòng lặp buff: {str(e)}"
                time.sleep(5)

    except Exception as e:
        bot_status = f"Lỗi hệ thống: {str(e)}"

@app.route('/')
def index():
    html_template = """
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Zefoy Smart Tool</title>
        <style>
            body { background: #0f172a; color: #f8fafc; font-family: sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }
            .card { background: #1e293b; padding: 25px; border-radius: 16px; width: 100%; max-width: 450px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); text-align: center; }
            input, select { width: 100%; padding: 12px; margin: 8px 0; background: #0f172a; border: 1px solid #334155; color: white; border-radius: 8px; box-sizing: border-box; }
            button { background: #22c55e; color: white; border: none; padding: 12px; width: 100%; border-radius: 8px; font-weight: bold; cursor: pointer; margin-top: 10px; }
            button:hover { background: #16a34a; }
            .status { margin-top: 15px; font-size: 13px; color: #38bdf8; background: #0f172a; padding: 10px; border-radius: 8px; border: 1px solid #334155; text-align: left; }
            .service-item { display: flex; justify-content: space-between; padding: 5px 0; font-size: 13px; border-bottom: 1px solid #334155; }
        </style>
    </head>
    <body>
        <div class="card">
            <h2>🤖 Zefoy Auto Master</h2>
            <button onclick="startBot()">1. Khởi động Trình duyệt & Giải Captcha</button>
            
            <div style="margin-top: 15px; text-align: left;">
                <label style="font-size: 12px; color: #94a3b8;">Chọn dịch vụ:</label>
                <select id="serviceSelect">
                    <option value="">-- Đang chờ quét danh sách --</option>
                </select>
            </div>

            <div style="text-align: left; margin-top: 10px;">
                <label style="font-size: 12px; color: #94a3b8;">Link Video TikTok:</label>
                <input type="text" id="videoUrl" placeholder="https://www.tiktok.com/@...">
            </div>

            <button style="background: #3b82f6;" onclick="confirmConfig()">2. Xác nhận & Bắt đầu Auto Buff</button>
            
            <div class="status" id="statusBox">Trạng thái: Chưa chạy.</div>
        </div>

        <script>
            function startBot() {
                fetch('/start').then(res => res.json()).then(data => alert(data.message));
            }

            function confirmConfig() {
                const service = document.getElementById('serviceSelect').value;
                const url = document.getElementById('videoUrl').value;
                if(!service || !url) { alert('Vui lòng chọn dịch vụ và điền link!'); return; }
                
                fetch(`/config?service=${encodeURIComponent(service)}&url=${encodeURIComponent(url)}`)
                    .then(res => res.json())
                    .then(data => alert(data.message));
            }

            setInterval(() => {
                fetch('/status')
                    .then(res => res.json())
                    .then(data => {
                        document.getElementById('statusBox').innerText = "Trạng thái: " + data.status;
                        
                        let select = document.getElementById('serviceSelect');
                        if(Object.keys(data.services).length > 0 && select.options.length <= 1) {
                            select.innerHTML = "";
                            for(let [name, info] of Object.entries(data.services)) {
                                let opt = document.createElement('option');
                                opt.value = name;
                                opt.text = `${name} (${info.status})`;
                                if(!info.active) opt.disabled = true;
                                select.appendChild(opt);
                            }
                        }
                    });
            }, 2000);
        </script>
    </body>
    </html>
    """
    return render_template_string(html_template)

@app.route('/start')
def start():
    global bot_thread
    if bot_thread and bot_thread.is_alive():
        return jsonify({"message": "Tool đã chạy rồi!"})
    bot_thread = threading.Thread(target=run_zefoy_bot)
    bot_thread.daemon = True
    bot_thread.start()
    return jsonify({"message": "Đã bật trình duyệt! Hãy nhìn màn hình để giải Captcha."})

@app.route('/config')
def config():
    global target_video_url, selected_service_url, driver
    target_video_url = request.args.get('url')
    service_name = request.args.get('service')
    
    # Tìm đường dẫn URL tương ứng với dịch vụ người dùng chọn trên trang
    try:
        cards = driver.find_elements(By.CSSSelector, "div.col-sm-3.col-xs-12, div.t-card")
        for card in cards:
            if service_name in card.text:
                btn = card.find_element(By.TAG_NAME, "button")
                # Zefoy thường dùng hàm javascript hoặc form submit để chuyển trang dịch vụ
                driver.execute_script("arguments[0].click();", btn)
                selected_service_url = driver.current_url
                break
    except Exception as e:
        return jsonify({"message": f"Lỗi chọn dịch vụ: {str(e)}"})
        
    return jsonify({"message": "Đã nhận cấu hình! Tool bắt đầu tự động cày."})

@app.route('/status')
def status():
    return jsonify({"status": bot_status, "services": services_list})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
