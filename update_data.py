import yfinance as yf
import re

# =========================================================
# 1. 100개씩 꽉 채우기 리스트
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
# 2. HTML 조각 생성기
# =========================================================
def make_nasdaq_row(symbol):
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
        short_name = t.info.get('shortName', symbol)
        if len(short_name) > 15: short_name = short_name[:15] + ".."
        return f"""<tr><td style="color:#fff; font-weight:bold;">{symbol}</td><td style="color:#8b949e;">{short_name}</td><td style="color:#fff;">${price:,.2f}</td><td class="{cls}">{sign}{change:.2f}%</td><td style="color:{sig_color}; font-weight:bold;">{signal}</td></tr>"""
    except: return ""

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
        return f"""<div class="card"><div class="card-header"><span class="symbol" style="font-weight:bold; color:#fff;">{name}</span><span class="pct {cls}" style="float:right;">{sign}{change:.2f}%</span></div><div class="price" style="font-size:1.4em; font-weight:bold; margin-top:5px;">${price:,.2f}</div></div>"""
    except: return ""

def get_simple_price(symbol):
    try:
        t = yf.Ticker(symbol)
        price = t.history(period="1d")['Close'].iloc[-1]
        return f"${price:,.2f}"
    except: return "Loading..."

# =========================================================
# 3. [수정됨] 무식하고 확실한 교체 엔진
# =========================================================
def replace_placeholder(filename, placeholder_text, new_content):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            html = f.read()
        
        # 1. 플레이스홀더 텍스트가 있는지 확인
        if placeholder_text in html:
            # 2. 플레이스홀더를 감싸고 있는 태그 전체를 교체하기 위해 단순 치환 시도
            # (정교한 Regex 대신 텍스트 기반으로 확실하게 찾음)
            
            # 카드의 경우: <div class="card" ...>...Connecting...</div> 이걸 통째로 날리고 new_content로 대체
            # 하지만 안전하게 'ID가 있는 DIV의 내부'를 교체하는 로직을 Regex로 단순화
            
            # 플레이스홀더가 포함된 카드 div 전체를 찾아서 삭제하고 데이터 삽입
            # "Connecting..." 문구가 있는 div를 찾음
            if "Connecting to Blockchain..." in html or "Initializing Data..." in html or "Initializing Real-Time Data Stream..." in html:
                # 해당 문구가 있는 줄이나 블록을 찾기보다, ID 기반으로 다시 시도하되 더 넓게 잡음
                pass

        # ID 기반 교체 (이번엔 더 강력하게)
        # id="coin-grid">  ...  </div>  <-- 이 사이를 싹 비우고 채움
        pattern = f'(id="{placeholder_text}"[^>]*>)(.*?)(</div>)'
        
        # DOTALL 옵션으로 줄바꿈 포함해서 다 잡음
        import re
        if re.search(pattern, html, re.DOTALL):
            updated_html = re.sub(pattern, f'\\1{new_content}\\3', html, flags=re.DOTALL)
            with open(filename, "w", encoding="utf-8") as f:
                f.write(updated_html)
            print(f"✅ {filename} 업데이트 성공!")
        else:
            print(f"❌ {filename} 실패: ID '{placeholder_text}'를 못 찾았습니다.")

    except FileNotFoundError:
        print(f"⚠️ {filename} 파일 없음")

# =========================================================
# 4. 실행
# =========================================================
if __name__ == "__main__":
    print("데이터 수집 중...")

    # 1. 나스닥
    nasdaq_html = "".join([make_nasdaq_row(s) for s in nasdaq_tickers])
    replace_placeholder("index.html", "nasdaq-table", nasdaq_html) # ID: nasdaq-table
    
    # 2. 코인 (여기가 문제였음 -> ID: coin-grid)
    coin_html = "".join([make_card_html(s) for s in coin_tickers])
    replace_placeholder("coin.html", "coin-grid", coin_html)
    
    # 3. 배당주 (ID: dividend-grid)
    div_html = "".join([make_card_html(s) for s in dividend_tickers])
    replace_placeholder("dividend.html", "dividend-grid", div_html)
    
    # 4. 상단 지표
    replace_placeholder("index.html", "qqq-price", get_simple_price("QQQ"))
    replace_placeholder("index.html", "vix-index", get_simple_price("^VIX"))
    replace_placeholder("index.html", "sentiment-score", "GREED (78)")

    print("완료.")
