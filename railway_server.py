from flask import Flask
import threading
import os
import time

app = Flask(__name__)

@app.route('/')
def home():
    return "🚀 Crypto Signals Bot is running"

@app.route('/health')
def health():
    return "✅ Healthy"

def run_bot():
    print("🤖 Starting PDH Bot...")
    try:
        # Try PDH scanner first
        from pdh_auto_scheduler import main
        main()
    except Exception as e:
        print(f"❌ PDH failed: {e}")
        # Fallback to EMA
        try:
            from ema_scheduler import main as ema_main
            ema_main()
        except Exception as e2:
            print(f"❌ EMA failed: {e2}")

if __name__ == '__main__':
    # Start bot in background
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # Start web server
    port = int(os.environ.get("PORT", 8080))
    print(f"🌐 Web server starting on port {port}")
    app.run(host='0.0.0.0', port=port)
