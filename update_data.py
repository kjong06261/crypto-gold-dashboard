import yfinance as yf
from datetime import datetime

# 사장님이 선정한 글로벌 핵심 자산 리스트
asset_pool = {
    'BTC-USD': 'Bitcoin', 'ETH-USD': 'Ethereum', 'SOL-USD': 'Solana',
    'DOGE-USD': 'Doge Coin', 'XRP-USD': 'Ripple', 'NVDA': 'NVIDIA',
    'TSLA': 'Tesla', 'AAPL': 'Apple', 'QQQ': 'Nasdaq 100',
    'GLD': 'Gold SPDR', 'KRW=X': 'USD/KRW Rate'
}

def get_data():
    results = []
    now = datetime.now().strftime('%b %d, %Y %H:%M')
    for s, n in asset_pool.items():
        try:
            t = yf.Ticker(s)
            df = t.history(period='2d')
            if len(df) >= 2:
                cur = df['Close'].iloc[-1]
                prev = df['Close'].iloc[-2]
                pct = ((cur - prev) / prev) * 100
                results.append({'symbol': s, 'name': n, 'price': cur, 'pct': pct})
        except: continue
    results.sort(key=lambda x: x['name'])

    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Prime Asset Terminal</title>
        <meta name="google-site-verification" content="여기에_구글서치콘솔_코드를_넣으세요" />
        <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3030006828946894" crossorigin="anonymous"></script>
        <style>
            body {{ background: #020617; color: #f1f5f9; font-family: 'Inter', sans-serif; margin: 0; padding: 20px; }}
            .container {{ max-width: 1000px; margin: 0 auto; }}
            .header {{ border-left: 4px solid #3b82f6; padding: 25px; margin: 40px 0; background: #0f172a; border-radius: 0 12px 12px 0; }}
            h1 {{ margin: 0; font-size: 2.2rem; letter-spacing: -2px; color: #fff; font-weight: 800; }}
            .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 15px; }}
            .card {{ background: #0f172a; border: 1px solid #1e293b; padding: 25px; border-radius: 12px; transition: 0.2s; }}
            .card:hover {{ border-color: #3b82f6; transform: translateY(-2px); }}
            .label {{ color: #94a3b8; font-size: 0.8rem; font-weight: 700; text-transform: uppercase; margin-bottom: 12px; display: block; }}
            .price-row {{ display: flex; justify-content: space-between; align-items: baseline; }}
            .price {{ font-size: 1.8rem; font-weight: 800; }}
            .pct {{ font-size: 0.95rem; font-weight: 700; }}
            .up {{ color: #ef4444; }} .down {{ color: #3b82f6; }}
            .footer {{ margin-top: 60px; text-align: center; color: #4b5563; font-size: 0.8rem; border-top: 1px solid #1e293b; padding: 40px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>PRIME ASSET TERMINAL</h1>
                <p style="color:#64748b; margin:8px 0 0 0;">Global Market Intelligence • Updated: {now}</p>
            </div>
            <div class="grid">
    """
    for item in results:
        cls = "up" if item['pct'] >= 0 else "down"
        sign = "+" if item['pct'] >= 0 else ""
        prefix = "₩" if item['symbol'] == 'KRW=X' else "$"
        html += f"""
        <div class="card">
            <span class="label">{item['name']}</span>
            <div class="price-row">
                <span class="price">{prefix}{item['price']:,.2f}</span>
                <span class="pct {cls}">{sign}{item['pct']:.2f}%</span>
            </div>
        </div>
        """
    html += """
            </div>
            <div class="footer"><p>© 2025 PRIME TERMINAL</p></div>
        </div>
    </body>
    </html>
    """
    return html

if __name__ == "__main__":
    # 1. 사이트 메인 페이지 생성
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(get_data())

    # 2. 구글용 지도(Sitemap) 생성
    sitemap = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://coin.us-dividend-pro.com/</loc>
        <lastmod>{datetime.now().strftime('%Y-%m-%d')}</lastmod>
        <changefreq>hourly</changefreq>
        <priority>1.0</priority>
    </url>
</urlset>"""
    with open('sitemap.xml', 'w', encoding='utf-8') as f:
        f.write(sitemap)
