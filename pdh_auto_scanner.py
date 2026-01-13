import requests
import time
from datetime import datetime
import sys
import os

# Import config
sys.path.append(os.path.dirname(__file__))
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

def send_telegram(message):
    """Send ONLY when breakout happens"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        response = requests.post(url, json={
            'chat_id': TELEGRAM_CHAT_ID,
            'text': message,
            'parse_mode': 'HTML',
            'disable_notification': False  # Notification aayega
        }, timeout=10)
        return response.status_code == 200
    except:
        return False

def get_all_futures_symbols():
    """Get ALL Binance Futures symbols automatically"""
    url = "https://fapi.binance.com/fapi/v1/exchangeInfo"
    try:
        response = requests.get(url, timeout=30)
        data = response.json()
        
        symbols = []
        for symbol_info in data['symbols']:
            if symbol_info['quoteAsset'] == 'USDT' and \
               symbol_info['contractType'] == 'PERPETUAL' and \
               symbol_info['status'] == 'TRADING':
                symbols.append(symbol_info['symbol'])
        
        print(f"✅ Found {len(symbols)} futures symbols")
        return symbols
    except Exception as e:
        print(f"Error fetching symbols: {e}")
        return []

def check_pdh_breakout(symbol):
    """Check if coin broke PDH - returns breakout data if yes, else None"""
    try:
        # Get yesterday's daily candle
        url = "https://fapi.binance.com/fapi/v1/klines"
        params = {'symbol': symbol, 'interval': '1d', 'limit': 2}
        response = requests.get(url, params=params, timeout=10)
        candles = response.json()
        
        if len(candles) < 2:
            return None
        
        # Yesterday's data (index 0 is yesterday, 1 is today)
        yesterday = candles[0]
        yesterday_high = float(yesterday[2])  # PDH
        yesterday_close = float(yesterday[4])
        
        # Get current price
        price_url = "https://fapi.binance.com/fapi/v1/ticker/price"
        price_resp = requests.get(price_url, params={'symbol': symbol}, timeout=10)
        current_price = float(price_resp.json()['price'])
        
        # CHECK BREAKOUT CONDITION
        if current_price > yesterday_high:
            above_percent = ((current_price - yesterday_high) / yesterday_high) * 100
            
            # Only if > 0.5% breakout (to avoid noise)
            if above_percent > 0.5:
                # Get 24h volume
                stats_url = "https://fapi.binance.com/fapi/v1/ticker/24hr"
                stats_resp = requests.get(stats_url, params={'symbol': symbol}, timeout=10)
                stats = stats_resp.json()
                volume = float(stats.get('volume', 0))
                
                return {
                    'symbol': symbol,
                    'current_price': current_price,
                    'pdh': yesterday_high,
                    'above_percent': above_percent,
                    'yesterday_close': yesterday_close,
                    'volume_24h': volume,
                    'time': datetime.now().strftime('%H:%M:%S')
                }
        
        return None  # No breakout
        
    except Exception as e:
        print(f"Error checking {symbol}: {e}")
        return None

def scan_and_alert():
    """Main scanning function - Sends alert ONLY when breakout found"""
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 🔍 Scanning for PDH breakouts...")
    
    # Get all symbols automatically
    symbols = get_all_futures_symbols()
    if not symbols:
        print("❌ No symbols found")
        return
    
    total_scanned = 0
    breakouts_found = 0
    
    for symbol in symbols:
        total_scanned += 1
        print(f"Scanning {total_scanned}/{len(symbols)}: {symbol}", end='\r')
        
        # Check for breakout
        breakout_data = check_pdh_breakout(symbol)
        
        if breakout_data:
            breakouts_found += 1
            
            # 🔥 SEND SIGNAL ONLY IF BREAKOUT FOUND
            message = f"""
🚨 <b>PDH BREAKOUT DETECTED!</b> 🚨

🏷️ <b>Symbol:</b> {breakout_data['symbol']}.P
💰 <b>Current Price:</b> ${breakout_data['current_price']:.4f}
📈 <b>Above PDH:</b> +{breakout_data['above_percent']:.2f}%
🎯 <b>PDH Level:</b> ${breakout_data['pdh']:.4f}
📊 <b>Yesterday Close:</b> ${breakout_data['yesterday_close']:.4f}
📈 <b>24h Volume:</b> {breakout_data['volume_24h']:,.0f}
🕒 <b>Time:</b> {breakout_data['time']}

✅ <b>Breakout confirmed!</b>
🎯 <b>Strategy:</b> Buy with stop below PDH

#PDH #Breakout #{breakout_data['symbol']}
"""
            print(f"\n🔥 BREAKOUT: {symbol} +{breakout_data['above_percent']:.2f}%")
            send_telegram(message)
            
            # Wait 1 second between signals
            time.sleep(1)
        
        # API rate limiting
        time.sleep(0.05)
    
    print(f"\n✅ Scan complete! Scanned: {total_scanned}, Breakouts: {breakouts_found}")
    
    # Send summary ONLY if breakouts found
    if breakouts_found > 0:
        summary = f"""
📊 <b>SCAN SUMMARY</b>

✅ Scan completed successfully
🕒 Time: {datetime.now().strftime('%H:%M:%S')}
🔍 Coins scanned: {total_scanned}
🚀 Breakouts found: {breakouts_found}
🔄 Next scan: 1 hour

#ScanComplete #{breakouts_found}Breakouts
"""
        send_telegram(summary)
    else:
        # NO SIGNAL IF NO BREAKOUTS - COMPLETE SILENCE
        print("📭 No breakouts found. No signal sent.")
    
    return breakouts_found

if __name__ == "__main__":
    print("🤖 PDH Auto Scanner - Only alerts on actual breakouts")
    scan_and_alert()