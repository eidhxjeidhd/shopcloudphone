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
        <title>TikTok Live - Dự Báo Thời Tiết Giọng Nói AI</title>
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
            .gps-btn { background: #ffa502; border: none; color: #12131c; padding: 8px 12px; border-radius: 10px; font-weight: bold; cursor: pointer; width: 100%; margin-bottom: 10px; font-size: 12px; }
            .gps-btn:hover { background: #ffb143; }
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
            <div class="subtitle">Quét vị trí GPS • Dự báo theo khung giờ • Giọng đọc AI</div>
            
            <button class="gps-btn" onclick="getGPSLocation()">📍 Quét khu vực hiện tại của tôi</button>
            <button class="voice-btn" onclick="speakWeather()">🔊 Nghe AI đọc bản tin thời tiết</button>

            <div class="search-box">
                <input type="text" id="cityInput" class="search-input" placeholder="Hoặc nhập tên thành phố..." value="Hanoi">
                <button class="search-btn" onclick="getWeather()">Xem</button>
            </div>
            
            <div class="win-label" id="locationLabel">NHIỆT ĐỘ KHU VỰC</div>
            <div class="win-number" id="tempDisplay">--°C</div>
            <div class="alert-box" id="infoSection">
                <div class="alert-title" id="descDisplay">Trạng thái: Đang chờ quét GPS...</div>
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
                            
                            // Hiển thị dự báo theo khung giờ
                            let hourlyHtml = "<b>⏰ Dự báo theo khung giờ:</b><br>";
                            data.hourly.forEach(h => {
                                hourlyHtml += `• ${h.time}: ${h.temp}°C - ${h.desc}<br>`;
                            });
                            document.getElementById('hourlyDisplay').innerHTML = hourlyHtml;

                            // Chuẩn bị nội dung cho AI đọc
                            lastSpokenText = `Xin chào! Dữ liệu thời tiết tại ${data.city} hiện tại là ${data.temperature độ C}, trạng thái ${data.weather_status}. Cảm giác thực tế là ${data.feels_like độ C}. Độ ẩm ${data.humidity phần trăm}.`;
                            
                            // Tự động đọc luôn khi có dữ liệu mới
                            speakWeather();
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
                    document.getElementById('descDisplay').innerText = "🛰️ Đang quét vị trí GPS...";
                    navigator.geolocation.getCurrentPosition(
                        (position) => {
                            const lat = position.coords.latitude;
                            const lon = position.coords.longitude;
                            fetchWeather(`${lat},${lon}`);
                        },
                        (error) => {
                            alert("Không thể quét vị trí GPS. Hãy nhập thủ công!");
                            document.getElementById('descDisplay').innerText = "⚠️ Không thể lấy GPS.";
                        }
                    );
                } else {
                    alert("Trình duyệt không hỗ trợ định vị GPS.");
                }
            }

            // Hàm kích hoạt giọng nói AI (Text-to-Speech)
            function speakWeather() {
                if (!lastSpokenText) {
                    alert("Chưa có dữ liệu thời tiết để đọc!");
                    return;
                }
                if ('speechSynthesis' in window) {
                    window.speechSynthesis.cancel(); // Dừng giọng đọc cũ nếu đang đọc dở
                    let utterance = new SpeechSynthesisUtterance(lastSpokenText);
                    utterance.lang = 'vi-VN'; // Chọn ngôn ngữ Tiếng Việt chuẩn
                    utterance.rate = 1.0;     // Tốc độ đọc
                    utterance.pitch = 1.0;    // Tông giọng
                    window.speechSynthesis.speak(utterance);
                } else {
                    alert("Trình duyệt của bạn không hỗ trợ tính năng đọc giọng nói AI.");
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
            
            weather_code = str(current.get('weatherCode', ''))
            desc_en = current['weatherDesc'][0]['value'].lower()
            
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
                status_vn = "🌫️ Sương Mù Dày Đặc"

            # Lấy danh sách dự báo theo các khung giờ trong ngày (ví dụ: Sáng, Trưa, Chiều, Tối)
            hourly_list = []
            today_weather = data.get('weather', [])[0].get('hourly', [])
            # Lọc lấy một số mốc giờ tiêu biểu trong ngày (00:00, 06:00, 12:00, 18:00...)
            for item in today_weather:
                time_str = item.get('time', '0').zfill(4)
                formatted_time = f"{time_str[:2]}:00"
                temp_c = item.get('tempC', '')
                desc_text = item.get('weatherDesc', [{}])[0].get('value', '')
                
                # Việt hóa mô tả theo giờ đơn giản
                desc_vn_hourly = "Nắng/Đẹp"
                d_lower = desc_text.lower()
                if "rain" in d_lower or "shower" in d_lower:
                    desc_vn_hourly = "Có mưa"
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
                "hourly": hourly_list[:6] # Lấy 6 mốc giờ chính trong ngày
            })
        else:
            return jsonify({"success": False, "error": "Không thể lấy dữ liệu thời tiết khu vực này!"})
    except Exception as e:
        return jsonify({"success": False, "error": f"Lỗi hệ thống: {str(e)}"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
