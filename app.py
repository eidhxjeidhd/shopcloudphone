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
        <title>TikTok Live - Dự Báo Thời Tiết Chuẩn Xác</title>
        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap" rel="stylesheet">
        <style>
            body { background-color: #0b0c10; color: white; font-family: 'Poppins', sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }
            .game-container { width: 100%; max-width: 440px; background: #151823; border: 2px solid #2ed573; border-radius: 24px; padding: 20px; box-sizing: border-box; text-align: center; box-shadow: 0 20px 40px rgba(46,213,115,0.2); position: relative; margin: 20px 0; }
            .avatar-box { width: 75px; height: 75px; border-radius: 50%; border: 3px solid #2ed573; object-fit: cover; margin: 0 auto 10px auto; display: block; box-shadow: 0 0 15px rgba(46,213,115,0.4); }
            .title { color: #2ed573; font-size: 17px; font-weight: 700; margin: 0 0 3px 0; text-transform: uppercase; }
            .subtitle { color: #8f9bb3; font-size: 11px; margin: 0 0 12px 0; }
            .search-box { display: flex; gap: 8px; margin-bottom: 10px; }
            .search-input { flex: 1; background: #12131c; border: 1px solid #232738; padding: 10px 12px; border-radius: 10px; color: white; font-size: 13px; outline: none; }
            .search-input:focus { border-color: #2ed573; }
            .search-btn { background: #2ed573; border: none; color: white; padding: 0 12px; border-radius: 10px; font-weight: bold; cursor: pointer; transition: 0.2s; }
            .search-btn:hover { background: #26af5f; }
            .voice-btn { background: #3b82f6; border: none; color: white; padding: 8px 12px; border-radius: 10px; font-weight: bold; cursor: pointer; width: 100%; margin-bottom: 12px; font-size: 12px; }
            .voice-btn:hover { background: #2563eb; }
            .win-label { font-size: 11px; color: #8f9bb3; font-weight: 600; letter-spacing: 1px; }
            .win-number { font-size: 42px; font-weight: bold; color: #ffa502; margin: 2px 0; text-shadow: 0 0 20px rgba(255,165,2,0.4); }
            .alert-box { background: rgba(46,213,115,0.1); border: 1px solid #2ed573; padding: 10px; border-radius: 14px; margin-top: 10px; text-align: left; }
            .alert-title { color: #2ed573; font-weight: bold; font-size: 13px; margin-bottom: 4px; }
            .msg-box { background: #12131c; border: 1px solid #232738; padding: 10px 12px; border-radius: 12px; margin-top: 10px; font-size: 12px; word-break: break-word; color: #d1d5db; line-height: 1.4; text-align: left; max-height: 130px; overflow-y: auto; }
        </style>
    </head>
    <body>
        <div class="game-container">
            <img src="https://i.ibb.co/Z1Yck7SH/7475196962448704520-avatar-png.png" alt="Avatar" class="avatar-box">
            <div class="title">🎙️ AI PHÁT THANH VIÊN THỜI TIẾT</div>
            <div class="subtitle">Tra cứu chuẩn dấu • Dự báo theo giờ • Giọng đọc AI</div>
            
            <button class="voice-btn" onclick="speakWeather()">🔊 Nghe AI đọc bản tin thời tiết</button>

            <div class="search-box">
                <input type="text" id="cityInput" class="search-input" placeholder="Nhập tên khu vực (VD: Hào Nam, Hà Nội)..." value="Hào Nam">
                <button class="search-btn" onclick="getWeather()">Xem</button>
            </div>
            
            <div class="win-label" id="locationLabel">NHIỆT ĐỘ KHU VỰC</div>
            <div class="win-number" id="tempDisplay">--°C</div>
            <div class="alert-box" id="infoSection">
                <div class="alert-title" id="descDisplay">Trạng thái: Đang tải...</div>
                <div style="font-size: 11px; color: #8f9bb3;" id="feelsLikeDisplay">Cảm giác thực tế: --°C</div>
            </div>
            
            <div class="msg-box" id="hourlyDisplay">
                ⏳ Đang tải lịch trình dự báo theo giờ...
            </div>
        </div>

        <script>
            let lastSpokenText = "";

            function fetchWeather(query) {
                fetch(`/api/weather?q=${encodeURIComponent(query)}`)
                    .then(res => res.json())
                    .then(data => {
                        if(data.success) {
                            document.getElementById('locationLabel').innerText = `TẠI ${data.city.toUpperCase()}`;
                            document.getElementById('tempDisplay').innerText = `${data.temperature}°C`;
                            document.getElementById('descDisplay').innerText = data.weather_status;
                            document.getElementById('feelsLikeDisplay').innerText = `🌡️ Cảm giác như: ${data.feels_like}°C | 💧 Độ ẩm: ${data.humidity}%`;
                            
                            let hourlyHtml = "<b>⏰ Dự báo theo khung giờ:</b><br>";
                            data.hourly.forEach(h => {
                                hourlyHtml += `• ${h.time}: ${h.temp}°C - ${h.desc}<br>`;
                            });
                            document.getElementById('hourlyDisplay').innerHTML = hourlyHtml;

                            lastSpokenText = `Xin chào các bạn! Dữ liệu thời tiết tại khu vực ${data.city} hiện tại là ${data.temperature} độ C, với trạng thái ${data.weather_status}. Cảm giác thực tế ngoài trời là ${data.feels_like} độ C, độ ẩm khoảng ${data.humidity} phần trăm. Chúc các bạn có một ngày làm việc và học tập hiệu quả!`;
                        } else {
                            alert("Không tìm thấy địa điểm!");
                        }
                    })
                    .catch(err => console.log("Lỗi:", err));
            }

            function getWeather() {
                const city = document.getElementById('cityInput').value.trim();
                if(city) fetchWeather(city);
            }

            function speakWeather() {
                if (!lastSpokenText) {
                    alert("Đang tải dữ liệu, vui lòng đợi giây lát!");
                    return;
                }
                if ('speechSynthesis' in window) {
                    window.speechSynthesis.cancel();
                    let utterance = new SpeechSynthesisUtterance(lastSpokenText);
                    utterance.lang = 'vi-VN';
                    utterance.rate = 1.0;
                    utterance.pitch = 1.0;
                    window.speechSynthesis.speak(utterance);
                } else {
                    alert("Trình duyệt không hỗ trợ giọng đọc AI.");
                }
            }

            // Mặc định load luôn Hào Nam chuẩn chỉnh ngay khi mở web
            window.onload = () => { fetchWeather('Hào Nam'); };
        </script>
    </body>
    </html>
    """
    return render_template_string(html_template)

@app.route('/api/weather')
def api_weather():
    query = request.args.get('q', 'Hào Nam')
    url = f"https://wttr.in/{query}?format=j1"
    try:
        headers = {'User-Agent': 'curl/7.68.0'}
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            current = data['current_condition'][0]
            
            # Lấy chính xác tên do người dùng nhập hoặc trả về tên chuẩn có dấu
            area_name = query.strip()
            if area_name.lower() in ["hanoi", "ha noi"]:
                area_name = "Hà Nội"

            weather_code = str(current.get('weatherCode', ''))
            desc_en = current['weatherDesc'][0]['value'].lower()
            
            status_vn = f"Trời Nắng Ráo, Quang Mây"
            if "sun" in desc_en or "clear" in desc_en or weather_code in ['113']:
                status_vn = "Trời Nắng Ráo, Quang Mây"
            elif "thunder" in desc_en or "storm" in desc_en or weather_code in ['386', '389', '392', '395']:
                status_vn = "Có Mưa Dông, Sấm Sét"
            elif "heavy rain" in desc_en or weather_code in ['302', '305', '308', '359']:
                status_vn = "Trời Đang Mưa Rất To"
            elif "rain" in desc_en or "shower" in desc_en or weather_code in ['293', '296', '299', '305', '353', '356']:
                status_vn = "Trời Đang Có Mưa Rào Nhỏ"
            elif "cloud" in desc_en or "overcast" in desc_en or weather_code in ['116', '119', '122']:
                status_vn = "Trời Nhiều Mây, Dịu Mát"
            elif "fog" in desc_en or "mist" in desc_en or weather_code in ['143', '248', '260']:
                status_vn = "Sương Mù Dày Đặc"

            hourly_list = []
            today_weather = data.get('weather', [])[0].get('hourly', [])
            for item in today_weather:
                time_str = item.get('time', '0').zfill(4)
                formatted_time = f"{time_str[:2]}:00"
                temp_c = item.get('tempC', '')
                desc_text = item.get('weatherDesc', [{}])[0].get('value', '')
                
                desc_vn_hourly = "Trời nắng đẹp"
                d_lower = desc_text.lower()
                if "rain" in d_lower or "shower" in d_lower:
                    desc_vn_hourly = "Có mưa rào"
                elif "cloud" in d_lower:
                    desc_vn_hourly = "Nhiều mây"
                elif "sun" in d_lower or "clear" in d_lower:
                    desc_vn_hourly = "Trời nắng"

                hourly_list.append({
                    "time": formatted_time,
                    "temp": temp_c,
                    "desc": desc_vn_hourly
                })

            return jsonify({
                "success": True,
                "city": area_name,
                "temperature": current['temp_C'],
                "feels_like": current['FeelsLikeC'],
                "humidity": current['humidity'],
                "weather_status": status_vn,
                "wind_speed": current['windspeedKmph'],
                "hourly": hourly_list[:6]
            })
        else:
            return jsonify({"success": False, "error": "Lỗi dữ liệu"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
