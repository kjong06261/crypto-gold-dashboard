import yfinance as yf
from datetime import datetime

# 코인 데이터로 꽉 채우기
coin_pool = {
    'BTC-USD': 'Bitcoin', 'ETH-USD': 'Ethereum', 'SOL-USD': 'Solana',
    'XRP-USD': 'Ripple', 'ADA-USD': 'Cardano', 'DOGE-USD': 'Dogecoin',
    'DOT-USD': 'Polkadot', 'MATIC-USD': 'Polygon', 'LINK-USD': 'Chainlink',
    'AVAX-USD': 'Avalanche', 'TRX-USD': 'TRON', 'SHIB-USD': 'Shiba Inu'
}

def get_data():
    results = []
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    for s, n in coin_pool.items():
        try:
            t = yf.Ticker(s)
            df = t.history(period='2d')
            cur = df['Close'].iloc[-1]
            prev = df['Close'].iloc[-2]
            pct = ((cur - prev) / prev) * 100
            results.append({'symbol': n, 'price': cur, 'pct': pct})
        except: continue
    
    # 디자인: 골드 & 블랙 (코인 느낌)
    html = f"""
    <body style="background:#000; color:#fbbf24; font-family:sans-serif; text-align:center;">
        <h1 style="color:#fbbf24;">CRYPTO TERMINAL</h1>
        <p>실시간 암호화폐 시세 | {now}</p>
        <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(200px, 1fr)); gap:20px; padding:20px;">
    """
    for item in results:
        color = "#f87171" if item['pct'] >= 0 else "#60a5fa"
        html += f"""
            <div style="background:#111; border:1px solid #fbbf24; padding:20px; border-radius:15px;">
                <h2>{item['symbol']}</h2>
                <div style="font-size:24px; font-weight:bold;">${item['price']:,.2f}</div>
                <div style="color:{color};">{item['pct']:.2f}%</div>
            </div>
        """
    html += "</div></body>"
    return html
# (이하 저장 로직 동일)
