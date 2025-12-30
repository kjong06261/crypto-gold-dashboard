import yfinance as yf
import re

# =========================================================
# 1. 100개 데이터 리스트 (이건 그대로 둠)
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
# 2. HTML 생성기
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
# 3. [핵심 수정] 무조건 찾아내는 강력한 함수
# =========================================================
def inject_html_force(filename, target_id, new_content):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            html = f.read()
        
        # 1. 찾을 패턴: <div ... id="target_id" ... > ... </div>
        # class가 앞에 있든 뒤에 있든, id가 어디에 박혀있든 잡아내는 정규식입니다.
        # <div[^>]* : <div로 시작하고 닫는 괄호 전까지 아무거나 옴
        # id="{target_id}" : 그 안에 id="coin-grid"가 있어야 함
        pattern = f'(<div[^>]*id="{target_id}"[^>]*>)(.*?)(</div>)'
        
        # 2. 교체 시도
        if re.search(pattern, html, re.DOTALL):
            # \1 : 원래 있던 오프닝 태그 (<div class="grid" id="...">) 유지
            # new_content : 우리가 만든 카드 100개
            # \3 : </div> 닫는 태그 유지
            updated_html = re.sub(pattern, f'\\1{new_content}\\3', html, flags=re.DOTALL)
            
            with open(filename, "w", encoding="utf-8") as f:
                f.write(updated_html)
            print(f"✅ {filename} : ID '{target_id}' 찾아서 데이터 주입 완료!")
            
        else:
            # 나스닥 같은 tbody 태그용 (혹시 몰라서 남겨둠)
            pattern_tbody = f'(<tbody[^>]*id="{target_id}"[^>]*>)(.*?)(</tbody>)'
            if re.search(pattern_tbody, html, re.DOTALL):
                updated_html = re.sub(pattern_tbody, f'\\1{new_content}\\3', html, flags=re.DOTALL)
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(updated_html)
                print(f"✅ {filename} (Table) : 데이터 주입 완료!")
            else:
                print(f"❌ {filename} 실패: 도저히 ID '{target_id}'를 못 찾겠습니다.")

    except FileNotFoundError:
        print(f"⚠️ {filename} 파일이 없습니다.")

# =========================================================
# 4. 실행
# =========================================================
if __name__ == "__main__":
    print("🚀 데이터 수집 및 주입 시작...")

    # 1. 나스닥
    nasdaq_html = "".join([make_nasdaq_row(s) for s in nasdaq_tickers])
    inject_html_force("index.html", "nasdaq-table", nasdaq_html)
    
    # 2. 코인 (여기가 문제였음 -> 이제 해결됨)
    coin_html = "".join([make_card_html(s) for s in coin_tickers])
    inject_html_force("coin.html", "coin-grid", coin_html)
    
    # 3. 배당주
    div_html = "".join([make_card_html(s) for s in dividend_tickers])
    inject_html_force("dividend.html", "dividend-grid", div_html)
    
    # 4. 상단 지표 (얘네는 단순 id라 잘 됨)
    inject_html_force("index.html", "qqq-price", get_simple_price("QQQ"))
    inject_html_force("index.html", "vix-index", get_simple_price("^VIX"))
    inject_html_force("index.html", "sentiment-score", "GREED (78)")

    print("🏁 모든 작업 끝.")
