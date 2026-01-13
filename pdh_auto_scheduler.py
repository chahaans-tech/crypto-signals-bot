import schedule
import time
from datetime import datetime
from pdh_auto_scanner import scan_and_alert, send_telegram

def hourly_scan():
    """Run hourly scan - Only sends signal if breakouts found"""
    print(f"\n{'='*60}")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🚀 Starting hourly PDH scan...")
    print('='*60)
    
    breakouts = scan_and_alert()
    
    if breakouts == 0:
        # COMPLETE SILENCE - No message at all
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 📭 No breakouts. No signal sent.")
    else:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ {breakouts} breakouts alerted.")

def main():
    """Main scheduler - Runs 24/7"""
    print("=" * 60)
    print("🤖 PDH AUTO BREAKOUT BOT")
    print("=" * 60)
    print("📱 Will ONLY send Telegram when breakouts happen")
    print("📭 Complete silence when no breakouts")
    print("⏰ Scans every hour automatically")
    print("=" * 60)
    
    # Send ONE startup message
    startup_msg = f"""
🤖 <b>PDH AUTO BREAKOUT BOT ACTIVATED</b>

✅ System: ONLINE
🕒 Started: {datetime.now().strftime('%H:%M:%S')}
🎯 Target: PDH Breakouts only
📱 Alerts: ONLY when breakouts happen
📭 Silence: When no breakouts
⏰ Schedule: Automatic hourly scans

✅ Bot will scan 500+ coins every hour
🚀 Will alert ONLY on actual breakouts
📭 No spam - only quality signals

#BotOnline #AutoPDH #NoSpam
"""
    send_telegram(startup_msg)
    
    # Setup schedule
    schedule.every().hour.do(hourly_scan)
    print("✅ Scheduler set: Every hour")
    
    # Run first scan immediately
    print(f"\n🚀 Running first scan now...")
    hourly_scan()
    
    # Keep running
    print("\n✅ Bot running. Press Ctrl+C to stop.")
    print("📱 Telegram signals ONLY when breakouts happen")
    print("📭 Complete silence otherwise")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped")
        send_telegram("🛑 PDH Bot stopped manually")

if __name__ == "__main__":
    main()