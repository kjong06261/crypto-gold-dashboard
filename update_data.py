import datetime, pytz, os, html, json
from pathlib import Path

# 0) 경로 설정
OUTPUT_DIR = Path("./docs")
for d in [OUTPUT_DIR]: d.mkdir(parents=True, exist_ok=True)

SITE_NAME = "US Dividend Pro"
ADSENSE_ID = "ca-pub-3030006828946894"
BASE_URL = os.getenv("BASE_URL", "").strip().rstrip("/")
if BASE_URL and not BASE_URL.startswith("/"): BASE_URL = "/" + BASE_URL

def u(path: str): return f"{BASE_URL}/{path.lstrip('/')}"

# 1) 종목 리스트 (대표님이 요청하신 4대 카테고리)
TICKERS = {
    "AI": ["NVDA", "AMD", "MSFT", "GOOGL", "META", "TSM", "AVGO", "ARM", "ASML", "AMAT", "LRCX", "KLAC", "MRVL", "MU", "INTC", "SMCI", "SNPS", "CDNS", "ANSS", "MCHP", "TXN", "ADI", "NXPI", "PLTR", "TSLA", "ORCL", "ADBE", "CRM", "IBM", "QCOM"],
    "NASDAQ": ["AAPL", "AMZN", "NFLX", "ADBE", "ORCL", "AMGN", "SBUX", "MDLZ", "ISRG", "GILD", "BKNG", "VRTX", "REGN", "ADP", "PANW", "SNOW", "WDAY", "TEAM", "DDOG", "MDB", "ZS", "OKTA", "CRWD", "NET", "FSLY", "SHOP", "SQ", "PYPL"],
    "COIN": ["BTC-USD", "ETH-USD", "SOL-USD", "XRP-USD", "DOGE-USD", "ADA-USD", "DOT-USD", "LINK-USD", "AVAX-USD", "SHIB-USD", "MATIC-USD", "TRX-USD", "LTC-USD", "BCH-USD", "UNI-USD", "ATOM-USD", "XLM-USD", "ETC-USD", "ICP-USD", "FIL-USD"],
    "DIVIDEND": ["O", "SCHD", "JEPI", "JEPQ", "VICI", "MAIN", "STAG", "ADC", "MO", "T", "VZ", "JNJ", "PG", "KO", "PEP", "ABV", "CVX", "XOM", "PFE", "MMM", "WBA", "TGT", "HD", "LOW", "COST", "WMT", "CL", "KMB", "JPM", "BAC", "WFC", "MS", "GS", "BLK", "SPGI", "V", "MA", "AXP"]
}

# 2) 디자인 및 탭 로직 (CSS/JS)
BASE_CSS = """
:root{--bg:#05070a;--panel:#11141b;--border:#1e222d;--text:#d1d4dc;--link:#58a6ff;--accent:#00d084;}
body{margin:0;background:var(--bg);color:var(--text);font-family:system-ui,sans-serif;}
.container{max-width:1000px;margin:0 auto;padding:20px;}
.nav{display:flex;gap:15px;padding:15px 5%;background:#0b0e14;border-bottom:1px solid var(--border);sticky:top;z-index:100;}
.nav a{color:var(--text);text-decoration:none;font-weight:700;}
/* 탭 메뉴 스타일 */
.tab-menu{display:flex;flex-wrap:wrap;gap:10px;margin:20px 0;border-bottom:1px solid var(--border);padding-bottom:10px;}
.tab-btn{background:#1e222d;color:var(--text);border:1px solid var(--border);padding:10px 20px;border-radius:8px;cursor:pointer;font-weight:bold;}
.tab-btn.active{background:var(--link);color:#fff;border-color:var(--link);}
.tab-content{display:none;animation:fadeIn 0.3s;}
.tab-content.active{display:block;}
@keyframes fadeIn{from{opacity:0;}to{opacity:1;}}
/* 계산기/카드 스타일 */
.card{background:var(--panel);padding:25px;border-radius:12px;border:1px solid var(--border);margin-bottom:20px;}
input{background:#000;border:1px solid var(--link);color:#fff;padding:12px;border-radius:8px;width:130px;margin:5px;}
.ticker-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(100px,1fr));gap:8px;}
.ticker-link{display:block;padding:10px;background:#1e222d;border-radius:6px;text-decoration:none;color:var(--text);text-align:center;font-size:0.8rem;border:1px solid var(--border);}
"""

TAB_JS = """
function openTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.getElementById(tabName).classList.add('active');
    event.currentTarget.classList.add('active');
}
"""

def make_links(category):
    return "".join([f'<a href="{u("/assets/index.html")}?t={t}" class="ticker-link">{t}</a>' for t in TICKERS[category]])

def main():
    now_et = datetime.datetime.now(pytz.timezone("US/Eastern")).strftime("%Y-%m-%d %H:%M %Z")
    
    home_body = f"""
    <div class="tab-menu">
        <button class="tab-btn active" onclick="openTab('calc')">계산기</button>
        <button class="tab-btn" onclick="openTab('ai')">AI 30</button>
        <button class="tab-btn" onclick="openTab('nasdaq')">나스닥</button>
        <button class="tab-btn" onclick="openTab('coin')">코인</button>
        <button class="tab-btn" onclick="openTab('divi')">배당주</button>
    </div>

    <div id="calc" class="tab-content active">
        <div class="card">
            <h2>📈 실시간 수익률 계산기</h2>
            <input type="number" id="p" placeholder="평단가($)">
            <input type="number" id="q" placeholder="보량">
            <button class="tab-btn" style="background:var(--link);color:white;" onclick="alert('예상 금액: $'+(document.getElementById('p').value*document.getElementById('q').value))">계산</button>
        </div>
    </div>

    <div id="ai" class="tab-content"><div class="ticker-grid">{make_links('AI')}</div></div>
    <div id="nasdaq" class="tab-content"><div class="ticker-grid">{make_links('NASDAQ')}</div></div>
    <div id="coin" class="tab-content"><div class="ticker-grid">{make_links('COIN')}</div></div>
    <div id="divi" class="tab-content"><div class="ticker-grid">{make_links('DIVIDEND')}</div></div>
    <script>{TAB_JS}</script>
    """
    
    html_content = f"""<!DOCTYPE html><html><head><meta charset='UTF-8'><meta name='viewport' content='width=device-width,initial-scale=1.0'>
    <title>{SITE_NAME}</title><style>{BASE_CSS}</style></head>
    <body><div class='nav'><strong>{SITE_NAME}</strong><a href='{u('/index.html')}'>Home</a><a href='{u('/finance.html')}'>Terminal</a></div>
    <div class='container'>{home_body}</div></body></html>"""
    
    Path(OUTPUT_DIR / "index.html").write_text(html_content, encoding="utf-8")
    Path(OUTPUT_DIR / "finance.html").write_text("Terminal Page", encoding="utf-8")

if __name__ == "__main__": main()
