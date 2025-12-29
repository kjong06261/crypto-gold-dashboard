import yfinance as yf
from datetime import datetime

# Global Asset List (English Focus)
tickers = {
    'BTC-USD': 'Bitcoin',
    'ETH-USD': 'Ethereum',
    'SOL-USD': 'Solana',
    'DOGE-USD': 'Doge Coin',
    'XRP-USD': 'Ripple',
    'NVDA': 'NVIDIA',
    'TSLA': 'Tesla',
    'AAPL': 'Apple',
    'QQQ': 'Nasdaq 100',
    'GLD': 'Gold Spot',
    'KRW=X': 'USD/KRW'
}

def get_data():
    now = datetime.now().strftime('%b %d, %Y %H:%M')
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Global Asset Terminal</title>
        <style>
            body {{ background: #020617; color: #f1f5f9; font-family: 'Inter', system-ui, sans-serif; margin: 0; padding: 20px; }}
            .container {{ max-width: 1100px; margin: 0 auto; }}
            .header {{ border-bottom: 1px solid #1e293b; padding: 40px 0 20px 0; margin-bottom: 30px; display: flex; justify-content: space-between; align-items: flex-end; }}
            .header h1 {{ margin: 0; font-size: 2.5rem; font-weight: 800; color: #fff; letter-spacing: -2px; }}
            .header-meta {{ text-align: right; color: #64748b; font-size: 0.85rem; }}
            .status {{ display: inline-flex; align-items: center; background: #064e3b; color: #4ade80; padding: 4px 12px; border-radius: 50px; font-size: 0.75rem; font-weight: 700; margin-bottom: 10px; }}
            .dot {{ width: 8px; height: 8px; background: #4ade80; border-radius: 50%; margin-right: 8px; animation: blink 1.5s infinite; }}
            @keyframes blink {{ 0% {{ opacity: 1; }} 50% {{ opacity: 0.3; }} 100% {{ opacity: 1; }} }}
            .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 16px; }}
            .card {{ background: #0f172a; border: 1px solid #1e293b; padding: 24px; border-radius: 12px; transition: all 0.2s; }}
            .card:hover {{ border-color: #3b82f6; }}
            .label {{ color: #94a3b8; font-size: 0.8rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 12px; display: block; }}
            .price-row {{ display: flex; justify-content: space-between; align-items: center; }}
            .price {{ font-size: 1.75rem; font-weight: 700; }}
            .change {{ font-size: 0.9rem; font-weight: 700; }}
            .up {{ color: #ef4444; }} .down {{ color: #3b82f6; }}
            .footer {{ margin-top: 60px; padding-top: 20px; border-top: 1px solid #1e293b; text-align: center; color: #475569; font-size: 0.8rem; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div>
                    <div class="status"><span class="dot"></span>LIVE SYSTEM ONLINE</div>
                    <h1>ASSET TERMINAL</h1>
                </div>
                <div class="header-meta">
                    Last Update: {now} (KST)<br>
                    Data Refresh: Every Hour
                </div>
            </div>
            <div class="grid">
    """

    for s, n in tickers.items():
        try:
            t = yf.Ticker(s)
            df = t.history(period='2d')
            if len(df) >= 2:
                cur = df['Close'].iloc[-1]
                prev = df['Close'].iloc[-2]
                pct = ((cur - prev) / prev) * 100
                cls = "up" if pct >= 0 else "down"
                sign = "+" if pct >= 0 else ""
                val = f"{cur:,.2f}"
                val = f"₩{val}" if s == 'KRW=X' else f"${val}"

                html += f"""
                <div class="card">
                    <span class="label">{n}</span>
                    <div class="price-row">
                        <span class="price">{val}</span>
                        <span class="change {cls}">{sign}{pct:.2f}%</span>
                    </div>
                    <div style="font-size: 0.7rem; color: #334155; margin-top: 8px;">{s}</div>
                </div>
                """
        except: continue

    html += """
            </div>
            <div class="footer">
                © 2025 US-DIVIDEND-PRO | GLOBAL PROJECT | POWERED BY YAHOO FINANCE
            </div>
        </div>
    </body>
    </html>
    """
    return html

if __name__ == "__main__":
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(get_data())
