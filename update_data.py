import yfinance as yf

# =========================================================
# 1. 종목 리스트 (각 100개)
# =========================================================
nasdaq_tickers = [
    'AAPL', 'MSFT', 'NVDA', 'GOOGL', 'AMZN', 'META', 'TSLA', 'AVGO', 'ASML', 'COST',
    'PEP', 'NFLX', 'AMD', 'LIN', 'ADBE', 'AZN', 'QCOM', 'TMUS', 'CSCO', 'INTU',
    'TXN', 'CMCSA', 'AMGN', 'INTC', 'HON', 'AMAT', 'BKNG', 'ISRG', 'ADI', 'GILD',
    'VRTX', 'LRCX', 'REGN', 'MDLZ', 'PANW', 'SNPS', 'KLAC', 'CDNS', 'CHTR', 'PDD',
    'MAR', 'ORCL', 'MELI', 'CRWD', 'CTAS', 'CSX', 'PYPL', 'MNST', 'WDAY', 'ROP',
    'LULU', 'NXPI', 'AEP', 'DXCM', 'MRVL', 'ADSK', 'MCHP', 'CPRT', 'KDP', 'PAYX',
    'PCAR', 'ROST', 'SBUX', 'IDXX', 'FTNT', 'ODFL', 'FAST', 'EA', 'KHC', 'VRSK',
    'BKR', 'EXC', 'CTSH', 'GEHC', 'XEL', 'CSGP', 'ON', 'GFS', 'TEAM', 'CDW',
    'TTWO', 'DLTR', 'ANSS', 'WBD', 'BIIB', 'FANG', 'SPLK', 'ILMN', 'SIRI', 'EBAY',
    'ZM', 'ALGN', 'JD', 'LCID', 'RIVN', 'SOFI', 'PLTR', 'ARM', 'CART', 'KVUE'
]

coin_tickers = [
    'BTC-USD', 'ETH-USD', 'SOL-USD', 'BNB-USD', 'XRP-USD', 'ADA-USD', 'DOGE-USD', 'AVAX-USD', 'TRX-USD', 'LINK-USD',
    'DOT-USD', 'MATIC-USD', 'LTC-USD', 'BCH-USD', 'SHIB-USD', 'UNI-USD', 'ATOM-USD', 'XLM-USD', 'ETC-USD', 'FIL-USD',
    'HBAR-USD', 'ICP-USD', 'APT-USD', 'LDO-USD', 'ARB-USD', 'NEAR-USD', 'QNT-USD', 'VET-USD', 'MKR-USD', 'GRT-USD',
    'OP-USD', 'AAVE-USD', 'ALGO-USD', 'AXS-USD', 'SAND-USD', 'EGLD-USD', 'EOS-USD', 'STX-USD', 'SNX-USD', 'IMX-USD',
    'THETA-USD', 'XTZ-USD', 'APE-USD', 'MANA-USD', 'FTM-USD', 'RNDR-USD', 'INJ-USD', 'NEO-USD', 'FLOW-USD', 'KAVA-USD',
    'CHZ-USD', 'GALA-USD', 'CFX-USD', 'PEPE-USD', 'CRV-USD', 'KLAY-USD', 'ZEC-USD', 'IOTA-USD', 'MINA-USD', 'FRAX-USD',
    'SUI-USD', 'CAKE-USD', 'GMX-USD', 'COMP-USD', 'DASH-USD', 'LUNC-USD', 'XEC-USD', 'RPL-USD', 'FXS-USD', 'HOT-USD',
    'ZIL-USD', 'WLD-USD', 'SEI-USD', 'GAS-USD', 'TWT-USD', 'AR-USD', '1INCH-USD', 'QTUM-USD', 'JASMY-USD', 'ENJ-USD',
    'BAT-USD', 'MEME-USD', 'BONK-USD', 'FLOKI-USD', 'ORDI-USD', 'SATS-USD', 'BLUR-USD', 'GMT-USD', 'KSM-USD', 'LRC-USD'
]

dividend_tickers = [
    'O', 'SCHD', 'JEPI', 'JEPQ', 'VICI', 'MAIN', 'STAG', 'ADC', 'MO', 'T',
    'VZ', 'BTI', 'PFE', 'MMM', 'KO', 'PEP', 'PG', 'JNJ', 'ABBV', 'CVX',
    'XOM', 'CSCO', 'IBM', 'TXN', 'QCOM', 'ARCC', 'HTGC', 'OBDC', 'PSEC', 'EPR',
    'ABR', 'HRZN', 'GAIN', 'GLAD', 'LTC', 'OHI', 'MPW', 'NNN', 'WPC', 'IRM',
    'DLR', 'PSA', 'SPG', 'PLD', 'CCI', 'AMT', 'WELL', 'VTR', 'ARE', 'ESS',
    'MAA', 'SUI', 'AVB', 'EQR', 'UDR', 'CPT', 'EXR', 'CUBE', 'LAMR', 'OUT',
    'KMI', 'WMB', 'EPD', 'ET', 'MPLX', 'OKE', 'TRP', 'ENB', 'PPL', 'SO',
    'DUK', 'D', 'NEE', 'AEP', 'ED', 'PEG', 'SRE', 'XEL', 'WEC', 'ES',
    'PM', 'UVV', 'LEG', 'BEN', 'SWK', 'TROW', 'GPC', 'DOV', 'EMR', 'ITW',
    'LOW', 'TGT', 'WMT', 'HD', 'MCD', 'YUM', 'GIS', 'K', 'CL', 'KMB'
]

# =========================================================
# 2. 디자인 템플릿 (파일 전체를 여기서 정의)
# =========================================================

# [코인 페이지 디자인]
COIN_TEMPLATE_HEAD = """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PREMIUM CRYPTO TERMINAL</title>
    <style>
        :root { --bg: #05070a; --card-bg: #11141b; --border: #1e222d; --text: #d1d4dc; --accent: #fbbf24; }
        body { background-color: var(--bg); color: var(--text); font-family: 'Trebuchet MS', sans-serif; margin: 0; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        header { border-bottom: 2px solid var(--accent); padding-bottom: 20px; margin-bottom: 40px; }
        h1 { font-size: 38px; color: #ffffff; margin: 0; letter-spacing: -1px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 12px; }
        .card { background: var(--card-bg); border: 1px solid var(--border); padding: 15px; border-radius: 6px; }
        .card:hover { background: #1c212d; border-color: var(--accent); }
        .card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
        .symbol { font-weight: bold; font-size: 16px; color: #fff; }
        .price { font-size: 24px; font-weight: 700; color: #ffffff; }
        .pct { font-size: 13px; font-weight: bold; padding: 2px 6px; border-radius: 4px; }
        .up { color: #00ffaa; background: rgba(0, 255, 170, 0.1); }
        .down { color: #ff3b3b; background: rgba(255, 59, 59, 0.1); }
        footer { margin-top: 80px; padding: 40px; text-align: center; font-size: 0.8rem; color: #8b949e; border-top: 1px solid var(--border); }
    </style>
</head>
<body>
    <div class="container">
        <header><h1>CRYPTO GOLD TERMINAL</h1><div style="color:#888;">REAL-TIME BLOCKCHAIN FEED • TOP 100 ASSETS</div></header>
        <h2 style="color:var(--accent); border-left:4px solid var(--accent); padding-left:10px;">GLOBAL CRYPTO MARKET (TOP 100)</h2>
        <div class="grid">
"""

# [배당주 페이지 디자인]
DIV_TEMPLATE_HEAD = """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PREMIUM DIVIDEND TERMINAL</title>
    <style>
        :root { --bg: #05070a; --card-bg: #11141b; --border: #1e222d; --text: #d1d4dc; --accent: #00ffaa; }
        body { background-color: var(--bg); color: var(--text); font-family: 'Trebuchet MS', sans-serif; margin: 0; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        header { border-bottom: 2px solid var(--accent); padding-bottom: 20px; margin-bottom: 40px; }
        h1 { font-size: 38px; color: #ffffff; margin: 0; letter-spacing: -1px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 12px; }
        .card { background: var(--card-bg); border: 1px solid var(--border); padding: 15px; border-radius: 6px; }
        .card:hover { background: #1c212d; border-color: var(--accent); }
        .card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
        .symbol { font-weight: bold; font-size: 16px; color: #fff; }
        .price { font-size: 24px; font-weight: 700; color: #ffffff; }
        .pct { font-size: 13px; font-weight: bold; padding: 2px 6px; border-radius: 4px; }
        .up { color: #00ffaa; background: rgba(0, 255, 170, 0.1); }
        .down { color: #ff3b3b; background: rgba(255, 59, 59, 0.1); }
        footer { margin-top: 80px; padding: 40px; text-align: center; font-size: 0.8rem; color: #8b949e; border-top: 1px solid var(--border); }
    </style>
</head>
<body>
    <div class="container">
        <header><h1>DIVIDEND TERMINAL PRO</h1><div style="color:#888;">LIVE MARKET DATA • REAL-TIME FEED</div></header>
        <h2 style="color:var(--accent); border-left:4px solid var(--accent); padding-left:10px;">DIVIDEND KINGS (TOP 100)</h2>
        <div class="grid">
"""

FOOTER = """        </div>
        <footer>
            <div style="margin-bottom:20px;"><strong>⚠️ INVESTMENT DISCLAIMER</strong><br>Data provided is for informational purposes only. Invest at your own risk.</div>
            <div>© 2025 US-DIVIDEND-PRO. All rights reserved.</div>
        </footer>
    </div>
</body>
</html>"""

# [나스닥 인덱스 페이지 디자인]
INDEX_TEMPLATE_HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>NASDAQ Real-Time Terminal</title>
    <style>
        body { background: #0b0e14; color: #e2e8f0; font-family: sans-serif; padding: 20px; margin: 0; }
        .dashboard { max-width: 1200px; margin: 0 auto; background: #161b22; border: 1px solid #30363d; padding: 30px; border-radius: 12px; }
        .grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 30px; }
        .stat-card { background: #0d1117; padding: 20px; border-radius: 8px; border-top: 4px solid #00ff88; }
        .stat-title { color: #8b949e; font-size: 0.9rem; margin-bottom: 5px; }
        .price { font-size: 2rem; font-weight: bold; color: #ffffff; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 0.95rem; }
        th { background: #21262d; color: #8b949e; padding: 15px; text-align: left; border-bottom: 2px solid #30363d; }
        td { padding: 12px 15px; border-bottom: 1px solid #30363d; }
        tr:hover { background: #21262d; }
        .up { color: #39d353; font-weight: bold; } 
        .down { color: #ff7b72; font-weight: bold; }
        footer { margin-top: 60px; padding-top: 30px; border-top: 1px solid #30363d; color: #8b949e; font-size: 0.8rem; text-align: center; }
    </style>
</head>
<body>
    <div class="dashboard">
        <h1>🚀 NASDAQ-100 Live Intelligence</h1>
        <div class="grid">
            <div class="stat-card"><div class="stat-title">QQQ Price</div><div class="price">{qqq_price}</div></div>
            <div class="stat-card" style="border-top-color:#58a6ff;"><div class="stat-title">Sentiment</div><div class="price">GREED (78)</div></div>
            <div class="stat-card" style="border-top-color:#e3b341;"><div class="stat-title">VIX Index</div><div class="price">{vix_price}</div></div>
        </div>
        <h3>Top Technology Constituents</h3>
        <table>
            <thead><tr><th>Ticker</th><th>Name</th><th>Price ($)</th><th>Change (%)</th><th>Signal</th></tr></thead>
            <tbody>
"""

INDEX_TEMPLATE_FOOTER = """            </tbody>
        </table>
        <footer>
            <strong>⚠️ INVESTMENT DISCLAIMER</strong><br>The data provided is for informational purposes only.<br>
            © 2025 US-DIVIDEND-PRO. All rights reserved.
        </footer>
    </div>
</body>
</html>"""

# =========================================================
# 3. 데이터 생성 함수들
# =========================================================
def make_card_html(symbol):
    try:
        t = yf.Ticker(symbol)
        data = t.history(period="2d")
        if len(data) < 2: return ""
        price = data['Close'].iloc[-1]
        prev = data['Close'].iloc[-2]
        change = ((price - prev) / prev) * 100
        cls = "up" if change >= 0 else "down"
        sign = "+" if change >= 0 else ""
        name = symbol.replace("-USD", "")
        
        return f"""
        <div class="card">
            <div class="card-header">
                <span class="symbol">{name}</span>
                <span class="pct {cls}">{sign}{change:.2f}%</span>
            </div>
            <div class="price">${price:,.2f}</div>
        </div>"""
    except: return ""

def make_table_row(symbol):
    try:
        t = yf.Ticker(symbol)
        data = t.history(period="2d")
        if len(data) < 2: return ""
        price = data['Close'].iloc[-1]
        prev = data['Close'].iloc[-2]
        change = ((price - prev) / prev) * 100
        cls = "up" if change >= 0 else "down"
        sign = "+" if change >= 0 else ""
        signal = "STRONG BUY" if change > 2 else ("BUY" if change > 0.5 else ("SELL" if change < -0.5 else "HOLD"))
        sig_color = "#39d353" if "BUY" in signal else ("#ff7b72" if "SELL" in signal else "#8b949e")
        short_name = t.info.get('shortName', symbol)[:15] + ".." if t.info.get('shortName') else symbol

        return f"""
        <tr>
            <td style="color:#fff; font-weight:bold;">{symbol}</td>
            <td style="color:#8b949e;">{short_name}</td>
            <td style="color:#fff;">${price:,.2f}</td>
            <td class="{cls}">{sign}{change:.2f}%</td>
            <td style="color:{sig_color}; font-weight:bold;">{signal}</td>
        </tr>"""
    except: return ""

def get_price(symbol):
    try:
        t = yf.Ticker(symbol)
        return f"${t.history(period='1d')['Close'].iloc[-1]:,.2f}"
    except: return "Loading..."

# =========================================================
# 4. 실행 (파일 덮어쓰기 모드)
# =========================================================
if __name__ == "__main__":
    print("🚀 데이터 수집 및 파일 재생성 시작...")

    # 1. 코인 페이지 생성 (coin.html)
    print("Processing Coin...")
    coin_data = "".join([make_card_html(s) for s in coin_tickers])
    with open("coin.html", "w", encoding="utf-8") as f:
        f.write(COIN_TEMPLATE_HEAD + coin_data + FOOTER)
    
    # 2. 배당주 페이지 생성 (dividend.html)
    print("Processing Dividend...")
    div_data = "".join([make_card_html(s) for s in dividend_tickers])
    with open("dividend.html", "w", encoding="utf-8") as f:
        f.write(DIV_TEMPLATE_HEAD + div_data + FOOTER)

    # 3. 나스닥 페이지 생성 (index.html)
    print("Processing Nasdaq...")
    nasdaq_data = "".join([make_table_row(s) for s in nasdaq_tickers])
    qqq = get_price("QQQ")
    vix = get_price("^VIX")
    
    # 지표 값 채워서 헤더 완성
    final_index_head = INDEX_TEMPLATE_HEAD.replace("{qqq_price}", qqq).replace("{vix_price}", vix)
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(final_index_head + nasdaq_data + INDEX_TEMPLATE_FOOTER)

    print("🏁 모든 파일 재생성 및 업데이트 완료!")
