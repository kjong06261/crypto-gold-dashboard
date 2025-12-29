import yfinance as yf
from datetime import datetime

# 사장님의 똑똑한 선택: 주식 + 코인 하이브리드 리스트
tickers = {
    # --- 코인 섹션 ---
    'BTC-USD': '비트코인',
    'ETH-USD': '이더리움',
    'SOL-USD': '솔라나',
    'DOGE-USD': '도지코인',
    'XRP-USD': '리플',
    # --- 주식 & 자산 섹션 ---
    'NVDA': '엔비디아',
    'TSLA': '테슬라',
    'AAPL': '애플',
    'QQQ': '나스닥100',
    'GLD': '금 현물',
    'KRW=X': '원/달러 환율'
}

def get_data():
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Crypto & Stock Terminal</title>
        <style>
            body {{ background: #05070a; color: #e2e8f0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 0; padding: 20px; }}
            .wrapper {{ max-width: 1200px; margin: 0 auto; }}
            .header {{ display: flex; justify-content: space-between; align-items: flex-end; padding: 20px 0; border-bottom: 2px solid #1e293b; margin-bottom: 30px; }}
            h1 {{ margin: 0; font-size: 2rem; color: #f8fafc; letter-spacing: -1px; }}
            .live-dot {{ display: inline-block; width: 10px; height: 10px; background: #22c55e; border-radius: 50%; margin-right: 8px; animation: pulse 2s infinite; }}
            @keyframes pulse {{ 0% {{ opacity: 1; }} 50% {{ opacity: 0.4; }} 100% {{ opacity: 1; }} }}
            .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 15px; }}
            .card {{ background: #111827; padding: 20px; border-radius: 12px; border: 1px solid #1f2937; transition: all 0.2s ease; }}
            .card:hover {{ border-color: #3b82f6; background: #1a2234; }}
            .info {{ display: flex; justify-content: space-between; margin-bottom: 10px; }}
            .label {{ color: #94a3b8; font-size: 0.8rem; font-weight: 600; }}
            .symbol {{ color: #475569; font-size: 0.7rem; }}
            .price-box {{ display: flex; align-items: baseline; justify-content: space-between; }}
            .price {{ font-size: 1.6rem; font-weight: 700; color: #f1f5f9; }}
            .change {{ font-size: 0.9rem; font-weight: 600; padding: 4px 8px; border-radius: 6px; }}
            .up {{ color: #ff4d4d; background: rgba(255, 77, 77, 0.1); }}
            .down {{ color: #4d94ff; background: rgba(77, 148, 255, 0.1); }}
            .footer {{ text-align: center; margin-top: 50px; color: #475569; font-size: 0.8rem; border-top: 1px solid #1e293b; padding-top: 20px; }}
        </style>
    </head>
    <body>
        <div class="wrapper">
            <div class="header">
                <div>
                    <h1><span class="live-dot"></span>PRO ASSET TERMINAL</h1>
                    <p style="color:#64748b; margin:5px 0 0 0;">Stock & Crypto Real-time Tracker</p>
                </div>
                <div style="text-align: right; color:#94a3b8; font-size:0.8rem;">
                    Last Update: {now}<br>Auto-refresh: Every 1 Hour
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
                diff = cur - prev
                pct = (diff / prev) * 100
                
                cls = "up" if diff >= 0 else "down"
                sign = "+" if diff >= 0 else ""
                
                # 원화/달러 구분 표시
                val = f"{cur:,.2f}"
                val = f"₩{val}" if s == 'KRW=X' else f"${val}"

                html += f"""
                <div class="card">
                    <div class="info">
                        <span class="label">{n}</span>
                        <span class="symbol">{s}</span>
                    </div>
                    <div class="price-box">
                        <span class="price">{val}</span>
                        <span class="change {cls}">{sign}{pct:.2f}%</span>
                    </div>
                </div>
                """
        except Exception as e:
            continue

    html += """
            </div>
            <div class="footer">
                © 2025 US-DIVIDEND-PRO | Built for Gemini Training Project | Data via Yahoo Finance
            </div>
        </div>
    </body>
    </html>
    """
    return html

if __name__ == "__main__":
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(get_data())
