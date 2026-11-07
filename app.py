import os
import requests
from flask import Flask, render_template_string, jsonify, request

app = Flask(__name__)

@app.route('/')
def index():
    html_template = """
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>TikTok Live - Dự Báo Thời Tiết Chi Tiết</title>
        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap" rel="stylesheet">
        <style>
            body { background-color: #0b0c10; color: white; font-family: 'Poppins', sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; overflow: hidden; }
            .game-container { width: 100%; max-width: 440px; background: #151823; border: 2px solid #2ed573; border-radius: 24px; padding: 25px; box-sizing: border-box; text-align: center; box-shadow: 0 20px 40px rgba(46,213,115,0.2); z-index: 10; position: relative; }
            .avatar-box { width: 85px; height: 85px; border-radius: 50%; border: 3px solid #2ed573; object-fit: cover; margin: 0 auto 10px auto; display: block; box-shadow: 0 0 15px rgba(46,213,115,0.4); }
            .title { color: #2ed573; font-size: 18px; font-weight: 700; margin: 0 0 5px 0; text-transform: uppercase; }
            .subtitle { color: #8f9bb3; font-size: 11px; margin: 0 0 15px 0; }
            .search-box { display: flex; gap: 8px; margin-bottom: 12px; }
            .search-input { flex: 1; background: #12131c; border: 1px solid #232738; padding: 10px 12px; border-radius: 10px; color: white; font-size: 13px; outline: none; }
            .search-input:focus { border-color: #2ed573; }
            .search-btn { background: #2ed573; border: none; color: white; padding: 0 12px; border-radius: 10px; font-weight: bold; cursor: pointer; transition: 0.2s; }
            .search-btn:hover { background: #26af5f; }
            .gps-btn { background: #ffa502; border: none; color: #12131c; padding: 8px 12px; border-radius: 10px; font-weight: bold; cursor: pointer; width: 100%; margin-bottom: 15px; font-size: 12px; }
            .gps-btn:hover { background: #ffb143; }
            .win-label { font-size: 11px; color: #8f9bb3; font-weight: 600; letter-spacing: 1px; }
            .win-number { font-size: 48px; font-weight: bold; color: #ffa502; margin: 5px 0; text-shadow: 0 0 20px rgba(255,165,2,0.4); }
            .alert-box { background: rgba(46,213,115,0.1); border: 1px solid #2ed573; padding: 10px; border-radius: 14px; margin-top: 15px; text-align: left; }
            .alert-title { color: #2ed573; font-weight: bold; font-size: 14px; margin-bottom: 4px; }
            .msg-box { background: #12131c; border: 1px solid #232738; padding: 12px 15px; border-radius: 12px; margin-top: 12px; font-size: 13px; word-break: break-word; color: #d1d5db; line-height: 1.4; display: flex; align-items: center; justify-content: space-between; }
        </style>
    </head>
    <body>
        <div class="game-container">
            <img src="https://i.ibb.co/Z1Yck7SH/7475196962448704520-avatar-png.png" alt="Avatar" class="avatar-box">
            <div class="title">🛰️ DỰ BÁO THỜI TIẾT CHI TIẾT</div>
            <div class="subtitle">Quét vị trí GPS & Phân tích trạng thái Nắng, Mưa, Dông chuẩn xác</div>
            
            <button class="gps-btn" onclick="getGPSLocation()">📍 Quét khu vực hiện tại của tôi</button>

            <div class="search-box">
                <input type="text" id="cityInput" class="search-input" placeholder="Hoặc nhập tên thành phố..." value="Hanoi">
                <button class="search-btn" onclick="getWeather()">Xem</button>
            </div>
            
            <div class="win-label" id="locationLabel">NHIỆT ĐỘ KHU VỰC</div>
            <div class="win-number" id="tempDisplay">--°C</div>
            <div class="alert-box" id="infoSection">
                <div class="alert-title" id="descDisplay">Trạng thái: Nhấn nút quét GPS phía trên</div>
                <div style="font-size: 11px; color: #8f9bb3;" id="feelsLikeDisplay">Cảm giác thực tế: --°C</div>
            </div>
            <div class="msg-box">
                <div>💧 Độ ẩm: <strong id="humidityDisplay" style="color:#ffa502">--%</strong></div>
                <div>💨 Gió: <strong id="windDisplay" style="color:#ffa502">-- km/h</strong></div>
            </div>
        </div>
        <script>
            function fetchWeather(query) {
                fetch(`/api/weather?q=${encodeURIComponent(query)}`)
                    .then(res => res.json())
                    .then(data => {
                        if(data.success) {
                            document.getElementById('locationLabel').innerText = `TẠI ${data.city.toUpperCase()}`;
                            document.getElementById('tempDisplay').innerText = `${data.temperature}°C`;
                            document.getElementById('descDisplay').innerText = data.weather_status;
                            document.getElementById('feelsLikeDisplay').innerText = `🌡️ Cảm giác như: ${data.feels_like}°C`;
                            document.getElementById('humidityDisplay').innerText = `${data.humidity}%`;
                            document.getElementById('windDisplay').innerText = `${data.wind_speed} km/h`;
                        } else {
                            alert(data.error || "Không tìm thấy địa điểm!");
                        }
                    })
                    .catch(err => console.log("Lỗi tải thời tiết:", err));
            }

            function getWeather() {
                const city = document.getElementById('cityInput').value.trim();
                if(city) fetchWeather(city);
            }

            function getGPSLocation() {
                if (navigator.geolocation) {
                    document.getElementById('descDisplay').innerText = "🛰️ Đang quét vị trí GPS của bạn...";
                    navigator.geolocation.getCurrentPosition(
                        (position) => {
                            const lat = position.coords.latitude;
                            const lon = position.coords.longitude;
                            fetchWeather(`${lat},${lon}`);
                        },
                        (error) => {
                            alert("Không thể quét vị trí. Vui lòng cấp quyền vị trí hoặc nhập thủ công!");
                            document.getElementById('descDisplay').innerText = "⚠️ Không thể lấy vị trí GPS.";
                        }
                    );
                } else {
                    alert("Trình duyệt không hỗ trợ định vị GPS.");
                }
            }

            window.onload = () => { getGPSLocation(); };
        </script>
    </body>
    </html>
    """
    return render_template_string(html_template)

@app.route('/api/weather')
def api_weather():
    query = request.args.get('q', 'Hanoi')
    url = f"https://wttr.in/{query}?format=j1"
    try:
        headers = {'User-Agent': 'curl/7.68.0'}
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            current = data['current_condition'][0]
            area_name = data.get('nearest_area', [{}])[0].get('areaName', [{}])[0].get('value', query)
            
            # Lấy mã code thời tiết từ wttr.in để dịch chi tiết dạng Nắng / Mưa / Dông
            weather_code = str(current.get('weatherCode', ''))
            desc_en = current['weatherDesc'][0]['value'].lower()
            
            # Bộ từ điển chuyển đổi trạng thái tiếng Việt chi tiết 100%
            status_vn = f"🌤️ {current['weatherDesc'][0]['value']}"
            
            if "sun" in desc_en or "clear" in desc_en or weather_code in ['113']:
                status_vn = "☀️ Trời Nắng Ráo, Quang Mây"
            elif "thunder" in desc_en or "storm" in desc_en or weather_code in ['386', '389', '392', '395']:
                status_vn = "⚡ Cảnh Báo: Có Mưa Dông, Sấm Sét!"
            elif "heavy rain" in desc_en or weather_code in ['302', '305', '308', '359']:
                status_vn = "🌧️ Trời Đang Có Mưa Rất To!"
            elif "rain" in desc_en or "shower" in desc_en or weather_code in ['293', '296', '299', '305', '353', '356']:
                status_vn = "🌦️ Trời Đang Có Mưa, Mưa Rào Nhỏ"
            elif "cloud" in desc_en or "overcast" in desc_en or weather_code in ['116', '119', '122']:
                status_vn = "☁️ Trời Nhiều Mây, Dịu Mát"
            elif "fog" in desc_en or "mist" in desc_en or weather_code in ['143', '248', '260']:
                status_vn = "🌫️ Sương Mù Dày Đặc, Hạn Chế Tầm Nhìn"

            return jsonify({
                "success": True,
                "city": area_name,
                "temperature": current['temp_C'],
                "feels_like": current['FeelsLikeC'],
                "humidity": current['humidity'],
                "weather_status": status_vn,
                "wind_speed": current['windspeedKmph']
            })
        else:
            return jsonify({"success": False, "error": "Không thể lấy dữ liệu thời tiết khu vực này!"})
    except Exception as e:
        return jsonify({"success": False, "error": f"Lỗi hệ thống: {str(e)}"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
