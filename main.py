import os
import threading
from flask import Flask, render_template_string, jsonify, request

app = Flask(__name__)

# Trạng thái game tương tác TikTok Live
live_game_state = {
    "wins": 100,               # Số lượt Win hiện tại
    "is_under_attack": False,  # Trạng thái đang bị tấn công
    "countdown": 0,            # Bộ đếm ngược 10 giây
    "last_action_msg": "Đang chạy chế độ trực tuyến trên Render. Sẵn sàng nhận tương tác!"
}

# Luồng đếm ngược 10 giây khi bị tấn công
def run_countdown():
    global live_game_state
    while live_game_state["countdown"] > 0 and live_game_state["is_under_attack"]:
        import time
        time.sleep(1)
        live_game_state["countdown"] -= 1
    
    if live_game_state["countdown"] <= 0:
        live_game_state["is_under_attack"] = False
        live_game_state["last_action_msg"] = "🛡️ Đã hết thời gian tấn công! Phòng thủ thành công!"

# Giao diện Web Game độc lập thuần túy
@app.route('/')
def index():
    html_template = """
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>TikTok Live Interactive Game</title>
        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap" rel="stylesheet">
        <style>
            body { background-color: #0b0c10; color: white; font-family: 'Poppins', sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
            .game-box { width: 100%; max-width: 420px; background: #151823; border: 2px solid #ff4757; border-radius: 20px; padding: 25px; box-sizing: border-box; text-align: center; box-shadow: 0 15px 35px rgba(255,71,87,0.3); }
            .win-number { font-size: 52px; font-weight: bold; color: #2ed573; margin: 10px 0; text-shadow: 0 0 15px rgba(46,213,115,0.4); }
            .msg-box { background: #12131c; border: 1px solid #232738; padding: 15px; border-radius: 12px; margin-top: 20px; font-size: 14px; min-height: 60px; word-break: break-word; color: #d1d5db; line-height: 1.4; }
            .alert-box { display: none; background: rgba(255,71,87,0.15); border: 1px solid #ff4757; padding: 12px; border-radius: 12px; margin-top: 15px; }
            .alert-title { color: #ff4757; font-weight: bold; font-size: 18px; animation: blink 1s infinite; }
            @keyframes blink { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }
            .timer-num { font-size: 45px; color: #ffa502; font-weight: bold; line-height: 1; margin-top: 5px; }
            .avatar-game { width: 90px; height: 90px; border-radius: 50%; border: 3px solid #ffa502; object-fit: cover; margin-bottom: 10px; }
        </style>
    </head>
    <body>
        <div class="game-box">
            <img src="https://i.ibb.co/Z1Yck7SH/7475196962448704520-avatar-png.png" alt="Avatar" class="avatar-game">
            <h2 style="margin: 0 0 5px 0; color: #ff4757; font-size: 18px;">⚔️ TƯƠNG TÁC TIKTOK LIVE</h2>
            <p style="color: #8f9bb3; font-size: 12px; margin: 0 0 15px 0;">Thả Hoa Hồng = Tăng Win | Quà Khác = Trừ Win (10s)</p>
            
            <span style="font-size: 12px; color: #8f9bb3; font-weight: 600;">SỐ LƯỢT WIN</span>
            <div class="win-number" id="winsDisplay">100</div>

            <div class="alert-box" id="attackSection">
                <div class="alert-title">🚨 ĐANG BỊ TẤN CÔNG!</div>
                <div style="font-size: 11px; color: #ff6b81; margin-top: 4px;">Thời gian phản công:</div>
                <div class="timer-num" id="countdownDisplay">10</div>
            </div>

            <div class="msg-box" id="msgDisplay">
                Đang chờ dữ liệu từ Livestream...
            </div>
        </div>

        <script>
            // Tự động đồng bộ trạng thái từ server mỗi 1 giây
            setInterval(() => {
                fetch('/api/status')
                .then(res => res.json())
                .then(data => {
                    document.getElementById('winsDisplay').innerText = data.wins;
                    document.getElementById('msgDisplay').innerText = data.last_action_msg;
                    
                    let attackSec = document.getElementById('attackSection');
                    if (data.is_under_attack) {
                        attackSec.style.display = 'block';
                        document.getElementById('countdownDisplay').innerText = data.countdown;
                    } else {
                        attackSec.style.display = 'none';
                    }
                })
                .catch(err => console.log("Lỗi tải API:", err));
            }, 1000);
        </script>
    </body>
    </html>
    """
    return render_template_string(html_template)

@app.route('/api/status')
def api_status():
    return jsonify(live_game_state)

# Endpoint nhận dữ liệu quà tặng (Bạn có thể dùng tool như Tasker trên điện thoại, hoặc Extension kết nối TikTok Live để bắn vào đây)
@app.route('/api/webhook', methods=['POST'])
def api_webhook():
    global live_game_state
    data = request.json or {}
    gift_name = data.get("gift_name", "Hoa hồng").lower()
    user_name = data.get("user_name", "Người xem")
    repeat_count = int(data.get("repeat_count", 1))

    if "rose" in gift_name or "hoa hồng" in gift_name:
        live_game_state["wins"] += repeat_count
        live_game_state["is_under_attack"] = False
        live_game_state["countdown"] = 0
        live_game_state["last_action_msg"] = f"💖 {user_name} tặng {repeat_count} {gift_name}! Cộng thẳng {repeat_count} Win!"
    else:
        live_game_state["is_under_attack"] = True
        live_game_state["countdown"] = 10
        penalty = 2 * repeat_count
        live_game_state["wins"] = max(0, live_game_state["wins"] - penalty)
        live_game_state["last_action_msg"] = f"🚨 {user_name} tấn công bằng {gift_name}! Trừ {penalty} Win! Đang đếm ngược 10 giây!"
        
        threading.Thread(target=run_countdown, daemon=True).start()

    return jsonify({"status": "success", "new_wins": live_game_state["wins"]})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
