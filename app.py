import time
import threading
from flask import Flask, render_template_string, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)

# Biến toàn cục lưu trạng thái tool
bot_status = "Đang tắt"
driver = None
bot_thread = None

def run_zefoy_automation(video_url):
    global bot_status, driver
    try:
        bot_status = "Đang khởi động trình duyệt..."
        options = webdriver.ChromeOptions()
        # Nếu chạy trên máy tính, bạn có thể comment dòng headless lại để thấy cửa sổ trình duyệt giải captcha
        # options.add_argument("--headless") 
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get("https://zefoy.com/")
        
        bot_status = "⚠️ HÃY TỰ GIẢI CAPTCHA TRÊN TRÌNH DUYỆT ĐANG MỞ!"
        
        # Chờ người dùng tự vượt qua Captcha (kiểm tra khi nào vào được trang chính của Zefoy - có ô nhập link)
        while True:
            try:
                # Zefoy thường có ô input chứa placeholder "Enter Video URL" hoặc class tương tự sau khi đăng nhập captcha
                input_box = driver.find_element(By.XPATH, "//input[contains(@placeholder, 'Enter Video URL')]")
                if input_box:
                    break
            except:
                pass
            time.sleep(2)
            
        bot_status = "Đã vượt Captcha! Đang tiến hành buff..."
        time.sleep(2)
        
        # Nhập link video cần buff
        input_box = driver.find_element(By.XPATH, "//input[contains(@placeholder, 'Enter Video URL')]")
        input_box.clear()
        input_box.send_keys(video_url)
        time.sleep(1)
        
        # Click nút tìm kiếm video (Search)
        search_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Search')]")
        search_btn.click()
        
        bot_status = "Đã tìm thấy video, đang chờ nút gửi tim/view..."
        time.sleep(3)
        
        # Vòng lặp tự động bấm buff (Hearts / Views) liên tục mỗi khi hết thời gian chờ (cooldown)
        while True:
            try:
                # Tìm nút gửi tim (Send hearts) hoặc views tùy ý bạn chọn
                send_hearts_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Send hearts')]")
                if send_hearts_btn.is_enabled():
                    send_hearts_btn.click()
                    bot_status = "🎉 Đã buff thành công một lượt! Đang chờ cooldown..."
                else:
                    bot_status = "⏳ Đang trong thời gian chờ (Cooldown) của Zefoy..."
            except Exception as e:
                bot_status = f"Đang xử lý hoặc chờ lượt tiếp theo... ({str(e)[:30]})"
            
            time.sleep(10)
            
    except Exception as e:
        bot_status = f"Lỗi: {str(e)}"
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

@app.route('/')
def index():
    html_template = """
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Zefoy Auto Buff - TikTok</title>
        <style>
            body { background: #0f172a; color: #f8fafc; font-family: sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
            .card { background: #1e293b; padding: 30px; border-radius: 16px; width: 100%; max-width: 400px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); text-align: center; }
            input { width: 100%; padding: 12px; margin: 10px 0; background: #0f172a; border: 1px solid #334155; color: white; border-radius: 8px; box-sizing: border-box; }
            button { background: #22c55e; color: white; border: none; padding: 12px; width: 100%; border-radius: 8px; font-weight: bold; cursor: pointer; margin-top: 10px; }
            button:hover { background: #16a34a; }
            .status { margin-top: 20px; font-size: 14px; color: #38bdf8; background: #0f172a; padding: 10px; border-radius: 8px; border: 1px solid #334155; }
        </style>
    </head>
    <body>
        <div class="card">
            <h2>🤖 Zefoy Auto Buff TikTok</h2>
            <p style="font-size: 12px; color: #94a3b8;">Nhập link video TikTok của bạn bên dưới</p>
            <input type="text" id="videoUrl" placeholder="https://www.tiktok.com/@user/video/...">
            <button onclick="startBot()">Bắt đầu Chạy Tool</button>
            <div class="status" id="statusBox">Trạng thái: Đang chờ lệnh...</div>
        </div>

        <script>
            function startBot() {
                const url = document.getElementById('videoUrl').value;
                if(!url) { alert('Vui lòng nhập link video!'); return; }
                
                fetch('/start?url=' + encodeURIComponent(url))
                    .then(res => res.json())
                    .then(data => { alert(data.message); });
            }

            setInterval(() => {
                fetch('/status')
                    .then(res => res.json())
                    .then(data => {
                        document.getElementById('statusBox').innerText = "Trạng thái: " + data.status;
                    });
            }, 2000);
        </script>
    </body>
    </html>
    """
    return render_template_string(html_template)

@app.route('/start')
def start():
    global bot_thread, bot_status
    video_url = request.args.get('url')
    
    if bot_thread and bot_thread.is_alive():
        return jsonify({"message": "Tool đang chạy rồi!"})
        
    bot_thread = threading.Thread(target=run_zefoy_automation, args=(video_url,))
    bot_thread.daemon = True
    bot_thread.start()
    
    return jsonify({"message": "Đã khởi động tool! Hãy nhìn vào màn hình trình duyệt để giải Captcha."})

@app.route('/status')
def status():
    return jsonify({"status": bot_status})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
