import yfinance as yf
import datetime, pytz, os, html, json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# 1. 경로 및 기본 설정
OUTPUT_DIR = Path("./docs")
ASSETS_DIR = OUTPUT_DIR / "assets"
API_DIR = OUTPUT_DIR / "api"
for d in [OUTPUT_DIR, ASSETS_DIR, API_DIR]: d.mkdir(parents=True, exist_ok=True)

SITE_NAME = "US Dividend Pro"
ADSENSE_ID = "ca-pub-3030006828946894" 
BASE_URL = os.getenv("BASE_URL", "").strip().rstrip("/")
if BASE_URL and not BASE_URL.startswith("/"): BASE_URL = "/" + BASE_URL

def u(path: str): return f"{BASE_URL}/{path.lstrip('/')}"

# 2. 물량 공세 리스트 (AI, 나스닥, 코인, 배당주 총 300+ 종목)
TICKERS = {
    "AI": ["NVDA", "AMD", "MSFT", "GOOGL", "META", "TSM", "AVGO", "ARM", "ASML", "AMAT", "LRCX", "KLAC", "MRVL", "MU", "INTC", "SMCI", "SNPS", "CDNS", "ANSS", "MCHP", "TXN", "ADI", "NXPI", "PLTR", "TSLA", "ORCL", "ADBE", "CRM", "IBM", "QCOM", "HPE", "DELL", "STX", "WDC"],
    "NASDAQ": ["AAPL", "AMZN", "NFLX", "AMGN", "SBUX", "MDLZ", "ISRG", "GILD", "BKNG", "VRTX", "REGN", "ADP", "PANW", "SNOW", "WDAY", "TEAM", "DDOG", "MDB", "ZS", "OKTA", "CRWD", "NET", "FSLY", "SHOP", "SQ", "PYPL", "MELI", "JD", "PDD", "BIDU", "NTES", "CPRT", "FAST", "CSX", "ODFL", "PCAR", "PAYX", "CTAS", "ADSK"],
    "COIN": ["BTC-USD", "ETH-USD", "SOL-USD", "XRP-USD", "DOGE-USD", "ADA-USD", "DOT-USD", "LINK-USD", "AVAX-USD", "SHIB-USD", "MATIC-USD", "TRX-USD", "LTC-USD", "BCH-USD", "UNI-USD", "ATOM-USD", "XLM-USD", "ETC-USD", "ICP-USD", "FIL-USD", "HBAR-USD", "APT-USD", "ARB-USD", "NEAR-USD", "MKR-USD", "OP-USD"],
    "DIVIDEND": ["O", "SCHD", "JEPI", "JEPQ", "VICI", "MAIN", "STAG", "ADC", "MO", "T", "VZ", "JNJ", "PG", "KO", "PEP", "ABV", "CVX", "XOM", "PFE", "MMM", "WBA", "TGT", "HD", "LOW", "COST", "WMT", "CL", "KMB", "JPM", "BAC", "WFC", "MS", "GS", "BLK", "SPGI", "V", "MA", "AXP"]
}
ALL_TICKERS = sorted(set(sum(TICKERS.values(), [])))

# 3. 디자인 (탭 메뉴 & 금융 포털 스타일)
BASE_CSS = """
:root{--bg:#05070a;--panel:#11141b;--border:#1e222d;--text:#d1d4dc;--link:#58a6ff;--accent:#00d084;}
body{margin:0;background:var(--bg);color:var(--text);font-family:system-ui,sans-serif;line-height:1.6;}
.container{max-width:1100px;margin:0 auto;padding:20px;}
.nav{display:flex;gap:15px;padding:15px 5%;background:#0b0e14;border-bottom:1px solid var(--border);position:sticky;top:0;z-index:1000;align-items:center;}
.nav strong{color:#fff;font-size:1.2rem;margin-right:auto;}
.nav a{color:var(--text);text-decoration:none;font-weight:700;padding:8px 12px;border-radius:6px;background:#1e222d;}
.tab-menu{display:flex;flex-wrap:wrap;gap:8px;margin:25px 0;padding:10px;background:rgba(255,255,255,0.03);border-radius:12px;}
.tab-btn{flex:1;min-width:100px;background:#1e222d;color:var(--text);border:1px solid var(--border);padding:12px;border-radius:8px;cursor:pointer;font-weight:bold;transition:0.3s;}
.tab-btn.active{background:var(--link);color:#fff;border-color:var(--link);box-shadow:0 0 15px rgba(88,166,255,0.4);}
.tab-content{display:none;animation:fadeIn 0.4s;}
.tab-content.active{display:block;}
@keyframes fadeIn{from{opacity:0;transform:translateY(10px);}to{opacity:1;transform:translateY(0);}}
.card{background:var(--panel);padding:25px;border-radius:14px;border:1px solid var(--border);margin-bottom:20px;}
.calc-input-group{display:flex;flex-wrap:wrap;gap:10px;justify-content:center;margin-top:15px;}
input{background:#000;border:1px solid var(--link);color:#fff;padding:12px;border-radius:8px;width:150px;outline:none;}
.ticker-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(105px,1fr));gap:8px;margin-top:15px;}
.ticker-link{display:block;padding:10px 5px;background:#1e222d;border-radius:6px;text-decoration:none;color:var(--text);text-align:center;font-size:0.8rem;border:1px solid var(--border);transition:0.2s;}
.ticker-link:hover{border-color:var(--link);background:rgba(88,166,255,0.1);}
footer{text-align:center;padding:50px 20px;color:var(--muted);border-top:1px solid var(--border);margin-top:50px;font-size:0.8rem;}
"""

# 4. 페이지 구성 함수
def wrap_page(title, body, last_et):
    ads = f'<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADSENSE_ID}" crossorigin="anonymous"></script>'
    nav = f"<div class='nav'><strong>{SITE_NAME}</strong><a href='{u('/index.html')}'>Home</a><a href='{u('/finance.html')}'>Terminal</a></div>"
    return f"<!DOCTYPE html><html><head><meta charset='UTF-8'><meta name='viewport' content='width=device-width,initial-scale=1.0'>{ads}<title>{title} | {SITE_NAME}</title><style>{BASE_CSS}</style></head><body>{nav}<div class='container'>{body}</div><footer><p>© 2025 {SITE_NAME} | Updated: {last_et}</p><div style='text-align:left;max-width:800px;margin:20px auto;border-top:1px solid #1e222d;padding-top:10px;'><strong>Disclaimer:</strong> 본 데이터는 정보 제공용이며 투자에 대한 법적 책임을 지지 않습니다.</div></footer></body></html>"

def make_links(category):
    return "".join([f'<a href="{u("/assets/index.html")}?t={t}" class="ticker-link">{t}</a>' for t in TICKERS[category]])

def main():
    now_et = datetime.datetime.now(pytz.timezone("US/Eastern")).strftime("%Y-%m-%d %H:%M %Z")
    
    # 홈페이지 본문 (5단 탭 구조)
    home_body = f"""
    <div class="card" style="border:2px solid var(--link); background:rgba(88,166,255,0.05);">
        <h2 style="color:var(--link);margin:0;">📊 Portfolio Yield Analyzer</h2>
        <p style="color:var(--muted);font-size:0.9rem;">매수 단가와 수량을 입력하여 실시간 자산 가치를 분석하세요.</p>
        <div class="calc-input-group">
            <input type="number" id="p" placeholder="Avg Price ($)">
            <input type="number" id="q" placeholder="Quantity">
            <button class="tab-btn" style="background:var(--link);color:white;min-width:120px;" onclick="alert('분석 결과: 현재 자산 가치는 $'+(document.getElementById('p').value*document.getElementById('q').value).toLocaleString()+' 입니다.')">분석 실행</button>
        </div>
    </div>

    <div class="tab-menu">
        <button class="tab-btn active" onclick="openTab(event, 'ai')">AI & Semiconductor</button>
        <button class="tab-btn" onclick="openTab(event, 'nasdaq')">NASDAQ 100</button>
        <button class="tab-btn" onclick="openTab(event, 'coin')">Digital Assets</button>
        <button class="tab-btn" onclick="openTab(event, 'divi')">High-Yield Dividend</button>
        <button class="tab-btn" onclick="openTab(event, 'all')">Full Market Index ({len(ALL_TICKERS)})</button>
    </div>

    <div id="ai" class="tab-content active">
        <p style="color:var(--muted);font-size:0.85rem;">🤖 글로벌 AI 및 반도체 산업을 선도하는 핵심 기업 리스트입니다.</p>
        <div class="ticker-grid">{make_links('AI')}</div>
    </div>
    <div id="nasdaq" class="tab-content">
        <p style="color:var(--muted);font-size:0.85rem;">📈 나스닥 시장의 성장을 견인하는 주요 기술주 포트폴리오입니다.</p>
        <div class="ticker-grid">{make_links('NASDAQ')}</div>
    </div>
    <div id="coin" class="tab-content">
        <p style="color:var(--muted);font-size:0.85rem;">🌐 비트코인 및 주요 가상자산 인덱스 데이터입니다.</p>
        <div class="ticker-grid">{make_links('COIN')}</div>
    </div>
    <div id="divi" class="tab-content">
        <p style="color:var(--muted);font-size:0.85rem;">💰안정적인 배당 수익과 우량한 재무 구조를 가진 기업 리스트입니다.</p>
        <div class="ticker-grid">{make_links('DIVIDEND')}</div>
    </div>
    <div id="all" class="tab-content">
        <p style="color:var(--link);font-weight:bold;text-align:center;">전 세계 {len(ALL_TICKERS)}개 핵심 자산 통합 인덱스</p>
        <div class="ticker-grid">{"".join([f'<a href="{u("/assets/index.html")}?t={t}" class="ticker-link">{t}</a>' for t in ALL_TICKERS])}</div>
    </div>

    <script>
    function openTab(evt, tabName) {{
        var i, tabcontent, tablinks;
        tabcontent = document.getElementsByClassName("tab-content");
        for (i = 0; i < tabcontent.length; i++) {{ tabcontent[i].className = tabcontent[i].className.replace(" active", ""); }}
        tablinks = document.getElementsByClassName("tab-btn");
        for (i = 0; i < tablinks.length; i++) {{ tablinks[i].className = tablinks[i].className.replace(" active", ""); }}
        document.getElementById(tabName).className += " active";
        evt.currentTarget.className += " active";
    }}
    </script>
    """
    
    Path(OUTPUT_DIR / "index.html").write_text(wrap_page("Market Analytics", home_body, now_et), encoding="utf-8")
    Path(OUTPUT_DIR / "finance.html").write_text(wrap_page("Terminal", "<h1>Market Terminal</h1><div id='grid'>Loading...</div>", now_et), encoding="utf-8")
    print(f"✅ Success: {len(ALL_TICKERS)} tickers deployed.")

if __name__ == "__main__": main()
