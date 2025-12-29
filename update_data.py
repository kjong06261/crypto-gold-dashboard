import yfinance as yf
from datetime import datetime

tickers = {
    'IBIT': '비트코인 ETF', 'ETH-USD': '이더리움', 'GLD': '금 현물',
    'NVDA': '엔비디아', 'TSLA': '테슬라', 'AAPL': '애플',
    'QQQ': '나스닥100', 'KRW=X': '원/달러 환율'
}

def get_data():
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ background: #0b0f19; color: #e2e8f0; font-family: 'Inter', sans-serif; margin: 0; padding: 40px 20px; }}
            .header {{ margin-bottom: 40px; border-left: 5px solid #38bdf8; padding-left: 20px; text-align: left; max-width: 1000px; margin: 0 auto 40px; }}
            h1 {{ font-size: 2.2rem; margin: 0; color: #f8fafc; }}
            .update-time {{ color: #64748b; font-size: 0.9rem; }}
            .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 20px; max-width: 1000px; margin: 0 auto; }}
            .card {{ background: #161e2d; padding: 25px; border-radius: 16px; border: 1px solid #2d3748; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }}
            .name {{ color: #94a3b8; font-size: 0.85rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }}
            .price-row {{ display: flex; align-items: baseline; gap: 10px; margin: 10px 0; }}
            .price {{ font-size: 1.8rem; font-weight: 800; letter-spacing: -0.02em; }}
            .change {{ font-size: 0.95rem; font-weight: 600; }}
            .up {{ color: #ef4444; }} .down {{ color: #3b82f6; }}
            .footer {{ max-width: 1000px; margin: 60px auto 0; padding-top: 20px; border-top: 1px solid #2d3748; color: #475569; font-size: 0.85rem; display: flex; justify-content: space-between; }}
            .market-status {{ display: inline-block; padding: 4px 12px; background: #064e3b; color: #34d399; border-radius: 20px; font-size: 0.75rem; font-weight: bold; margin-bottom: 15px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="market-status">● LIVE MARKET DATA</div>
            <h1>Global Asset Terminal</h1>
            <div class="update-time">마지막 업데이트: {now} (KST)</div>
        </div>
        <div class="grid">
    """
    
    for s, n in tickers.items():
        try:
            t = yf.Ticker(s)
            df = t.history(period='2d')
            if len(df) >= 2:
                close_today = df['Close'].iloc[-1]
                close_yesterday = df['Close'].iloc[-2]
                change = close_today - close_yesterday
                change_pct = (change / close_yesterday) * 100
                
                color_class = "up" if change >= 0 else "down"
                sign = "+" if change >= 0 else ""
                arrow = "▲" if change >= 0 else "▼"
                
                p_str = f"{close_today:,.2f}"
                if s == 'KRW=X': p_str = f"₩{p_str}"
                else: p_str = f"${p_str}"

                html += f"""
                <div class="card">
                    <div class="name">{n}</div>
                    <div class="price-row">
                        <div class="price">{p_str}</div>
                        <div class="change {color_class}">{arrow} {sign}{change_pct:.2f}%</div>
                    </div>
                    <div style="font-size: 0.7rem; color: #475569;">Symbol: {s}</div>
                </div>
                """
        except: continue
    
    html += f"""
        </div>
        <div class="footer">
            <div>© 2025 US-DIVIDEND-PRO Terminal</div>
            <div>Data provided by Yahoo Finance</div>
        </div>
    </body>
    </html>
    """
    return html

if __name__ == "__main__":
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(get_data())
