import yfinance as yf
from datetime import datetime
import os

# 종목을 30개로 대폭 늘렸습니다. 15개만 나올 일이 없게 만들었습니다.
coin_pool = {
    'BTC-USD': 'Bitcoin', 'ETH-USD': 'Ethereum', 'SOL-USD': 'Solana',
    'XRP-USD': 'Ripple', 'ADA-USD': 'Cardano', 'DOGE-USD': 'Dogecoin',
    'DOT-USD': 'Polkadot', 'LINK-USD': 'Chainlink', 'AVAX-USD': 'Avalanche',
    'TRX-USD': 'TRON', 'SHIB-USD': 'Shiba Inu', 'LTC-USD': 'Litecoin',
    'BCH-USD': 'Bitcoin Cash', 'UNI-USD': 'Uniswap', 'NEAR-USD': 'NEAR Protocol',
    'APT-USD': 'Aptos', 'STX-USD': 'Stacks', 'RENDER-USD': 'Render',
    'SUI-USD': 'Sui', 'PEPE-USD': 'Pepe', 'OP-USD': 'Optimism',
    'ARB-USD': 'Arbitrum', 'KAS-USD': 'Kaspa', 'FET-USD': 'Fetch.ai',
    'STX-USD': 'Stacks', 'TAO-USD': 'Bittensor', 'IMX-USD': 'Immutable',
    'BONK-USD': 'Bonk', 'WIF-USD': 'dogwifhat', 'FLOKI-USD': 'Floki'
}

def get_data():
    results = []
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    # 데이터 수집 (안 불러와지는 건 패스하고 최대한 많이 채웁니다)
    for s, n in coin_pool.items():
        try:
            t = yf.Ticker(s)
            df = t.history(period='2d')
            if len(df) < 2: continue
            cur = df['Close'].iloc[-1]
            prev = df['Close'].iloc[-2]
            pct = ((cur - prev) / prev) * 100
            results.append({'symbol': n, 'price': cur, 'pct': pct})
        except:
            continue
    
    html = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3030006828946894" crossorigin="anonymous"></script>
        <title>Premium Crypto Terminal</title>
        <style>
            :root {{ --gold: #fbbf24; --bg: #000; --card: #111; --up: #f87171; --down: #60a5fa; }}
            body {{ background-color: var(--bg); color: var(--gold); font-family: 'Inter', sans-serif; margin: 0; padding: 20px; }}
            .container {{ max-width: 1400px; margin: 0 auto; }}
            header {{ text-align: center; padding: 40px 0; border-bottom: 2px solid var(--gold); margin-bottom: 30px; }}
            h1 {{ font-size: 3vw; text-transform: uppercase; letter-spacing: 4px; margin: 0; }}
            .time {{ color: #888; font-size: 14px; margin-top: 10px; }}
            .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 15px; }}
            .card {{ background: var(--card); padding: 20px; border-radius: 12px; border: 1px solid #333; transition: 0.3s; position: relative; overflow: hidden; }}
            .card:hover {{ border-color: var(--gold); transform: translateY(-5px); box-shadow: 0 5px 15px rgba(251, 191, 36, 0.2); }}
            .name {{ font-size: 16px; font-weight: bold; color: #fff; display: block; margin-bottom: 10px; opacity: 0.8; }}
            .price {{ font-size: 22px; font-weight: 800; display: block; margin-bottom: 8px; color: #fff; }}
            .pct {{ font-size: 15px; font-weight: 600; }}
            .up {{ color: var(--up); }}
            .down {{ color: var(--down); }}
            footer {{ margin-top: 50px; text-align: center; color: #444; font-size: 12px; border-top: 1px solid #222; padding-top: 20px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>CRYPTO TERMINAL</h1>
                <div class="time">REAL-TIME DATA FEED • LAST UPDATE: {now} (KST)</div>
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
            <footer>
                <p>Global Crypto Market Summary © 2025 COIN.US-DIVIDEND-PRO.COM</p>
            </footer>
        </div>
    </body>
    </html>
    """
    return html

if __name__ == "__main__":
    # 파일을 현재 실행 경로에 확실하게 저장
    content = get_data()
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(content)
    
    sitemap = f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://coin.us-dividend-pro.com/</loc><priority>1.0</priority></url></urlset>'
    with open('sitemap.xml', 'w', encoding='utf-8') as f:
        f.write(sitemap)
