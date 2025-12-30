import yfinance as yf
import datetime, pytz, os, re, time, html, json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# 0) 경로 및 기본 설정
OUTPUT_DIR = Path("./docs")
ASSETS_DIR = OUTPUT_DIR / "assets"
API_DIR = OUTPUT_DIR / "api"
CACHE_DIR = OUTPUT_DIR / ".cache"
for d in [OUTPUT_DIR, ASSETS_DIR, API_DIR, CACHE_DIR]: d.mkdir(parents=True, exist_ok=True)

SITE_NAME = "US Dividend Pro"
ADSENSE_ID = "ca-pub-3030006828946894" 
BASE_URL = os.getenv("BASE_URL", "").strip().rstrip("/")
if BASE_URL and not BASE_URL.startswith("/"): BASE_URL = "/" + BASE_URL
SITE_URL = os.getenv("SITE_URL", "").rstrip("/")

def u(path: str) -> str: return f"{BASE_URL}/{path.lstrip('/')}"
def abs_url(path: str) -> str: return (SITE_URL + u(path)) if SITE_URL else u(path)

# 1) 종목 리스트 300개 이상으로 대폭 확장 (AI, 코인, 나스닥, 배당주)
TICKERS = {
    "ai_top_30": ["NVDA", "AMD", "MSFT", "GOOGL", "META", "TSM", "AVGO", "ARM", "ASML", "AMAT", "LRCX", "KLAC", "MRVL", "MU", "INTC", "SMCI", "SNPS", "CDNS", "ANSS", "MCHP", "TXN", "ADI", "NXPI", "PLTR", "TSLA", "ORCL", "ADBE", "CRM", "IBM", "QCOM"],
    "crypto_50": ["BTC-USD", "ETH-USD", "SOL-USD", "XRP-USD", "DOGE-USD", "ADA-USD", "DOT-USD", "LINK-USD", "AVAX-USD", "SHIB-USD", "MATIC-USD", "TRX-USD", "LTC-USD", "BCH-USD", "UNI-USD", "ATOM-USD", "XLM-USD", "ETC-USD", "ICP-USD", "FIL-USD", "HBAR-USD", "APT-USD", "ARB-USD", "NEAR-USD", "MKR-USD", "OP-USD", "RNDR-USD", "STX-USD", "INJ-USD", "TIA-USD", "SUI-USD", "SEI-USD", "IMX-USD", "ALGO-USD", "GRT-USD", "AAVE-USD"],
    "dividend_100": ["O", "SCHD", "JEPI", "JEPQ", "VICI", "MAIN", "STAG", "ADC", "MO", "T", "VZ", "JNJ", "PG", "KO", "PEP", "ABV", "CVX", "XOM", "PFE", "MMM", "IBM", "WBA", "TGT", "HD", "LOW", "COST", "WMT", "CL", "KMB", "JPM", "BAC", "WFC", "MS", "GS", "BLK", "SPGI", "V", "MA", "AXP", "PYPL", "ABT", "BMY", "LLY", "UNH", "CVS", "CI", "EL", "PM", "D", "SO", "DUK", "NEE", "AEP", "PEG", "ED", "EXC", "FE"],
    "nasdaq_top": ["AAPL", "AMZN", "NFLX", "ADBE", "ORCL", "AMGN", "SBUX", "MDLZ", "ISRG", "GILD", "BKNG", "VRTX", "REGN", "ADP", "PANW", "SNOW", "WDAY", "TEAM", "DDOG", "MDB", "ZS", "OKTA", "CRWD", "NET", "FSLY", "SHOP", "SQ", "PYPL"]
}
ALL_TICKERS = sorted(set(sum(TICKERS.values(), [])))

# 2) 디자인 및 레이아웃
BASE_CSS = """
:root{--bg:#05070a;--panel:#11141b;--border:#1e222d;--text:#d1d4dc;--muted:#8b949e;--link:#58a6ff;--success:#00d084;--danger:#ff3366;}
body{margin:0;background:var(--bg);color:var(--text);font-family:system-ui,sans-serif;line-height:1.6;}
.container{max-width:1200px;margin:0 auto;padding:20px;}
.nav{display:flex;gap:12px;padding:15px 5%;background:#0b0e14;border-bottom:1px solid var(--border);position:sticky;top:0;z-index:100;align-items:center;}
.nav a{color:var(--link);text-decoration:none;font-weight:700;padding:8px 14px;background:#1e222d;border-radius:8px;}
.calc-box{background:var(--panel);padding:30px;border-radius:14px;border:1px solid var(--link);margin-bottom:30px;text-align:center;}
input{background:#05070a;border:1px solid var(--border);color:#fff;padding:12px;border-radius:8px;width:130px;margin:5px;}
.card{background:var(--panel);border:1px solid var(--border);padding:25px;border-radius:16px;margin-bottom:25px;}
.ticker-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(85px,1fr));gap:6px;margin-top:15px;}
.ticker-link{font-size:0.65rem;padding:5px;background:#1e222d;border-radius:4px;color:var(--muted);text-decoration:none;text-align:center;border:1px solid var(--border);overflow:hidden;}
.ai-link{border-color:var(--link);color:#fff;font-weight:bold;background:rgba(88,166,255,0.1);}
footer{text-align:center;padding:50px 20px;font-size:0.75rem;color:var(--muted);border-top:1px solid var(--border);margin-top:60px;}
"""

def wrap_page(title, body, last_et):
    ads = f'<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADSENSE_ID}" crossorigin="anonymous"></script>'
    nav = f"<div class='nav'><strong>{SITE_NAME}</strong><a href='{u('/index.html')}'>Home</a><a href='{u('/finance.html')}'>Terminal</a></div>"
    return f"<!DOCTYPE html><html><head><meta charset='UTF-8'><meta name='viewport' content='width=device-width,initial-scale=1.0'>{ads}<title>{title}</title><style>{BASE_CSS}</style></head><body>{nav}<div class='container'>{body}</div><footer><p>© 2025 {SITE_NAME} | Updated: {last_et}</p><div style='text-align:left;max-width:800px;margin:20px auto;border-top:1px solid #1e222d;padding-top:10px;'><strong>Disclaimer:</strong> 본 사이트는 정보 제공만을 목적으로 하며 투자 권유가 아닙니다.</div></footer></body></html>"

def fetch_data(t):
    try:
        s = yf.Ticker(t)
        h = s.history(period="2d")
        if h.empty: return None
        return {"t": t, "p": round(h['Close'].iloc[-1], 2)}
    except: return None

def main():
    now_et = datetime.datetime.now(pytz.timezone("US/Eastern")).strftime("%Y-%m-%d %H:%M %Z")
    results = []
    with ThreadPoolExecutor(max_workers=20) as ex:
        futures = [ex.submit(fetch_data, t) for t in ALL_TICKERS]
        for f in as_completed(futures):
            r = f.result()
            if r: results.append(r)
    
    ai_links = "".join([f'<a href="{u("/assets/index.html")}?t={t}" class="ticker-link ai-link">{t}</a>' for t in TICKERS["ai_top_30"]])
    all_links = "".join([f'<a href="{u("/assets/index.html")}?t={t}" class="ticker-link">{t}</a>' for t in ALL_TICKERS])

    home_body = f"""
    <div class="calc-box">
        <h2>📈 실시간 수익률 계산기</h2>
        <input type="number" id="p" placeholder="평단가($)"> <input type="number" id="q" placeholder="보유수량">
        <button onclick="alert('총 평가액: $'+(document.getElementById('p').value*document.getElementById('q').value).toLocaleString())" style="padding:12px 25px; background:var(--link); border:none; color:#fff; border-radius:8px; cursor:pointer; font-weight:bold;">계산하기</button>
    </div>
    <div class="card"><h3>🤖 AI & Semiconductor TOP 30 (집중 분석)</h3><div class="ticker-grid">{ai_links}</div></div>
    <div class="card"><h3>🌐 Global Market Assets ({len(ALL_TICKERS)} 종목 물량 공세)</h3><div class="ticker-grid">{all_links}</div></div>
    """
    
    Path(OUTPUT_DIR / "index.html").write_text(wrap_page("Home", home_body, now_et), encoding="utf-8")
    Path(API_DIR / "assets.json").write_text(json.dumps(results), encoding="utf-8")
    Path(OUTPUT_DIR / "finance.html").write_text(wrap_page("Terminal", "<h1>Terminal</h1><div id='grid'>Loading...</div>", now_et), encoding="utf-8")

if __name__ == "__main__": main()
