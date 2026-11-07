import os
import requests
from flask import Flask, render_template_string, jsonify, request

app = Flask(__name__)

# Cấu hình API thời tiết (Bạn có thể thay đổi API key miễn phí từ openweathermap.org)
OPENWEATHER_API_KEY = "1df1c2d3e4f5a6b7c8d9e0f1a2b3c4d5" # Khuyên bạn nên đổi sang API key của riêng mình

@app.route('/')
def index():
    html_template = """
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>TikTok Live - Dự Báo Thời Tiết Siêu Chuẩn</title>
        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap" rel="stylesheet">
        <style>
            body { background-color: #0b0c10; color: white; font-family: 'Poppins', sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; overflow: hidden; }
            .game-container { width: 100%; max-width: 440px; background: #151823; border: 2px solid #2ed573; border-radius: 24px; padding: 25px; box-sizing: border-box; text-align: center; box-shadow: 0 20px 40px rgba(46,213,115,0.2); z-index: 10; position: relative; }
            .avatar-box { width: 85px; height: 85px; border-radius: 50%; border: 3px solid #2ed573; object-fit: cover; margin: 0 auto 10px auto; display: block; box-shadow: 0 0 15px rgba(46,213,115,0.4); }
            .title { color: #2ed573; font-size: 18px; font-weight: 700; margin: 0 0 5px 0; text-transform: uppercase; }
            .subtitle { color: #8f9bb3; font-size: 11px; margin: 0 0 15px 0; }
            
            /* Khu vực tìm kiếm */
            .search-box { display: flex; gap: 8px; margin-bottom: 15px; }
            .search-input { flex: 1; background: #12131c; border: 1px solid #232738; padding: 10px 12px; border-radius: 10px; color: white; font-size: 13px; outline: none; }
            .search-input:focus { border-color: #2ed573; }
            .search-btn { background: #2ed573; border: none; color: white; padding: 0 15px; border-radius: 10px; font-weight: bold; cursor: pointer; transition: 0.2s; }
            .search-btn:hover { background: #26af5f; }

            .win-label { font-size: 11px; color: #8f9bb3; font-weight: 600; letter-spacing: 1px; }
            .win-number { font-size: 48px; font-weight: bold; color: #ffa502; margin: 5px 0; text-shadow: 0 0 20px rgba(255,165,2,0.4); }
            
            .alert-box { background: rgba(46,213,115,0.1); border: 1px solid #2ed573; padding: 10px; border-radius: 14px; margin-top: 15px; text-align: left; }
            .alert-title { color: #2ed573; font-weight: bold; font-size: 13px; margin-bottom: 4px; }
            
            .msg-box { background: #12131c; border: 1px solid #232738; padding: 12px 15px; border-radius: 12px; margin-top: 12px; font-size: 13px; word-break: break-word; color: #d1d5db; line-height: 1.4; display: flex; align-items: center; justify-content: space-between; }
        </style>
    </head>
    <body>
        <div class="game-container">
            <img src="https://i.ibb.co/Z1Yck7SH/7475196962448704520-avatar-png.png" alt="Avatar" class="avatar-box">
            <div class="title">🌤️ THỜI TIẾT THỜI GIAN THỰC</div>
            <div class="subtitle">Tra cứu dữ liệu khí tượng chuẩn xác theo khu vực</div>
            
            <!-- Form tra cứu -->
            <div class="search-box">
                <input type="text" id="cityInput" class="search-input" placeholder="Nhập tên thành phố (VD: Hanoi, Ho Chi Minh)..." value="Hanoi">
                <button class="search-btn" onclick="getWeather()">Xem</button>
            </div>

            <div class="win-label" id="locationLabel">NHIỆT ĐỘ TẠI HANOI</div>
            <div class="win-number" id="tempDisplay">--°C</div>
            
            <div class="alert-box" id="infoSection">
                <div class="alert-title" id="descDisplay">Trạng thái: Đang cập nhật...</div>
                <div style="font-size: 11px; color: #8f9bb3;" id="feelsLikeDisplay">Cảm giác thực tế: --°C</div>
            </div>

            <div class="msg-box">
                <div>💧 Độ ẩm: <strong id="humidityDisplay" style="color:#ffa502">--%</strong></div>
                <div>💨 Gió: <strong id="windDisplay" style="color:#ffa502">-- m/s</strong></div>
            </div>
        </div>

        <script>
            function getWeather() {
                const city = document.getElementById('cityInput').value.trim();
                if(!city) return;

                fetch(`/api/weather?city=${encodeURIComponent(city)}`)
                    .then(res => res.json())
                    .then(data => {
                        if(data.success) {
                            document.getElementById('locationLabel').innerText = `NHIỆT ĐỘ TẠI ${data.city.toUpperCase()}, ${data.country}`;
                            document.getElementById('tempDisplay').innerText = `${data.temperature}°C`;
                            document.getElementById('descDisplay').innerText = `☁️ Mô tả: ${data.description}`;
                            document.getElementById('feelsLikeDisplay').innerText = `🌡️ Cảm giác như: ${data.feels_like}°C`;
                            document.getElementById('humidityDisplay').innerText = `${data.humidity}%`;
                            document.getElementById('windDisplay').innerText = `${data.wind_speed} m/s`;
                        } else {
                            alert(data.error || "Không tìm thấy địa điểm!");
                        }
                    })
                    .catch(err => console.log("Lỗi tải thời tiết:", err));
            }

            // Tự động load thời tiết Hà Nội khi mở web
            window.onload = () => { getWeather(); };
        </script>
    </body>
    </html>
    """
    return render_template_string(html_template)

@app.route('/api/weather')
def api_weather():
    city = request.args.get('city', 'Hanoi')
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric&lang=vi"
    
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return jsonify({
                "success": True,
                "city": data["name"],
                "country": data["sys"]["country"],
                "temperature": round(data["main"]["temp"], 1),
                "feels_like": round(data["main"]["feels_like"], 1),
                "humidity": data["main"]["humidity"],
                "description": data["weather"][0]["description"].capitalize(),
                "wind_speed": data["wind"]["speed"]
            })
        else:
            return jsonify({"success": False, "error": "Không tìm thấy tên thành phố hoặc lỗi API!"})
    except Exception as e:
        return jsonify({"success": False, "error": f"Lỗi kết nối: {str(e)}"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
 app.run(host='0.0.0.0', port=port, debug=False)
