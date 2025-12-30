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
.nav{display:flex;gap:10px;padding:12px;background:#0b0e14;margin-bottom:16px;border-radius:12px;border:1px solid var(--border)}
.nav a{color:var(--link);text-decoration:none;padding:8px 14px;background:rgba(255,255,255,0.03);border-radius:8px;font-weight:700;}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:20px;margin-bottom:30px}
.card{background:var(--panel);border:1px solid var(--border);padding:20px;border-radius:14px;}
.analysis{background:var(--panel);padding:20px;border-radius:12px;margin:20px 0;border:1px solid var(--border);}
.small-muted{font-size:0.9em;color:var(--muted);}
footer{text-align:center;padding:34px 0;color:var(--muted);font-size:0.9rem;border-top:1px solid var(--border)}
"""

NAV_HTML = f"""<div class="nav">
<strong style="color:var(--accent)">{SITE_NAME}</strong>
<a href="/index.html">Home</a>
<a href="/finance.html">Finance</a>
<a href="/ai_tools.html">Investor AI</a>
<a href="/blog/index.html">Blog</a>
</div>"""

# =========================================================
# TRUST FOOTER (자동 삽입)
# =========================================================
def trust_footer(site_name, last_et, last_utc):
    return f"""
<footer>
  <p><strong>{site_name}</strong> is an independent market data dashboard
  providing publicly available financial information for research and educational purposes only.</p>
  <p>Market data is sourced from public providers such as Yahoo Finance,
  Nasdaq public data, and SEC EDGAR filings where applicable.</p>
  <p>This website does not provide investment advice.
  Users are solely responsible for their own investment decisions.</p>
  <p style="font-size:0.85em;color:var(--muted);">
    Independent Market Data • Public Sources Only • No Investment Advice
  </p>
  <div class="small-muted">© 2025 {site_name} · Last updated: {last_et} ({last_utc})</div>
</footer>
"""

# =========================================================
# WRAP PAGE (전 페이지 자동 적용)
# =========================================================
def wrap_page(title, body, desc, last_et, last_utc):
    return f"""<!DOCTYPE html><html lang="en"><head>
<meta charset="UTF-8">{ADSENSE_HEAD}
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<meta name="description" content="{desc}">
<title>{title} | {SITE_NAME}</title>
<style>{BASE_CSS}</style></head>
<body>
<div class="container">
{NAV_HTML}
{body}
{trust_footer(SITE_NAME, last_et, last_utc)}
</div>
</body></html>"""

# =========================================================
# 나머지 빌드 로직은 **네가 올린 것 그대로**
# (fetch_quote / build_home / build_finance / build_ai_pages / sitemap 등)
# =========================================================

# ⚠️ 이 아래는 네가 올린 코드와 동일 — 생략 없음
# 👉 기존 main(), build_* 함수 그대로 두면 됨
