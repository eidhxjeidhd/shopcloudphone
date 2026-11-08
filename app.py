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
        <title>Bacon Link Bypass</title>
        <style>
            body { background: #0f172a; color: #f8fafc; font-family: sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }
            .card { background: #1e293b; padding: 25px; border-radius: 16px; width: 100%; max-width: 480px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); box-sizing: border-box; }
            input { width: 100%; padding: 12px; margin: 8px 0; background: #0f172a; border: 1px solid #334155; color: white; border-radius: 8px; box-sizing: border-box; outline: none; }
            input:focus { border-color: #22c55e; }
            button { background: #22c55e; color: white; border: none; padding: 12px; width: 100%; border-radius: 8px; font-weight: bold; cursor: pointer; margin-top: 10px; transition: 0.2s; }
            button:hover { background: #16a34a; }
            .result-box { margin-top: 15px; font-size: 13px; color: #38bdf8; background: #0b0f19; padding: 12px; border-radius: 8px; border: 1px solid #334155; word-break: break-all; text-align: left; }
        </style>
    </head>
    <body>
        <div class="card">
            <h2 style="text-align: center; margin-top: 0;">🔗 Bacon Link Bypass</h2>
            <p style="font-size: 12px; color: #94a3b8; text-align: center;">Hệ thống bóc tách link qua BaconBypass</p>
            
            <div style="text-align: left; margin-top: 10px;">
                <label style="font-size: 12px; color: #94a3b8;">Nhập Link Rút Gọn Cần Bypass:</label>
                <input type="text" id="targetUrl" placeholder="https://...">
            </div>

            <button onclick="bypassLink()">Tiến Hành Bypass</button>
            
            <div style="text-align: left; margin-top: 15px; font-size: 12px; color: #94a3b8;">Kết quả nhận được:</div>
            <div class="result-box" id="resultBox">Chưa có link nào được xử lý.</div>
        </div>

        <script>
            function bypassLink() {
                const url = document.getElementById('targetUrl').value;
                if(!url) { alert('Vui lòng nhập link cần bypass!'); return; }

                const resultBox = document.getElementById('resultBox');
                resultBox.innerText = "Đang kết nối tới BaconBypass để bóc tách...";

                fetch(`/api/bypass?url=${encodeURIComponent(url)}`)
                    .then(res => res.json())
                    .then(data => {
                        if(data.success) {
                            resultBox.innerHTML = `✅ Link gốc thành công: <br><a href="${data.result}" target="_blank" style="color: #4ade80;">${data.result}</a>`;
                        } else {
                            resultBox.innerText = "❌ Lỗi: " + data.message;
                        }
                    })
                    .catch(err => {
                        resultBox.innerText = "❌ Lỗi kết nối đến máy chủ.";
                    });
            }
        </script>
    </body>
    </html>
    """
    return render_template_string(html_template)

@app.route('/api/bypass')
def api_bypass():
    target_url = request.args.get('url')
    if not target_url:
        return jsonify({"success": False, "message": "Thiếu đường dẫn URL!"})
    
    try:
        # Đường dẫn API endpoint của baconbypass.xyz
        api_endpoint = f"https://baconbypass.xyz/api?url={target_url}"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json"
        }
        
        response = requests.get(api_endpoint, headers=headers, timeout=20)
        
        if response.status_code == 200:
            try:
                data = response.json()
                # Lấy kết quả trả về từ các trường phổ biến của API
                final_link = data.get("result") or data.get("url") or data.get("destination") or data.get("link")
                
                if final_link:
                    return jsonify({"success": True, "result": final_link})
                else:
                    return jsonify({"success": True, "result": response.text})
            except:
                # Nếu phản hồi trả về dạng text thô không phải JSON
                return jsonify({"success": True, "result": response.text.strip()})
        else:
            return jsonify({"success": False, "message": f"Lỗi từ server BaconBypass (Mã: {response.status_code})"})
            
    except Exception as e:
        return jsonify({"success": False, "message": f"Lỗi kết nối: {str(e)}"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
