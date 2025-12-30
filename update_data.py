import yfinance as yf
import pandas as pd
import datetime, time
import pytz
from pathlib import Path

# =========================================================
# 0) Paths / Site
# =========================================================
OUTPUT_DIR = Path("./docs")
ASSETS_DIR = OUTPUT_DIR / "assets"
AI_DIR = OUTPUT_DIR / "ai"
BLOG_DIR = OUTPUT_DIR / "blog"
for d in [OUTPUT_DIR, ASSETS_DIR, AI_DIR, BLOG_DIR]:
    d.mkdir(parents=True, exist_ok=True)

CUSTOM_DOMAIN = "us-dividend-pro.com"
BASE_URL = f"https://{CUSTOM_DOMAIN}"
SITE_NAME = "US Market Terminals"

ADSENSE_HEAD = """<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3030006828946894" crossorigin="anonymous"></script>"""
ADS_TXT_LINE = "google.com, pub-3030006828946894, DIRECT, f08c47fec0942fa0"

# =========================================================
# 1) Tickers
# =========================================================
CRYPTO_TICKERS = ["BTC-USD", "ETH-USD"]

NASDAQ_TICKERS = [
    "AAPL","MSFT","NVDA","TSLA","AMZN","GOOGL","META","AVGO","AMD","QCOM","INTC","MU","ADBE","ORCL","CRM"
]

DIVIDEND_TICKERS = [
    "O","SCHD","JEPI","VICI","MAIN","STAG","ADC","MO","T","VZ","PG","KO","PEP","JNJ","PFE","ABBV","XOM"
]

ETF_TICKERS = [
    "SPY","QQQ","VTI","VOO","IVV","DIA","IWM","VGT","XLK","XLV","XLF","XLP","XLE","XLU","XLRE","XLY","XLB"
]

# =========================================================
# 2) AI Tools
# =========================================================
AI_TOOLS_30 = [
    {"id":"perplexity-pro","name":"Perplexity Pro","cat":"Research","price":"$20/mo","str":"Real-time news & citations","use":"Market investigation"},
    {"id":"claude-3-5-sonnet","name":"Claude 3.5 Sonnet","cat":"Analysis","price":"$20/mo","str":"Logical reasoning & risk","use":"Financial analysis"},
    {"id":"deepseek-v3","name":"DeepSeek V3","cat":"Code/Data","price":"$0.01/task","str":"Unmatched cost-efficiency","use":"Quant development"},
    {"id":"gpt-4o","name":"GPT-4o","cat":"Multi-modal","price":"$20/mo","str":"Creative reports & vision","use":"Report writing"},
    {"id":"gemini-pro","name":"Gemini Pro","cat":"Verification","price":"Free/Paid","str":"Google ecosystem sync","use":"Result validation"},
] + [{"id":f"tool-{i}","name":f"FinTech AI {i}","cat":"Investing","price":"$10/mo","str":f"Feature {i}","use":f"Use case {i}"} for i in range(6,31)]

# =========================================================
# 3) Theme
# =========================================================
BASE_CSS = """
:root{--bg:#05070a;--panel:#11141b;--border:#1e222d;--text:#d1d4dc;--muted:#8b949e;--link:#58a6ff;--accent:#fbbf24;--success:#00d084;--danger:#ff3366;}
body{margin:0;padding:18px;background:var(--bg);color:var(--text);font-family:system-ui,sans-serif;line-height:1.6;}
.container{max-width:1200px;margin:0 auto}
.nav{display:flex;flex-wrap:wrap;gap:10px;padding:12px;background:#0b0e14;margin-bottom:16px;border-radius:12px;border:1px solid var(--border);align-items:center}
.nav a{color:var(--link);text-decoration:none;padding:8px 14px;background:rgba(255,255,255,0.03);border-radius:8px;font-weight:700;}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:20px;margin-bottom:30px}
.card{background:var(--panel);border:1px solid var(--border);padding:20px;border-radius:14px;}
.analysis{background:var(--panel);padding:20px;border-radius:12px;margin:20px 0;border:1px solid var(--border);}
.small-muted{font-size:0.9em;color:var(--muted);}
footer{text-align:center;padding:34px 0;color:var(--muted);font-size:0.9rem;border-top:1px solid var(--border)}
table{width:100%;border-collapse:collapse;margin:15px 0}
th,td{padding:12px;text-align:left;border-bottom:1px solid var(--border)}
th{background:#0b0e14;color:var(--accent)}
"""

NAV_HTML = f"""<div class="nav">
<strong style="color:var(--accent);font-size:1.05em">{SITE_NAME}</strong>
<a href="/index.html">Home</a>
<a href="/finance.html">Finance</a>
<a href="/ai_tools.html">Investor AI</a>
<a href="/blog/index.html">Blog</a>
</div>"""

# =========================================================
# 4) Page Wrapper (🔥 여기서 footer 자동 삽입)
# =========================================================
def wrap_page(title: str, body: str, desc: str, last_et: str, last_utc: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
{ADSENSE_HEAD}
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<meta name="description" content="{desc}">
<title>{title} | {SITE_NAME}</title>
<style>{BASE_CSS}</style>
</head>
<body>
<div class="container">

{NAV_HTML}

{body}

<footer>
  <div style="max-width:900px;margin:0 auto;">
    <p>
      <strong>{SITE_NAME}</strong> is an independent market data dashboard
      providing publicly available financial information for research and
      educational purposes only.
    </p>
    <p>
      Market data is sourced from public providers such as Yahoo Finance,
      Nasdaq public market data, and SEC EDGAR filings where applicable.
    </p>
    <p>
      This website does not provide investment advice.
      Users are solely responsible for their own investment decisions.
    </p>
    <p style="font-size:0.85em;color:var(--muted);">
      Independent Market Data • Public Sources Only • No Investment Advice
    </p>
    <div class="small-muted">
      © 2025 {SITE_NAME} · Last updated: {last_et} ({last_utc})
    </div>
  </div>
</footer>

</div>
</body>
</html>"""

# =========================================================
# 5) Helpers
# =========================================================
def should_update_stocks(now_et: datetime.datetime) -> bool:
    if now_et.weekday() >= 5:
        return False
    return now_et.minute == 0

def safe_float(x, default=0.0):
    try:
        return float(x)
    except:
        return default

def fetch_quote(ticker: str):
    stock = yf.Ticker(ticker)
    info = {}
    try:
        info = stock.info or {}
    except:
        pass

    price = safe_float(info.get("currentPrice", info.get("regularMarketPrice", 0)))
    change_pct = safe_float(info.get("regularMarketChangePercent", 0))
    div_y = info.get("dividendYield", 0)
    div_yield_pct = safe_float(div_y, 0) * 100 if div_y else 0.0

    if price == 0:
        try:
            h = stock.history(period="1d", interval="1m")
            if not h.empty:
                price = float(h["Close"].iloc[-1])
        except:
            pass

    return {"price": price, "change_pct": change_pct, "div_yield_pct": div_yield_pct}

# =========================================================
# 6) Builders (home / finance / assets / ai / blog)
# =========================================================
def build_home(update_stocks: bool, last_et: str, last_utc: str):
    status = "Stocks updating" if update_stocks else "Crypto-only update"
    body = f"""
<h1>US Market Terminals</h1>
<p class="small-muted">{status}</p>
"""
    (OUTPUT_DIR / "index.html").write_text(
        wrap_page("Home", body, "Market overview dashboard.", last_et, last_utc),
        encoding="utf-8"
    )

# (⚠️ 나머지 build_finance_page, build_asset_page, build_ai_pages,
#  build_blog, sitemap, main()은 네가 올린 기존 코드 그대로 두면 된다)
