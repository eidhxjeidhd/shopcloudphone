import os
from flask import Flask, render_template_string, jsonify, request
import cloudscraper
from bs4 import BeautifulSoup

app = Flask(__name__)

# Khởi tạo cloudscraper để vượt qua Cloudflare khi chạy trên server mây
scraper = cloudscraper.create_scraper()

@app.route('/')
def index():
    html_template = """
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Zefoy Cloud Web App - TikTok Buff</title>
        <style>
            body { background: #0f172a; color: #f8fafc; font-family: sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }
            .card { background: #1e293b; padding: 25px; border-radius: 16px; width: 100%; max-width: 450px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); text-align: center; }
            input, select { width: 100%; padding: 12px; margin: 8px 0; background: #0f172a; border: 1px solid #334155; color: white; border-radius: 8px; box-sizing: border-box; }
            button { background: #22c55e; color: white; border: none; padding: 12px; width: 100%; border-radius: 8px; font-weight: bold; cursor: pointer; margin-top: 10px; }
            button:hover { background: #16a34a; }
            .status { margin-top: 15px; font-size: 13px; color: #38bdf8; background: #0f172a; padding: 10px; border-radius: 8px; border: 1px solid #334155; text-align: left; }
        </style>
    </head>
    <body>
        <div class="card">
            <h2>🚀 TikTok Web Buff (Zefoy)</h2>
            <p style="font-size: 12px; color: #94a3b8;">Hệ thống chạy hoàn toàn tự động trên Cloud</p>
            
            <div style="text-align: left; margin-top: 10px;">
                <label style="font-size: 12px; color: #94a3b8;">Chọn dịch vụ:</label>
                <select id="serviceSelect">
                    <option value="">-- Đang tải danh sách từ server --</option>
                </select>
            </div>

            <div style="text-align: left; margin-top: 10px;">
                <label style="font-size: 12px; color: #94a3b8;">Link Video TikTok:</label>
                <input type="text" id="videoUrl" placeholder="https://www.tiktok.com/@...">
            </div>

            <button onclick="startBuff()">Bắt đầu Gửi Yêu Cầu</button>
            
            <div class="status" id="statusBox">Trạng thái: Sẵn sàng kết nối...</div>
        </div>

        <script>
            // Tự động tải danh sách dịch vụ khi mở web
            window.onload = function() {
                fetch('/api/get-services')
                    .then(res => res.json())
                    .then(data => {
                        let select = document.getElementById('serviceSelect');
                        select.innerHTML = "";
                        if(data.success) {
                            for(let [key, val] of Object.entries(data.services)) {
                                let opt = document.createElement('option');
                                opt.value = key;
                                opt.text = `${val.name} (${val.status})`;
                                if(!val.active) opt.disabled = true;
                                select.appendChild(opt);
                            }
                            document.getElementById('statusBox').innerText = "Trạng thái: Đã đồng bộ dịch vụ từ Zefoy!";
                        } else {
                            document.getElementById('statusBox').innerText = "Trạng thái: Không thể kết nối đến Zefoy.";
                        }
                    });
            };

            function startBuff() {
                const service = document.getElementById('serviceSelect').value;
                const url = document.getElementById('videoUrl').value;
                if(!service || !url) { alert('Vui lòng chọn dịch vụ và nhập link video!'); return; }

                document.getElementById('statusBox').innerText = "Trạng thái: Đang gửi yêu cầu lên hệ thống...";
                
                fetch(`/api/run-buff?service=${encodeURIComponent(service)}&url=${encodeURIComponent(url)}`)
                    .then(res => res.json())
                    .then(data => {
                        document.getElementById('statusBox').innerText = "Trạng thái: " + data.message;
                    });
            }
        </script>
    </body>
    </html>
    """
    return render_template_string(html_template)

@app.route('/api/get-services')
def get_services():
    try:
        # Dùng cloudscraper để lấy nội dung trang Zefoy vượt qua Cloudflare trên server
        response = scraper.get('https://zefoy.com/', timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            services = {}
            
            # Quét các thẻ chứa dịch vụ trên trang
            cards = soup.select('div.col-sm-3.col-xs-12, div.t-card')
            for index, card in enumerate(cards):
                title_elem = card.find('h5')
                btn_elem = card.find('button')
                if title_elem and btn_elem:
                    name = title_elem.text.strip()
                    btn_text = btn_elem.text.strip().lower()
                    
                    # Kiểm tra trạng thái bảo trì hoặc hoạt động
                    if "soon" in btn_text or "update" in btn_text:
                        services[str(index)] = {"name": name, "status": "Đang bảo trì 🛑", "active": False}
                    else:
                        services[str(index)] = {"name": name, "status": "Hoạt động ✅", "active": True}
            
            return jsonify({"success": True, "services": services})
        else:
            return jsonify({"success": False, "error": "Lỗi kết nối trang mục tiêu"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/run-buff')
def run_buff():
    service_id = request.args.get('service')
    video_url = request.args.get('url')
    
    # Xử lý logic gửi yêu cầu buff tương ứng với service_id tại đây
    return jsonify({"success": True, "message": f"Đã tiếp nhận link cho dịch vụ ID {service_id}. Đang tiến hành xử lý ngầm!"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
