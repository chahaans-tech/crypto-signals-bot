# ema_scanner.py
import requests
import time
from datetime import datetime
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

def send_telegram(msg):
    """Send message to Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        response = requests.post(url, json={
            'chat_id': TELEGRAM_CHAT_ID,
            'text': msg,
            'parse_mode': 'HTML'
        }, timeout=5)
        return response.status_code == 200
    except:
        return False

def get_top_coins(limit=600):
    """Get top coins by volume"""
    try:
        url = "https://api.binance.com/api/v3/ticker/24hr"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            tickers = response.json()
            usdt_tickers = [t for t in tickers if t['symbol'].endswith('USDT')]
            usdt_tickers.sort(key=lambda x: float(x.get('quoteVolume', 0)), reverse=True)
            return [t['symbol'] for t in usdt_tickers[:limit]]
    except:
        return []
    return []

def calculate_ema(prices, period):
    """Exponential Moving Average"""
    if len(prices) < period:
        return 0
    
    # Start with SMA
    sma = sum(prices[:period]) / period
    
    # Calculate multiplier
    multiplier = 2 / (period + 1)
    
    # Calculate EMA
    ema = sma
    for price in prices[period:]:
        ema = (price - ema) * multiplier + ema
    
    return ema

def scan_ema_crossover():
    """Scan for 9EMA > 20EMA crossover on Daily timeframe"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔍 Daily EMA Scan")
    
    symbols = get_top_coins(600)
    if not symbols:
        print("❌ Failed to get symbols")
        return 0
    
    signals_found = 0
    
    for i, symbol in enumerate(symbols):
        try:
            print(f"Scanning {i+1}/{len(symbols)}: {symbol}", end='\r')
            
            # Get daily candles (1D timeframe)
            url = "https://api.binance.com/api/v3/klines"
            params = {'symbol': symbol, 'interval': '1d', 'limit': 50}
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code != 200:
                continue
            
            candles = response.json()
            if len(candles) < 30:
                continue
            
            # Get closing prices
            closes = [float(c[4]) for c in candles]
            
            # Current price
            price_url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
            price_resp = requests.get(price_url, timeout=5)
            if price_resp.status_code != 200:
                continue
            
            current_price = float(price_resp.json()['price'])
            
            # Calculate EMAs
            ema_9 = calculate_ema(closes, 9)
            ema_20 = calculate_ema(closes, 20)
            
            # Calculate previous EMAs
            ema_9_prev = calculate_ema(closes[:-1], 9) if len(closes) > 9 else 0
            ema_20_prev = calculate_ema(closes[:-1], 20) if len(closes) > 20 else 0
            
            # Check conditions
            if (ema_9_prev and ema_20_prev and
                current_price > ema_9 > ema_20 and
                ema_9_prev < ema_20_prev):
                
                signals_found += 1
                
                above_ema9 = ((current_price - ema_9) / ema_9) * 100
                above_ema20 = ((current_price - ema_20) / ema_20) * 100
                
                # Send signal
                msg = f"""
📈 <b>DAILY EMA CROSSOVER</b>

🏷️ {symbol}
💰 ${current_price:.4f}
📊 9EMA: ${ema_9:.4f} ({above_ema9:+.2f}%)
📈 20EMA: ${ema_20:.4f} ({above_ema20:+.2f}%)
🕒 {datetime.now().strftime('%H:%M:%S')}

✅ <b>CONFIRMED:</b> 9EMA > 20EMA
🎯 <b>SETUP:</b> Bullish trend
🛑 <b>STOP:</b> Below 20EMA

#EMA #{symbol}
"""
                send_telegram(msg)
                time.sleep(1)
            
            time.sleep(0.1)
            
        except Exception as e:
            continue
    
    print(f"\n✅ Scan complete. Signals: {signals_found}")
    
    # Send summary
    if signals_found > 0:
        summary = f"""
📊 <b>EMA SCAN SUMMARY</b>

✅ Scan completed
🕒 {datetime.now().strftime('%H:%M:%S')}
🔍 Coins scanned: {len(symbols)}
🚀 Signals found: {signals_found}

#EMA #{signals_found}Signals
"""
        send_telegram(summary)
    
    return signals_found

if __name__ == "__main__":
    scan_ema_crossover()
