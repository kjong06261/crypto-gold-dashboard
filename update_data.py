import yfinance as yf
from datetime import datetime

# 1. 나스닥 섹터 (대표님 기존 50개 종목 리스트)
nasdaq_sectors = {
    "MARKET INDEX": ['QQQ', 'TQQQ', 'SQQQ', 'VOO', 'DIA', 'IWM'],
    "MAGNIFICENT 7": ['NVDA', 'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA'],
    "SEMICONDUCTORS": ['SOXL', 'SOXX', 'AVGO', 'AMD', 'ARM', 'MU', 'TSM', 'ASML', 'INTC', 'AMAT', 'LRCX', 'QCOM'],
    "AI & SOFTWARE": ['PLTR', 'ORCL', 'ADBE', 'CRM', 'SNOW', 'NOW', 'WDAY', 'PALO'],
    "FINTECH & BEYOND": ['PYPL', 'SQ', 'V', 'MA', 'COIN', 'NFLX', 'UBER', 'SHOP', 'COST']
}

# 2. 코인 섹터
coin_sectors = {
    "MAJOR COINS": ['BTC-USD', 'ETH-USD', 'SOL-USD', 'BNB-USD'],
    "ALT COINS": ['XRP-USD', 'ADA-USD', 'DOGE-USD', 'LINK-USD', 'AVAX-USD']
}

# 3. 배당주 섹터 (대표님이 보시는 주요 배당주들)
dividend_sectors = {
    "DIVIDEND KINGS": ['O', 'SCHD', 'JEPI', 'JEPQ', 'VICI'],
    "TECH DIVIDEND": ['AVGO', 'MSFT', 'AAPL', 'TXN', 'CSCO'],
    "MONTHLY PAY": ['MAIN', 'STAG', 'ADC', 'EPR']
}

def create_terminal_html(title, sector_dict, now, accent_color="#2962ff"):
    """대표님의 나스닥 디자인을 그대로 쓰되, 섹터별로 색상 포인트만 다르게 설정 가능"""
    html_content = ""
    for sector_name, symbols in sector_dict.items():
        html_content += f'<h2 class="sector-title" style="border-left-color:{accent_color}; color:{accent_color};">{sector_name}</h2>'
        html_content += '<div class="grid">'
        for s in symbols:
            try:
                t = yf.Ticker(s)
                df = t.history(period='2d')
                if len(df) < 2: continue
                cur = df['Close'].iloc[-1]
                prev = df['Close'].iloc[-2]
                pct = ((cur - prev) / prev) * 100
                cls = "up" if pct >= 0 else "down"
                sign = "+" if pct >= 0 else ""
                
                # 심볼에서 -USD 제거 (보기 편하게)
                display_name = s.replace("-USD", "")
                
                html_content += f"""
                <div class="card">
                    <div class="card-header">
                        <span class="symbol">{display_name}</span>
                        <span class="pct {cls}">{sign}{pct:.2f}%</span>
                    </div>
                    <div class="price">${cur:,.2f}</div>
                </div>
                """
            except: continue
        html_content += '</div>'

    return f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        <style>
            :root {{ --bg: #05070a; --card-bg: #11141b; --border: #1e222d; --text: #d1d4dc; --accent: {accent_color}; }}
            body {{ background-color: var(--bg); color: var(--text); font-family: 'Trebuchet MS', sans-serif; margin: 0; padding: 20px; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            header {{ border-bottom: 2px solid var(--accent); padding-bottom: 20px; margin-bottom: 40px; }}
            h1 {{ font-size: 38px; color: #ffffff; margin: 0; letter-spacing: -1px; }}
            .update-tag {{ font-size: 14px; color: #848e9c; margin-top: 5px; }}
            .sector-title {{ font-size: 18px; margin: 40px 0 15px 0; border-left: 4px solid; padding-left: 10px; text-transform: uppercase; }}
            .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 12px; }}
            .card {{ background: var(--card-bg); border: 1px solid var(--border); padding: 15px; border-radius: 6px; transition: all 0.2s ease; }}
            .card:hover {{ background: #1c212d; border-color: var(--accent); transform: translateY(-2px); }}
            .symbol {{ font-weight: bold; font-size: 16px; color: #fff; }}
            .price {{ font-size: 24px; font-weight: 700; color: #ffffff; }}
            .pct {{ font-size: 13px; font-weight: bold; padding: 2px 6px; border-radius: 4px; }}
            .up {{ color: #00ffaa; background: rgba(0, 255, 170, 0.1); }}
            .down {{ color: #ff3b3b; background: rgba(255, 59, 59, 0.1); }}
            footer {{ margin-top: 80px; padding: 20px; text-align: center; font-size: 12px; color: #444; border-top: 1px solid var(--border); }}
        </style>
    </head>
    <body>
        <div class="container">
            <header><h1>{title}</h1><div class="update-tag">LIVE MARKET DATA • {now} KST</div></header>
            {html_content}
            <footer><p>© 2025 US-DIVIDEND-PRO. All rights reserved.</p></footer>
        </div>
    </body>
    </html>
    """

if __name__ == "__main__":
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    # 1. 나스닥 (index.html) - 파란색 강조
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(create_terminal_html("TECH TERMINAL PRO", nasdaq_sectors, now, "#2962ff"))
    
    # 2. 코인 (coin.html) - 금색 강조
    with open('coin.html', 'w', encoding='utf-8') as f:
        f.write(create_terminal_html("CRYPTO TERMINAL", coin_sectors, now, "#fbbf24"))
        
    # 3. 배당주 (dividend.html) - 초록색 강조
    with open('dividend.html', 'w', encoding='utf-8') as f:
        f.write(create_terminal_html("DIVIDEND TERMINAL", dividend_sectors, now, "#00ffaa"))

    print(f"[{now}] 나스닥, 코인, 배당주 페이지 전체 업데이트 완료!")
