import yfinance as yf
from datetime import datetime

# 종목 확 늘린 20개 리스트
coin_pool = {
    'BTC-USD': 'Bitcoin', 'ETH-USD': 'Ethereum', 'SOL-USD': 'Solana',
    'XRP-USD': 'Ripple', 'ADA-USD': 'Cardano', 'DOGE-USD': 'Dogecoin',
    'DOT-USD': 'Polkadot', 'LINK-USD': 'Chainlink', 'AVAX-USD': 'Avalanche',
    'TRX-USD': 'TRON', 'SHIB-USD': 'Shiba Inu', 'LTC-USD': 'Litecoin',
    'BCH-USD': 'Bitcoin Cash', 'UNI-USD': 'Uniswap', 'NEAR-USD': 'NEAR Protocol',
    'APT-USD': 'Aptos', 'STX-USD': 'Stacks', 'RENDER-USD': 'Render',
    'SUI-USD': 'Sui', 'PEPE-USD': 'Pepe'
}

def get_data():
    results = []
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    for s, n in coin_pool.items():
        try:
            t = yf.Ticker(s)
            df = t.history(period='2d')
            if len(df) < 2: continue
            cur = df['Close'].iloc[-1]
            prev = df['Close'].iloc[-2]
            pct = ((cur - prev) / prev) * 100
            results.append({'symbol': n, 'price': cur, 'pct': pct})
        except: continue
    
    html = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3030006828946894" crossorigin="anonymous"></script>
        <title>Crypto Terminal</title>
        <style>
            body {{ background-color: #000; color: #fbbf24; font-family: 'Inter', sans-serif; margin: 0; padding: 20px; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            header {{ text-align: center; padding: 40px 0; border-bottom: 2px solid #fbbf24; margin-bottom: 30px; }}
            h1 {{ font-size: 36px; text-transform: uppercase; letter-spacing: 2px; }}
            .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 15px; }}
            .card {{ background: #111; padding: 20px; border-radius: 12px; border: 1px solid #333; text-align: center; transition: 0.3s; }}
            .card:hover {{ border-color: #fbbf24; transform: scale(1.02); }}
            .name {{ font-size: 18px; font-weight: bold; display: block; margin-bottom: 10px; color: #fff; }}
            .price {{ font-size: 24px; font-weight: 800; display: block; margin-bottom: 5px; }}
            .pct {{ font-size: 16px; font-weight: 600; }}
            .up {{ color: #f87171; }} .down {{ color: #60a5fa; }}
            footer {{ margin-top: 50px; text-align: center; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>CRYPTO TERMINAL</h1>
                <p>24/7 Real-time Market Data | Last Update: {now}</p>
            </header>
            <div class="grid">
    """
    for item in results:
        cls = "up" if item['pct'] >= 0 else "down"
        sign = "+" if item['pct'] >= 0 else ""
        html += f"""
                <div class="card">
                    <span class="name">{item['symbol']}</span>
                    <span class="price">${item['price']:,.2f}</span>
                    <span class="pct {cls}">{sign}{item['pct']:.2f}%</span>
                </div>
        """
    html += """
            </div>
            <footer><p>© 2025 COIN.US-DIVIDEND-PRO</p></footer>
        </div>
    </body>
    </html>
    """
    return html

if __name__ == "__main__":
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(get_data())
    
    # 사이트맵도 코인 주소로 정확히 세팅
    sitemap = f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://coin.us-dividend-pro.com/</loc><priority>1.0</priority></url></urlset>'
    with open('sitemap.xml', 'w', encoding='utf-8') as f:
        f.write(sitemap)
