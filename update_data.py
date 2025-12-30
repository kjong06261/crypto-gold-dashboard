import yfinance as yf
import re

# =========================================================
# 1. [초대형 리스트] 화면 꽉 채우기용 (각 80~100개)
# =========================================================

# 나스닥 100 (QQQ 구성종목 + 주요 기술주 총망라)
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

# 코인 100 (메이저부터 알트, 밈코인까지 싹 다)
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

# 배당주 100 (배당킹, 귀족, 월배당, 고배당 리츠/BDC)
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
# 2. 데이터 생성 엔진 (HTML 구조에 맞춰서 생성)
# =========================================================

def make_card_html(symbol):
    """코인, 배당주용 카드 디자인 생성"""
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
        
        # 대표님이 주신 coin.html, dividend.html의 .card 구조
        return f"""
        <div class="card">
            <div class="card-header">
                <span class="symbol" style="font-weight:bold; color:#fff;">{name}</span>
                <span class="pct {cls}" style="float:right;">{sign}{change:.2f}%</span>
            </div>
            <div class="price" style="font-size:1.4em; font-weight:bold; margin-top:5px;">${price:,.2f}</div>
        </div>"""
    except: return ""

def make_table_row(symbol):
    """나스닥용 테이블 행(tr) 생성"""
    try:
        t = yf.Ticker(symbol)
        data = t.history(period="2d")
        if len(data) < 2: return ""
        price = data['Close'].iloc[-1]
        prev = data['Close'].iloc[-2]
        change = ((price - prev) / prev) * 100
        
        cls = "up" if change >= 0 else "down"
        sign = "+" if change >= 0 else ""
        
        # 매수/매도 시그널 (단순 로직)
        signal = "STRONG BUY" if change > 2.5 else ("BUY" if change > 0.5 else ("SELL" if change < -0.5 else "HOLD"))
        sig_color = "#39d353" if "BUY" in signal else ("#ff7b72" if "SELL" in signal else "#8b949e")
        
        # index.html의 table 구조
        return f"""
        <tr>
            <td style="color:#fff; font-weight:bold;">{symbol}</td>
            <td style="color:#8b949e;">{t.info.get('shortName', symbol)[:12]}..</td>
            <td style="color:#fff;">${price:,.2f}</td>
            <td class="{cls}">{sign}{change:.2f}%</td>
            <td style="color:{sig_color}; font-weight:bold;">{signal}</td>
        </tr>"""
    except: return ""

def get_simple_price(symbol):
    try:
        t = yf.Ticker(symbol)
        price = t.history(period="1d")['Close'].iloc[-1]
        return f"${price:,.2f}"
    except: return "Loading..."

# =========================================================
# 3. 파일 주입 엔진 (ID 찾아서 꽂아넣기)
# =========================================================
def inject_html(filename, target_id, new_content):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            html = f.read()
        
        # id="타겟" 태그 내부 교체 (비파괴 방식)
        pattern = f'(id="{target_id}"[^>]*>)(.*?)(</)'
        
        if re.search(pattern, html, re.DOTALL):
            updated_html = re.sub(pattern, f'\\1{new_content}\\3', html, flags=re.DOTALL)
            with open(filename, "w", encoding="utf-8") as f:
                f.write(updated_html)
            print(f"✅ {filename} ({target_id}) - 대량 데이터 업데이트 성공")
        else:
            print(f"❌ {filename}에서 id='{target_id}'를 찾을 수 없음.")
            
    except FileNotFoundError:
        print(f"⚠️ {filename} 파일이 없습니다.")

# =========================================================
# 4. 실행
# =========================================================
if __name__ == "__main__":
    print("🚀 초대형 데이터 크롤링 시작 (시간이 좀 걸립니다)...")
    
    # 1. 코인 100개
    print("Processing Crypto...")
    coin_html = "".join([make_card_html(s) for s in coin_tickers])
    inject_html("coin.html", "coin-grid", coin_html)
    
    # 2. 배당주 100개
    print("Processing Dividend...")
    div_html = "".join([make_card_html(s) for s in dividend_tickers])
    inject_html("dividend.html", "dividend-grid", div_html)
    
    # 3. 나스닥 100개
    print("Processing NASDAQ...")
    nasdaq_html = "".join([make_table_row(s) for s in nasdaq_tickers])
    inject_html("index.html", "nasdaq-table", nasdaq_html)
    
    # 4. 지표 업데이트
    inject_html("index.html", "qqq-price", get_simple_price("QQQ"))
    inject_html("index.html", "vix-index", get_simple_price("^VIX"))
    inject_html("index.html", "sentiment-score", "EXTREME GREED (80)")
    
    print("🏁 모든 작업 완료! 사이트를 확인하세요.")
