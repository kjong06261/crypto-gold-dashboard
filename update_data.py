import yfinance as yf
from datetime import datetime

# 종목 리스트 (주식, 코인, 금, 환율)
tickers = {
    'IBIT': '비트코인 ETF',
    'ETH-USD': '이더리움',
    'GLD': '금 현물',
    'SLV': '은 현물',
    'NVDA': '엔비디아',
    'TSLA': '테슬라',
    'AAPL': '애플',
    'QQQ': '나스닥100',
    'KRW=X': '원/달러 환율',
    'US10Y': '미국채 10금리'
}

def get_data():
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    # 고급스러운 블랙 테마 디자인
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ background-color: #0f172a; color: #f8fafc; font-family: 'Segoe UI', sans-serif; margin: 0; padding: 20px; text-align: center; }}
            h1 {{ color: #38bdf8; margin-bottom: 10px; font-size: 2.5rem; }}
            .update-time {{ color: #94a3b8; margin-bottom: 30px; font-size: 1rem; }}
            .container {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; max-width: 1000px; margin: 0 auto; }}
            .card {{ background: #1e293b; padding: 20px; border-radius: 15px; border: 1px solid #334155; transition: 0.3s; }}
            .card:hover {{ transform: translateY(-5px); border-color: #38bdf8; }}
            .name {{ color: #94a3b8; font-size: 0.9rem; margin-bottom: 10px; }}
            .price {{ font-size: 1.8rem; font-weight: bold; color: #f1f5f9; }}
            .symbol {{ font-size: 0.7rem; color: #64748b; margin-top: 5px; }}
        </style>
    </head>
    <body>
        <h1>🚀 실시간 자산 대시보드</h1>
        <div class="update-time">{now} (매시간 자동 업데이트)</div>
        <div class="container">
    """
    
    for s, n in tickers.items():
        try:
            t = yf.Ticker(s)
            df = t.history(period='1d')
            if not df.empty:
                price = round(df['Close'].iloc[-1], 2)
                # 환율이나 금리는 단위 다르게 표시
                p_str = f"{price:,}"
                if s == 'KRW=X': p_str = f"₩{p_str}"
                elif s == 'US10Y': p_str = f"{price}%"
                else: p_str = f"${p_str}"
                
                html += f"""
                <div class="card">
                    <div class="name">{n}</div>
                    <div class="price">{p_str}</div>
                    <div class="symbol">{s}</div>
                </div>
                """
        except:
            continue
    
    html += """
        </div>
        <footer style="margin-top: 50px; color: #475569; font-size: 0.8rem;">
            © 2025 Crypto Gold Dashboard | Data by Yahoo Finance
        </footer>
    </body>
    </html>
    """
    return html

if __name__ == "__main__":
    result_html = get_data()
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(result_html)
