# volatility_scanner.py
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

def format_volume(volume):
    """Format volume to M/B"""
    if volume >= 1_000_000_000:
        return f"{volume/1_000_000_000:.2f}B"
    elif volume >= 1_000_000:
        return f"{volume/1_000_000:.2f}M"
    elif volume >= 1_000:
        return f"{volume/1_000:.1f}K"
    else:
        return f"{volume:.0f}"

def scan_volatility(min_volatility=15, min_volume=1_000_000):
    """Scan for high volatility coins"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔍 Volatility Scanner")
    print("=" * 60)
    
    try:
        url = "https://api.binance.com/api/v3/ticker/24hr"
        response = requests.get(url, timeout=15)
        
        if response.status_code != 200:
            print("❌ API failed")
            return 0
        
        tickers = response.json()
        signals = []
        
        for ticker in tickers:
            symbol = ticker['symbol']
            
            if not symbol.endswith('USDT'):
                continue
            
            # Get metrics
            quote_volume = float(ticker.get('quoteVolume', 0))
            price_change = float(ticker.get('priceChangePercent', 0))
            current_price = float(ticker.get('lastPrice', 0))
            volume = float(ticker.get('volume', 0))
            
            # Check filters
            if (quote_volume >= min_volume and
                abs(price_change) >= min_volatility and
                current_price > 0.01):
                
                # Get daily range
                kline_url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1d&limit=2"
                kline_resp = requests.get(kline_url, timeout=5)
                
                daily_range = 0
                if kline_resp.status_code == 200:
                    candles = kline_resp.json()
                    if len(candles) >= 2:
                        high = float(candles[0][2])
                        low = float(candles[0][3])
                        daily_range = ((high - low) / low) * 100
                
                signals.append({
                    'symbol': symbol,
                    'volume': quote_volume,
                    'volatility': abs(price_change),
                    'price_change': price_change,
                    'price': current_price,
                    'daily_range': daily_range,
                    'volume_formatted': format_volume(quote_volume)
                })
        
        # Sort by volatility (highest first)
        signals.sort(key=lambda x: x['volatility'], reverse=True)
        
        # Take top 20
        top_signals = signals[:20]
        
        print(f"📊 Total coins: {len(tickers)}")
        print(f"🚨 High volatility coins: {len(signals)}")
        print(f"📈 Top signals: {len(top_signals)}")
        
        # Send signals
        for idx, signal in enumerate(top_signals):
            direction = "📈" if signal['price_change'] > 0 else "📉"
            
            msg = f"""
{direction} <b>HIGH VOLATILITY ALERT #{idx+1}</b>

🏷️ {signal['symbol']}
💰 ${signal['price']:.4f}
📈 24h Change: {signal['price_change']:+.1f}%
🔥 Volatility: {signal['volatility']:.1f}%
💰 24h Volume: {signal['volume_formatted']} USDT
📊 Daily Range: {signal['daily_range']:.1f}%

🕒 {datetime.now().strftime('%H:%M:%S')}

✅ <b>SETUP:</b> High momentum
🎯 <b>STRATEGY:</b> Breakout/Reversal
⚠️ <b>RISK:</b> High volatility

#Volatility #{signal['symbol']}
"""
            send_telegram(msg)
            time.sleep(1)
        
        # Summary
        summary = f"""
📊 <b>VOLATILITY SCAN SUMMARY</b>

✅ Scan completed
🕒 {datetime.now().strftime('%H:%M:%S')}
🔍 Total coins: {len(tickers)}
🚨 High volatility: {len(signals)}
📈 Top alerts: {len(top_signals)}
📊 Min volatility: {min_volatility}%
💰 Min volume: {format_volume(min_volume)}

#VolatilityScan #{len(top_signals)}Alerts
"""
        send_telegram(summary)
        
        return len(top_signals)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 0

if __name__ == "__main__":
    scan_volatility(min_volatility=15, min_volume=1_000_000)
