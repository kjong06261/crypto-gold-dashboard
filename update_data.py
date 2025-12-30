import yfinance as yf
import feedparser
from datetime import datetime

# 1. 자산 리스트 설정
nasdaq_sectors = {
    "MARKET INDEX": ['QQQ', 'TQQQ', 'SQQQ', 'VOO', 'DIA', 'IWM'],
    "MAGNIFICENT 7": ['NVDA', 'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA'],
    "SEMICONDUCTORS": ['SOXL', 'SOXX', 'AVGO', 'AMD', 'ARM', 'MU', 'TSM', 'ASML', 'INTC', 'AMAT', 'LRCX', 'QCOM']
}

coin_sectors = {
    "MAJOR CRYPTO": ['BTC-USD', 'ETH-USD', 'SOL-USD', 'BNB-USD', 'XRP-USD'],
    "MEME & ALT": ['DOGE-USD', 'SHIB-USD', 'PEPE-USD', 'ADA-USD', 'LINK-USD']
}

dividend_sectors = {
    "DIVIDEND KINGS": ['O', 'SCHD', 'JEPI', 'JEPQ', 'VICI', 'MAIN', 'STAG'],
    "HIGH YIELD": ['MO', 'T', 'VZ', 'BTI', 'PFE']
}

# 2. 뉴스 가져오기
def get_news():
    try:
        url = "https://news.google.com/rss/search?q=investing+finance&hl=en-US&gl=US&ceid=US:en"
        feed = feedparser.parse(url)
        html = '<div class="news-box">'
        for entry in feed.entries[:4]:
            html += f'<div class="news-item">🔔 <a href="{entry.link}" target="_blank">{entry.title}</a></div>'
        return html + '</div>'
    except: return ""

# 3. 디자인 엔진 (여기가 핵심입니다. 황금색/검정색 디자인을 여기서 만듭니다)
def create_page(title, sectors, color_theme, filename):
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    cards_html = ""
    
    for sector, symbols in sectors.items():
        cards_html += f'<h2 class="sector-title" style="border-color:{color_theme}; color:{color_theme}">{sector}</h2><div class="grid">'
        for s in symbols:
            try:
                t = yf.Ticker(s)
                hist = t.history(period="2d")
                if len(hist) < 2: continue
                price = hist['Close'].iloc[-1]
                prev = hist['Close'].iloc[-2]
                pct = ((price - prev) / prev) * 100
                
                # 상승/하락 색상
                cls = "up" if pct >= 0 else "down"
                sign = "+" if pct >= 0 else ""
                
                # 심볼 이름 깔끔하게
                name = s.replace("-USD", "")
                
                cards_html += f"""
                <div class="card">
                    <div class="top">
                        <span class="name">{name}</span>
                        <span class="pct {cls}">{sign}{pct:.2f}%</span>
                    </div>
                    <div class="price">${price:,.2f}</div>
                </div>"""
            except: continue
        cards_html += '</div>'

    # 전체 HTML 조립 (CSS 디자인 포함)
    full_html = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        <style>
            :root {{ --bg: #000000; --card: #111; --text: #eee; --theme: {color_theme}; }}
            body {{ background: var(--bg); color: var(--text); font-family: 'Inter', sans-serif; margin: 0; padding: 20px; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            header {{ border-bottom: 2px solid var(--theme); padding-bottom: 20px; margin-bottom: 30px; }}
            h1 {{ margin: 0; font-size: 2rem; color: #fff; }}
            .time {{ color: #888; font-size: 0.9rem; margin-top: 5px; }}
            .sector-title {{ margin-top: 40px; border-left: 5px solid; padding-left: 15px; font-size: 1.2rem; text-transform: uppercase; }}
            .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 15px; }}
            .card {{ background: var(--card); border: 1px solid #333; padding: 20px; border-radius: 8px; }}
            .card:hover {{ border-color: var(--theme); transform: translateY(-3px); transition: 0.3s; }}
            .top {{ display: flex; justify-content: space-between; font-size: 0.9rem; color: #aaa; margin-bottom: 5px; }}
            .price {{ font-size: 1.5rem; font-weight: bold; color: #fff; }}
            .up {{ color: #ff4d4d; }} .down {{ color: #4da6ff; }} /* 한국식: 상승 빨강, 하락 파랑 */
            .news-box {{ background: #111; padding: 15px; margin-bottom: 30px; border: 1px solid #333; border-radius: 8px; }}
            .news-item {{ margin-bottom: 8px; font-size: 0.9rem; }}
            .news-item a {{ color: #ccc; text-decoration: none; }}
            .news-item a:hover {{ color: var(--theme); }}
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>{title}</h1>
                <div class="time">LAST UPDATE: {now} (KST)</div>
            </header>
            {get_news() if filename == 'index.html' else ''}
            {cards_html}
        </div>
    </body>
    </html>
    """
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(full_html)

if __name__ == "__main__":
    # 1. 나스닥 (메인, 파란색 테마)
    create_page("NASDAQ TERMINAL", nasdaq_sectors, "#2962ff", "index.html")
    
    # 2. 코인 (황금색 테마) - 여기가 대표님이 원하시는 골드 대시보드입니다.
    create_page("CRYPTO GOLD DASHBOARD", coin_sectors, "#fbbf24", "coin.html")
    
    # 3. 배당주 (초록색 테마)
    create_page("DIVIDEND KINGS", dividend_sectors, "#00ffaa", "dividend.html")
