# ema_scheduler.py
import schedule
import time
from datetime import datetime
from ema_scanner import scan_ema_crossover, send_telegram

def run_scan():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔄 Running EMA scan")
    scan_ema_crossover()

def main():
    print("🤖 EMA SCANNER - AUTO SCHEDULER")
    print("=" * 50)
    
    # Startup message
    send_telegram(f"""
🤖 <b>EMA SCANNER ACTIVATED</b>

✅ System: ONLINE
🕒 {datetime.now().strftime('%H:%M:%S')}
📊 Timeframe: Daily (1D)
🎯 Strategy: 9EMA > 20EMA crossover
⏰ Schedule: Every 1 hours
🔍 Coverage: Top 50 coins by volume

#EMA #AutoScan
""")
    
    # Schedule every 1 hours
    schedule.every(1).hours.do(run_scan)
    print("⏰ Schedule: Every 1 hours")
    
    # Run first scan immediately
    run_scan()
    
    print("\n✅ Scheduler running. Press Ctrl+C to stop.")
    
    # Keep running
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()
