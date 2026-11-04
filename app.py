import os
import threading
import time
from flask import Flask, render_template_string, jsonify
from TikTokLive import TikTokLiveClient
from TikTokLive.types.events import GiftEvent

app = Flask(__name__)

# Trạng thái game sinh tồn tương tác TikTok Live
live_game_state = {
    "wins": 500,                   # Số lượt Win khởi điểm
    "is_under_attack": False,      # Trạng thái bị tấn công
    "countdown": 0,                # Bộ đếm ngược 10 giây
    "last_attacker": "Hệ thống",
    "last_gift": "Chưa có",
    "last_action_msg": "🎮 Đang kết nối trực tiếp vào TikTok Live. Sẵn sàng chiến đấu!",
    "animation_trigger": 0,        # Hiệu ứng bay trên web
    "game_status": "RUNNING"       # Trạng thái game: RUNNING hoặc OFF_LIVE
}

# Kết nối TikTok Live kênh @idollatao
tiktok_client = TikTokLiveClient(unique_id="@idollatao")

@tiktok_client.on(GiftEvent)
async def on_tiktok_gift(event: GiftEvent):
    global live_game_state
    
    if live_game_state["game_status"] == "OFF_LIVE":
        return

    try:
        user_name = "Người xem bí ẩn"
        if hasattr(event, 'user') and event.user:
            user_name = getattr(event.user, 'nickname', None) or getattr(event.user, 'unique_id', 'Người xem bí ẩn')

        gift_name = "Món quà"
        repeat_count = 1
        
        if hasattr(event, 'gift') and event.gift:
            gift_name = getattr(event.gift, 'name', 'Món quà')
        
        if hasattr(event, 'repeat_count') and event.repeat_count:
            repeat_count = int(event.repeat_count)

        gift_lower = str(gift_name).lower()

        # NẾU LÀ QUÀ CON HỔ -> NGƯỜI TỐT XUẤT HIỆN -> OFF LIVE CHIẾN THẮNG!
        if "tiger" in gift_lower or "hổ" in gift_lower:
            live_game_state["game_status"] = "OFF_LIVE"
            live_game_state["is_under_attack"] = False
            live_game_state["last_attacker"] = user_name
            live_game_state["last_gift"] = f"{gift_name} (x{repeat_count})"
            live_game_state["last_action_msg"] = f"🐅 {user_name} (Người tốt) thả QUÀ CON HỔ! OFF LIVE chiến thắng rực rỡ!"
            live_game_state["animation_trigger"] += 1
            return

        # CÁC QUÀ KHÁC (KHÁCH QUẬY) -> TRỪ ĐIỂM WIN
        penalty = 5 * repeat_count  
        live_game_state["wins"] = max(0, live_game_state["wins"] - penalty)
        live_game_state["is_under_attack"] = True
        live_game_state["countdown"] = 10
        live_game_state["last_attacker"] = user_name
        live_game_state["last_gift"] = f"{gift_name} (x{repeat_count})"
        live_game_state["last_action_msg"] = f"🚨 {user_name} quậy phá bằng {gift_name} (x{repeat_count})! Trừ {penalty} Win!"
        live_game_state["animation_trigger"] += 1  
        
        threading.Thread(target=run_countdown, daemon=True).start()
    except Exception as e:
        print(f"Lỗi xử lý quà: {e}")

def run_countdown():
    global live_game_state
    while live_game_state["countdown"] > 0 and live_game_state["is_under_attack"] and live_game_state["game_status"] == "RUNNING":
        time.sleep(1)
        live_game_state["countdown"] -= 1
    
    if live_game_state["countdown"] <= 0 and live_game_state["game_status"] == "RUNNING":
        live_game_state["is_under_attack"] = False
        live_game_state["last_action_msg"] = "🛡️ Đã chống đỡ thành công đợt phá phách! Tiếp tục chiến đấu!"

def start_tiktok_listener():
    while True:
        try:
            print("Đang kết nối vào TikTok Live...")
            tiktok_client.run()
        except Exception as e:
            print(f"Mất kết nối TikTok Live: {e}. Thử lại sau 5 giây...")
            time.sleep(5)

@app.route('/')
def index():
    html_template = """
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>TikTok Live Survival Game</title>
        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap" rel="stylesheet">
        <style>
            body { background-color: #0b0c10; color: white; font-family: 'Poppins', sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; overflow: hidden; }
            .game-container { width: 100%; max-width: 440px; background: #151823; border: 2px solid #2ed573; border-radius: 24px; padding: 25px; box-sizing: border-box; text-align: center; box-shadow: 0 20px 40px rgba(46,213,115,0.2); z-index: 10; position: relative; }
            .avatar-box { width: 85px; height: 85px; border-radius: 50%; border: 3px solid #2ed573; object-fit: cover; margin: 0 auto 10px auto; display: block; box-shadow: 0 0 15px rgba(46,213,115,0.4); }
            .title { color: #2ed573; font-size: 18px; font-weight: 700; margin: 0 0 5px 0; text-transform: uppercase; }
            .subtitle { color: #8f9bb3; font-size: 11px; margin: 0 0 15px 0; }
            .win-label { font-size: 11px; color: #8f9bb3; font-weight: 600; letter-spacing: 1px; }
            .win-number { font-size: 56px; font-weight: bold; color: #ffa502; margin: 5px 0; text-shadow: 0 0 20px rgba(255,165,2,0.4); }
            .alert-box { display: none; background: rgba(255,71,87,0.15); border: 1px solid #ff4757; padding: 12px; border-radius: 14px; margin-top: 15px; }
            .alert-title { color: #ff4757; font-weight: bold; font-size: 16px; animation: pulse 0.8s infinite; }
            @keyframes pulse { 0% { opacity: 1; transform: scale(1); } 50% { opacity: 0.5; transform: scale(0.98); } 100% { opacity: 1; transform: scale(1); } }
            .timer-num { font-size: 40px; color: #ffa502; font-weight: bold; line-height: 1; margin-top: 4px; }
            .msg-box { background: #12131c; border: 1px solid #232738; padding: 12px 15px; border-radius: 12px; margin-top: 15px; font-size: 13px; min-height: 55px; word-break: break-word; color: #d1d5db; line-height: 1.4; display: flex; align-items: center; justify-content: center; }
            #offLiveOverlay { display: none; position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(11, 12, 16, 0.95); border-radius: 24px; z-index: 100; flex-direction: column; justify-content: center; align-items: center; }
            .flying-item { position: absolute; bottom: -80px; left: 50%; transform: translateX(-50%); font-size: 45px; z-index: 99; pointer-events: none; display: none; }
            @keyframes flyUpItem { 0% { bottom: -80px; opacity: 1; transform: translateX(-50%) scale(0.8) rotate(0deg); } 50% { transform: translateX(-30%) scale(1.3) rotate(15deg); } 100% { bottom: 105vh; opacity: 0; transform: translateX(-70%) scale(1) rotate(-15deg); } }
            .animate-item { display: block; animation: flyUpItem 2s ease-in-out forwards; }
        </style>
    </head>
    <body>
        <div class="flying-item" id="flyingItem">🐅</div>
        <div class="game-container">
            <div id="offLiveOverlay">
                <div style="font-size: 60px; margin-bottom: 10px;">🐅🎉</div>
                <h2 style="color: #2ed573; margin: 0 0 10px 0; font-size: 22px;">NGƯỜI TỐT CỨU THẾ! OFF LIVE!</h2>
                <p style="color: #d1d5db; font-size: 13px; padding: 0 20px; text-align: center;" id="offLiveMsg">Nhận được Quà Hổ, kết thúc phiên chơi an toàn và chiến thắng!</p>
                <button onclick="location.reload()" style="margin-top: 15px; background: #2ed573; border: none; color: white; padding: 10px 20px; border-radius: 10px; font-weight: bold; cursor: pointer;">Chơi Tiếp</button>
            </div>
            <img src="https://i.ibb.co/Z1Yck7SH/7475196962448704520-avatar-png.png" alt="Avatar" class="avatar-box">
            <div class="title">⚔️ SINH TỒN TIKTOK LIVE</div>
            <div class="subtitle">Khách quậy = Trừ Win! Người tốt tặng Hổ = Off Live chiến thắng!</div>
            <div class="win-label">SỐ LƯỢT WIN HIỆN TẠI</div>
            <div class="win-number" id="winsDisplay">500</div>
            <div class="alert-box" id="attackSection">
                <div class="alert-title" id="attackTitle">🚨 KHÁCH ĐANG PHÁ PHÁCH!</div>
                <div style="font-size: 11px; color: #ff6b81; margin-top: 3px;">Thời gian chống đỡ:</div>
                <div class="timer-num" id="countdownDisplay">10</div>
            </div>
            <div class="msg-box" id="msgDisplay">Đang chờ tương tác từ phiên Live...</div>
        </div>
        <script>
            let lastTrigger = 0;
            setInterval(() => {
                fetch('/api/status').then(res => res.json()).then(data => {
                    document.getElementById('winsDisplay').innerText = data.wins;
                    document.getElementById('msgDisplay').innerText = data.last_action_msg;
                    if (data.game_status === "OFF_LIVE") {
                        document.getElementById('offLiveOverlay').style.display = 'flex';
                        document.getElementById('offLiveMsg').innerText = data.last_action_msg;
                    }
                    if (data.animation_trigger !== lastTrigger) {
                        lastTrigger = data.animation_trigger;
                        triggerFlightAnimation();
                    }
                    let attackSec = document.getElementById('attackSection');
                    if (data.is_under_attack && data.game_status === "RUNNING") {
                        attackSec.style.display = 'block';
                        document.getElementById('countdownDisplay').innerText = data.countdown;
                    } else {
                        attackSec.style.display = 'none';
                    }
                }).catch(err => console.log("Lỗi đồng bộ:", err));
            }, 1000);
            function triggerFlightAnimation() {
                const item = document.getElementById('flyingItem');
                item.classList.remove('animate-item');
                void item.offsetWidth;
                item.classList.add('animate-item');
            }
        </script>
    </body>
    </html>
    """
    return render_template_string(html_template)

@app.route('/api/status')
def api_status():
    return jsonify(live_game_state)

if __name__ == '__main__':
    threading.Thread(target=start_tiktok_listener, daemon=True).start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
