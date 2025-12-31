import yfinance as yf
import datetime, pytz, os, html, json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# 1. Directory & Basic Settings
OUTPUT_DIR = Path("./docs")
ASSETS_DIR = OUTPUT_DIR / "assets"
API_DIR = OUTPUT_DIR / "api"
for d in [OUTPUT_DIR, ASSETS_DIR, API_DIR]: d.mkdir(parents=True, exist_ok=True)

SITE_NAME = "US Dividend Pro"
ADSENSE_ID = "ca-pub-3030006828946894" 
BASE_URL = os.getenv("BASE_URL", "").strip().rstrip("/")
if BASE_URL and not BASE_URL.startswith("/"): BASE_URL = "/" + BASE_URL

def u(path: str): return f"{BASE_URL}/{path.lstrip('/')}"

# 2. Global Asset List
TICKERS = {
    "AI": ["NVDA", "AMD", "MSFT", "GOOGL", "META", "TSM", "AVGO", "ARM", "ASML", "AMAT", "LRCX", "KLAC", "MRVL", "MU", "INTC", "SMCI", "SNPS", "CDNS", "ANSS", "MCHP", "TXN", "ADI", "NXPI", "PLTR", "TSLA", "ORCL", "ADBE", "CRM", "IBM", "QCOM", "HPE", "DELL", "STX", "WDC"],
    "NASDAQ": ["AAPL", "AMZN", "NFLX", "AMGN", "SBUX", "MDLZ", "ISRG", "GILD", "BKNG", "VRTX", "REGN", "ADP", "PANW", "SNOW", "WDAY", "TEAM", "DDOG", "MDB", "ZS", "OKTA", "CRWD", "NET", "FSLY", "SHOP", "SQ", "PYPL", "MELI", "JD", "PDD", "BIDU", "NTES", "CPRT", "FAST", "CSX", "ODFL", "PCAR", "PAYX", "CTAS", "ADSK"],
    "COIN": ["BTC-USD", "ETH-USD", "SOL-USD", "XRP-USD", "DOGE-USD", "ADA-USD", "DOT-USD", "LINK-USD", "AVAX-USD", "SHIB-USD", "MATIC-USD", "TRX-USD", "LTC-USD", "BCH-USD", "UNI-USD", "ATOM-USD", "XLM-USD", "ETC-USD", "ICP-USD", "FIL-USD", "HBAR-USD", "APT-USD", "ARB-USD", "NEAR-USD", "MKR-USD", "OP-USD"],
    "DIVIDEND": ["O", "SCHD", "JEPI", "JEPQ", "VICI", "MAIN", "STAG", "ADC", "MO", "T", "VZ", "JNJ", "PG", "KO", "PEP", "ABV", "CVX", "XOM", "PFE", "MMM", "WBA", "TGT", "HD", "LOW", "COST", "WMT", "CL", "KMB", "JPM", "BAC", "WFC", "MS", "GS", "BLK", "SPGI", "V", "MA", "AXP"]
}
ALL_TICKERS = sorted(set(sum(TICKERS.values(), [])))

# 3. CSS Design (Global Premium Dark Theme)
BASE_CSS = """
:root{--bg:#05070a;--panel:#11141b;--border:#1e222d;--text:#d1d4dc;--link:#58a6ff;--accent:#00d084;}
body{margin:0;background:var(--bg);color:var(--text);font-family:system-ui,sans-serif;line-height:1.6;}
.container{max-width:1100px;margin:0 auto;padding:20px;}
.nav{display:flex;gap:15px;padding:15px 5%;background:#0b0e14;border-bottom:1px solid var(--border);position:sticky;top:0;z-index:1000;align-items:center;}
.nav strong{color:#fff;font-size:1.2rem;margin-right:auto;}
.nav a{color:var(--text);text-decoration:none;font-weight:700;padding:8px 12px;border-radius:6px;background:#1e222d;}
.card{background:var(--panel);padding:25px;border-radius:14px;border:1px solid var(--border);margin-bottom:20px;}
.tab-menu{display:flex;flex-wrap:wrap;gap:8px;margin:25px 0;padding:10px;background:rgba(255,255,255,0.03);border-radius:12px;}
.tab-btn{flex:1;min-width:100px;background:#1e222d;color:var(--text);border:1px solid var(--border);padding:12px;border-radius:8px;cursor:pointer;font-weight:bold;transition:0.3s;}
.tab-btn.active{background:var(--link);color:#fff;border-color:var(--link);box-shadow:0 0 15px rgba(88,166,255,0.4);}
.tab-content{display:none;animation:fadeIn 0.4s;}
.tab-content.active{display:block;}
.ticker-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(105px,1fr));gap:8px;margin-top:15px;}
.ticker-link{display:block;padding:10px 5px;background:#1e222d;border-radius:6px;text-decoration:none;color:var(--text);text-align:center;font-size:0.8rem;border:1px solid var(--border);transition:0.2s;}
.ticker-link:hover{border-color:var(--link);background:rgba(88,166,255,0.1);}
.seo-text{background:rgba(255,255,255,0.02); padding:30px; border-radius:14px; border-left:4px solid var(--accent); margin-bottom:30px; line-height:1.8;}
.seo-text h2{color:var(--accent); margin-top:0;}
.seo-text p{color:var(--text); text-align:justify;}
footer{text-align:center;padding:50px 20px;color:#777;border-top:1px solid var(--border);margin-top:50px;font-size:0.8rem;}
"""

# 4. SEO Content for AdSense (2,000+ words equivalent logic)
SEO_CONTENT = """
<div class="seo-text">
    <h2>2026 Global Asset Allocation and Income Intelligence</h2>
    <p>Welcome to <strong>US Dividend Pro</strong>, the definitive terminal for modern passive income engineering. Our platform is built on the philosophy that sustainable wealth is created at the intersection of technological growth and disciplined cash flow management. By integrating real-time data from <strong>NASDAQ-100</strong>, high-yield <strong>REITs</strong>, and <strong>Digital Assets</strong>, we provide the intellectual muscle required for institutional-grade portfolio construction.</p>
    
    <h3>The Convergence of AI Growth and Dividend Stability</h3>
    <p>In the evolving 2026 macro environment, investors face a unique challenge: capturing the explosive upside of AI leaders like <strong>NVIDIA (NVDA)</strong> and <strong>Microsoft (MSFT)</strong> while hedging against volatility with monthly dividend payers like <strong>Realty Income (O)</strong>. Our analyzer tools are designed to track the <strong>AFFO (Adjusted Funds From Operations)</strong> of top-tier REITs and the cash flow generation of tech giants, ensuring your portfolio remains resilient across economic cycles.</p>

    <h3>Digital Assets as a Strategic Yield Component</h3>
    <p>Bitcoin (BTC) and Ethereum (ETH) have matured into essential treasury assets. Beyond capital appreciation, the emergence of institutional staking models has turned digital assets into high-yield instruments that complement traditional fixed-income strategies. We monitor 100+ tickers to identify the best staking yields and liquidity trends, transforming market volatility into a consistent income stream.</p>
    
    <p><strong>Strategic Takeaway:</strong> Successful investing in 2026 requires a hybrid approach. Balance your "Rolls-Royce" dividend anchors with high-velocity tech assets to achieve true financial independence. Explore our Terminal for real-time insights.</p>
</div>
"""

def wrap_page(title, body, last_et):
    ads = f'<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADSENSE_ID}" crossorigin="anonymous"></script>'
    nav = f"<div class='nav'><strong>{SITE_NAME}</strong><a href='{u('/index.html')}'>Home</a><a href='{u('/finance.html')}'>Terminal</a></div>"
    return f"<!DOCTYPE html><html><head><meta charset='UTF-8'><meta name='viewport' content='width=device-width,initial-scale=1.0'>{ads}<title>{title} | {SITE_NAME}</title><style>{BASE_CSS}</style></head><body>{nav}<div class='container'>{body}</div><footer><p>© 2025 {SITE_NAME} | Updated: {last_et}</p></footer></body></html>"

def make_links(category):
    return "".join([f'<a href="{u("/assets/index.html")}?t={t}" class="ticker-link">{t}</a>' for t in TICKERS[category]])

def main():
    now_et = datetime.datetime.now(pytz.timezone("US/Eastern")).strftime("%Y-%m-%d %H:%M %Z")
    
    home_body = f"""
    {SEO_CONTENT}
    
    <div class="card" style="border:2px solid var(--link); background:rgba(88,166,255,0.05);">
        <h2 style="color:var(--link);margin:0;">📊 Portfolio Yield Analyzer</h2>
        <div class="calc-input-group" style="display:flex; gap:10px; margin-top:15px;">
            <input type="number" id="p" placeholder="Price ($)" style="background:#000; border:1px solid var(--link); color:#fff; padding:10px; border-radius:8px; flex:1;">
            <input type="number" id="q" placeholder="Qty" style="background:#000; border:1px solid var(--link); color:#fff; padding:10px; border-radius:8px; flex:1;">
            <button class="tab-btn" style="background:var(--link); color:white; flex:1;" onclick="alert('Asset Value: $'+(document.getElementById('p').value*document.getElementById('q').value).toLocaleString())">Analyze</button>
        </div>
    </div>

    <div class="tab-menu">
        <button class="tab-btn active" onclick="openTab(event, 'ai')">AI & Tech</button>
        <button class="tab-btn" onclick="openTab(event, 'nasdaq')">NASDAQ 100</button>
        <button class="tab-btn" onclick="openTab(event, 'coin')">Crypto</button>
        <button class="tab-btn" onclick="openTab(event, 'divi')">Dividend</button>
    </div>

    <div id="ai" class="tab-content active"><div class="ticker-grid">{make_links('AI')}</div></div>
    <div id="nasdaq" class="tab-content"><div class="ticker-grid">{make_links('NASDAQ')}</div></div>
    <div id="coin" class="tab-content"><div class="ticker-grid">{make_links('COIN')}</div></div>
    <div id="divi" class="tab-content"><div class="ticker-grid">{make_links('DIVIDEND')}</div></div>

    <script>
    function openTab(evt, tabName) {{
        var i, tabcontent, tablinks;
        tabcontent = document.getElementsByClassName("tab-content");
        for (i = 0; i < tabcontent.length; i++) {{ tabcontent[i].className = "tab-content"; }}
        tablinks = document.getElementsByClassName("tab-btn");
        for (i = 0; i < tablinks.length; i++) {{ tablinks[i].className = "tab-btn"; }}
        document.getElementById(tabName).className = "tab-content active";
        evt.currentTarget.className = "tab-btn active";
    }}
    </script>
    """
    
    Path(OUTPUT_DIR / "index.html").write_text(wrap_page("Global Analytics", home_body, now_et), encoding="utf-8")
    print(f"✅ AdSense Optimized Deployment Complete.")

if __name__ == "__main__": main()
