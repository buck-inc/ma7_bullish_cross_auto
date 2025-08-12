import ccxt
import pandas as pd
from datetime import datetime
import pytz
import requests

# ===== CONFIG TELEGRAM =====
BOT_TOKEN = ${{secret."ISI_TOKEN_BOT_DISINI"}}
CHAT_ID = ${{secret."ISI_CHAT_ID_DISINI"}}

# List top 30 coin USDT pair
SYMBOLS = [
    "BTC/USDT", "ETH/USDT", "BNB/USDT", "SOL/USDT", "XRP/USDT", "ADA/USDT", "DOGE/USDT", "TRX/USDT",
    "DOT/USDT", "MATIC/USDT", "LTC/USDT", "SHIB/USDT", "AVAX/USDT", "LINK/USDT", "ATOM/USDT",
    "XMR/USDT", "UNI/USDT", "ETC/USDT", "HBAR/USDT", "APT/USDT", "ARB/USDT", "VET/USDT", "OP/USDT",
    "GRT/USDT", "QNT/USDT", "AAVE/USDT", "ALGO/USDT", "SAND/USDT", "MANA/USDT", "EOS/USDT"
]

# Inisialisasi exchange Binance
exchange = ccxt.binance()

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": msg}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Gagal kirim Telegram: {e}")

def get_signal(symbol):
    try:
        # Ambil data candle 1 jam
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe='1h', limit=20)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        
        # Konversi waktu ke WIB
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms', utc=True)
        df['timestamp'] = df['timestamp'].dt.tz_convert(pytz.timezone('Asia/Jakarta'))

        # Hitung MA7
        df['ma7'] = df['close'].rolling(window=7).mean()

        # Cek bullish cross MA7 dari bawah
        if df['close'].iloc[-2] < df['ma7'].iloc[-2] and df['close'].iloc[-1] > df['ma7'].iloc[-1]:
            return f"{symbol} 🚀 Bullish Cross MA7 | Waktu: {df['timestamp'].iloc[-1].strftime('%Y-%m-%d %H:%M')}"
        return None
    except Exception as e:
        return f"Error {symbol}: {e}"

def main():
    wib_time = datetime.now(pytz.timezone('Asia/Jakarta')).strftime('%Y-%m-%d %H:%M:%S')
    signals = []

    for symbol in SYMBOLS:
        sig = get_signal(symbol)
        if sig:
            signals.append(sig)

    if signals:
        pesan = f"📈 Sinyal Bullish Cross MA7 - {wib_time}\n\n" + "\n".join(signals)
    else:
        pesan = f"❌ Tidak ada sinyal Bullish Cross MA7 - {wib_time}"

    print(pesan)
    send_telegram(pesan)

if __name__ == "__main__":
    main()

