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
# 1) Tickers: NASDAQ / Dividend / ETF / Crypto
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
# 2) AI Tools (30)
# =========================================================
AI_TOOLS_30 = [
    {"id":"perplexity-pro","name":"Perplexity Pro","cat":"Research","price":"$20/mo","str":"Real-time news & citations","use":"Market investigation"},
    {"id":"claude-3-5-sonnet","name":"Claude 3.5 Sonnet","cat":"Analysis","price":"$20/mo","str":"Logical reasoning & risk","use":"Financial analysis"},
    {"id":"deepseek-v3","name":"DeepSeek V3","cat":"Code/Data","price":"$0.01/task","str":"Unmatched cost-efficiency","use":"Quant development"},
    {"id":"gpt-4o","name":"GPT-4o","cat":"Multi-modal","price":"$20/mo","str":"Creative reports & vision","use":"Report writing"},
    {"id":"gemini-pro","name":"Gemini Pro","cat":"Verification","price":"Free/Paid","str":"Google ecosystem sync","use":"Result validation"},
] + [{"id":f"tool-{i}","name":f"FinTech AI {i}","cat":"Investing","price":"$10/mo","str":f"Feature {i}","use":f"Use case {i}"} for i in range(6,31)]

# =========================================================
# 3) Theme (dark gold)
# =========================================================
BASE_CSS = """
:root{--bg:#05070a;--panel:#11141b;--border:#1e222d;--text:#d1d4dc;--muted:#8b949e;--link:#58a6ff;--accent:#fbbf24;--success:#00d084;--danger:#ff3366;}
body{margin:0;padding:18px;background:var(--bg);color:var(--text);font-family:system-ui,sans-serif;line-height:1.6;}
.container{max-width:1200px;margin:0 auto}
.nav{display:flex;flex-wrap:wrap;gap:10px;padding:12px;background:#0b0e14;margin-bottom:16px;border-radius:12px;border:1px solid var(--border);align-items:center}
.nav a{color:var(--link);text-decoration:none;padding:8px 14px;background:rgba(255,255,255,0.03);border-radius:8px;font-weight:700;}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:20px;margin-bottom:30px}
.card{background:var(--panel);border:1px solid var(--border);padding:20px;border-radius:14px;transition:0.2s;}
.card:hover{border-color:var(--accent);transform:translateY(-2px);}
.analysis{background:var(--panel);padding:20px;border-radius:12px;margin:20px 0;border:1px solid var(--border);}
.small-muted{font-size:0.9em;color:var(--muted);margin-top:6px;}
.badge{display:inline-block;padding:3px 10px;border-radius:999px;font-size:0.85em;background:rgba(255,255,255,0.06);border:1px solid var(--border);color:var(--text)}
h1,h2,h3{margin:10px 0;}
hr{border:0;border-top:1px solid var(--border);margin:18px 0;}
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

def wrap_page(title: str, body: str, desc: str, last_et: str, last_utc: str) -> str:
    return f"""<!DOCTYPE html><html lang="en"><head>
<meta charset="UTF-8">{ADSENSE_HEAD}
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<meta name="description" content="{desc}">
<title>{title} | {SITE_NAME}</title>
<style>{BASE_CSS}</style></head>
<body><div class="container">{NAV_HTML}{body}
<footer>© 2025 {SITE_NAME} · Last updated: {last_et} ({last_utc})</footer>
</div></body></html>"""

# =========================================================
# 4) Calculator JS (safe)
# =========================================================
SCRIPTS = """<script>
function calcInvestment(){
  let p=parseFloat(document.getElementById('p').value)||0;
  let m=parseFloat(document.getElementById('m').value)||0;
  let r_val=parseFloat(document.getElementById('r').value);
  let y_raw=parseInt(document.getElementById('y').value);
  let y=(isFinite(y_raw)?y_raw:0)*12;
  let total=0;
  if(!isFinite(r_val) || r_val===0){
    total=p+(m*y);
  }else{
    let r=r_val/100/12;
    total=p*Math.pow(1+r,y)+m*((Math.pow(1+r,y)-1)/r);
  }
  document.getElementById('res').innerHTML=
    "<div style='margin-top:15px;font-size:1.5em;color:var(--accent)'>Est. Value: $"+
    total.toLocaleString(undefined,{maximumFractionDigits:0})+"</div>";
}
</script>"""

# =========================================================
# 5) Helpers
# =========================================================
def should_update_stocks(now_et: datetime.datetime) -> bool:
    # weekend -> NO stocks
    if now_et.weekday() >= 5:
        return False
    # top of hour only (00)
    return now_et.minute == 0

def safe_float(x, default=0.0):
    try:
        if x is None:
            return default
        return float(x)
    except:
        return default

def fetch_quote(ticker: str):
    """
    Return dict: price, change_pct, div_yield_pct
    Use .info (works most) but protect errors.
    """
    stock = yf.Ticker(ticker)
    info = {}
    try:
        info = stock.info or {}
    except:
        info = {}

    price = safe_float(info.get("currentPrice", info.get("regularMarketPrice", 0)))
    change_pct = safe_float(info.get("regularMarketChangePercent", 0))
    div_y = info.get("dividendYield", 0)
    div_yield_pct = safe_float(div_y, 0) * 100 if div_y else 0.0

    # Fallback: try fast history if price missing
    if price == 0:
        try:
            h = stock.history(period="1d", interval="1m")
            if not h.empty:
                price = float(h["Close"].iloc[-1])
        except:
            pass

    return {"price": price, "change_pct": change_pct, "div_yield_pct": div_yield_pct}

def build_asset_page(ticker: str, q: dict, last_et: str, last_utc: str):
    price = q["price"]
    change = q["change_pct"]
    divy = q["div_yield_pct"]
    color = "var(--success)" if change >= 0 else "var(--danger)"
    body = f"""
    <h1>{ticker} Analysis</h1>
    <div class="analysis">
      <div class="badge">Live snapshot</div>
      <h2 style="color:var(--accent)">${price:.2f}</h2>
      <p>Change: <span style="color:{color}">{'+' if change>=0 else ''}{change:.2f}%</span></p>
      <p>Dividend Yield: <b>{divy:.2f}%</b></p>
      <hr>
      <h3>Investor AI Workflow</h3>
      <p>Use <a href="/ai/perplexity-pro.html">Perplexity Pro</a> for real-time news, then validate risk with
         <a href="/ai/claude-3-5-sonnet.html">Claude 3.5 Sonnet</a>.</p>
    </div>
    """
    (ASSETS_DIR / f"{ticker}.html").write_text(
        wrap_page(f"{ticker}", body, f"{ticker} live snapshot & AI investor guide.", last_et, last_utc),
        encoding="utf-8"
    )

def build_ai_pages(last_et: str, last_utc: str):
    cards = ""
    for t in AI_TOOLS_30:
        cards += f"""
        <div class="card">
          <h3>{t['name']}</h3>
          <div class="small-muted">{t['cat']} · {t.get('price','')}</div>
          <p>{t['str']}</p>
          <a href="/ai/{t['id']}.html">Learn More →</a>
        </div>
        """
    calc = """
    <div class="analysis">
      <h2>AI Cost Estimator</h2>
      <p class="small-muted">Tip: Use low-cost models for bulk screening, high-reasoning models for final decisions.</p>
    </div>
    """
    (OUTPUT_DIR / "ai_tools.html").write_text(
        wrap_page("Investor AI Toolkit", f"<h1>Investor AI Toolkit</h1>{calc}<div class='grid'>{cards}</div>",
                  "30 investor-focused AI tools.", last_et, last_utc),
        encoding="utf-8"
    )

    for t in AI_TOOLS_30:
        body = f"""
        <h1>{t['name']}</h1>
        <div class="analysis">
          <table>
            <tr><th>Category</th><td>{t['cat']}</td></tr>
            <tr><th>Price</th><td>{t.get('price','')}</td></tr>
            <tr><th>Core Strength</th><td>{t['str']}</td></tr>
            <tr><th>Best Use</th><td>{t['use']}</td></tr>
          </table>
          <p class="small-muted">Back to <a href="/ai_tools.html">Investor AI Toolkit</a></p>
        </div>
        """
        (AI_DIR / f"{t['id']}.html").write_text(
            wrap_page(t["name"], body, f"{t['name']} investor usage guide.", last_et, last_utc),
            encoding="utf-8"
        )

def build_blog(last_et: str, last_utc: str):
    (BLOG_DIR / "index.html").write_text(
        wrap_page("Blog", "<h1>Blog</h1><div class='analysis'><p>Coming soon.</p></div>",
                  "Market insights & AI investing notes.", last_et, last_utc),
        encoding="utf-8"
    )

def build_home(update_stocks: bool, last_et: str, last_utc: str):
    status = "Stocks: YES (weekday + top-of-hour)" if update_stocks else "Stocks: NO (crypto-only run)"
    body = f"""
    <header>
      <h1>US Market Terminals</h1>
      <p class="small-muted">Crypto updates every 15 minutes · Stocks update hourly on weekdays · Weekend stock updates are paused.</p>
      <div class="badge">{status}</div>
    </header>

    <div class="grid">
      <div class="card"><h2>📈 Nasdaq Leaders</h2><p>Top growth & tech.</p><a href="/finance.html#nasdaq">Open →</a></div>
      <div class="card"><h2>💵 Dividend & REIT</h2><p>Cashflow-focused picks.</p><a href="/finance.html#dividend">Open →</a></div>
      <div class="card"><h2>🪙 Crypto</h2><p>BTC/ETH live.</p><a href="/finance.html#crypto">Open →</a></div>
      <div class="card"><h2>🤖 Investor AI</h2><p>30 tools.</p><a href="/ai_tools.html">Open →</a></div>
    </div>
    """
    (OUTPUT_DIR / "index.html").write_text(
        wrap_page("Home", body, "AI-powered market terminal: Nasdaq, dividends, crypto.", last_et, last_utc),
        encoding="utf-8"
    )

def build_finance_page(sections: dict, last_et: str, last_utc: str):
    # sections: {"nasdaq":[(ticker,q)], "dividend":[...], "crypto":[...], "etf":[...]}
    def render_cards(items):
        html = ""
        for ticker, q in items:
            price = q["price"]
            change = q["change_pct"]
            divy = q["div_yield_pct"]
            color = "var(--success)" if change >= 0 else "var(--danger)"
            html += f"""
            <div class="card">
              <h3>{ticker}</h3>
              <div style="font-size:1.6em;color:var(--accent)">${price:.2f}</div>
              <div style="color:{color}">{'+' if change>=0 else ''}{change:.2f}%</div>
              <div class="small-muted">Div: {divy:.2f}%</div>
              <a href="/assets/{ticker}.html">Detailed Analysis →</a>
            </div>
            """
        return html

    calc = """
    <div class="analysis">
      <h2>Dividend Compound Calculator</h2>
      <div class="small-muted">Simple compounding estimate (not financial advice).</div>
      <input id="p" class="calc-input" placeholder="Initial ($)" value="10000">
      <input id="m" class="calc-input" placeholder="Monthly ($)" value="500">
      <input id="r" class="calc-input" placeholder="Yield (%)" value="5">
      <input id="y" class="calc-input" placeholder="Years" value="10">
      <button onclick="calcInvestment()" class="calc-btn">Calculate</button>
      <div id="res"></div>
    </div>
    """

    body = f"""
    <h1>Finance Terminal</h1>
    {calc}

    <div id="nasdaq" class="analysis"><h2>📈 Nasdaq Leaders</h2></div>
    <div class="grid">{render_cards(sections.get("nasdaq", []))}</div>

    <div id="dividend" class="analysis"><h2>💵 Dividend & REIT</h2></div>
    <div class="grid">{render_cards(sections.get("dividend", []))}</div>

    <div id="etf" class="analysis"><h2>🧺 ETFs</h2></div>
    <div class="grid">{render_cards(sections.get("etf", []))}</div>

    <div id="crypto" class="analysis"><h2>🪙 Crypto</h2></div>
    <div class="grid">{render_cards(sections.get("crypto", []))}</div>

    {SCRIPTS}
    """
    (OUTPUT_DIR / "finance.html").write_text(
        wrap_page("Finance", body, "Nasdaq, dividend, ETF, crypto terminal.", last_et, last_utc),
        encoding="utf-8"
    )

def write_static_files():
    (OUTPUT_DIR / "CNAME").write_text(CUSTOM_DOMAIN, encoding="utf-8")
    (OUTPUT_DIR / "ads.txt").write_text(ADS_TXT_LINE, encoding="utf-8")
    (OUTPUT_DIR / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {BASE_URL}/sitemap.xml", encoding="utf-8")

def build_sitemap(url_paths, lastmod_utc_iso):
    xml = '<?xml version="1.0" encoding="UTF-8"?>'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    for p in url_paths:
        xml += f"<url><loc>{BASE_URL}{p}</loc><lastmod>{lastmod_utc_iso}</lastmod></url>"
    xml += "</urlset>"
    (OUTPUT_DIR / "sitemap.xml").write_text(xml, encoding="utf-8")

# =========================================================
# 6) Main
# =========================================================
def main():
    tz = pytz.timezone("US/Eastern")
    now_et = datetime.datetime.now(tz)
    last_et = now_et.strftime("%Y-%m-%d %H:%M %Z")

    # timezone-aware UTC (no deprecated utcnow)
    now_utc = datetime.datetime.now(datetime.UTC)
    last_utc = now_utc.strftime("%Y-%m-%d %H:%M UTC")
    lastmod_utc_iso = now_utc.strftime("%Y-%m-%dT%H:%M:%SZ")

    print(f"🚀 Build start: {last_et}")

    update_stocks = should_update_stocks(now_et)
    print("🔁 Crypto update: ALWAYS (15m schedule)")
    print(f"🔁 Stocks update: {'YES' if update_stocks else 'NO'} (weekday + top-of-hour only)")

    # 1) Home + AI pages always regenerate (static)
    build_home(update_stocks, last_et, last_utc)
    build_ai_pages(last_et, last_utc)
    build_blog(last_et, last_utc)
    write_static_files()

    # 2) Quotes build
    created_assets = []
    sections = {"nasdaq": [], "dividend": [], "etf": [], "crypto": []}

    # Always update crypto quotes
    tickers_to_update = list(CRYPTO_TICKERS)

    # Update stocks only on schedule
    if update_stocks:
        tickers_to_update += NASDAQ_TICKERS + DIVIDEND_TICKERS + ETF_TICKERS

    # Deduplicate
    seen = set()
    tickers_to_update = [t for t in tickers_to_update if not (t in seen or seen.add(t))]

    for ticker in tickers_to_update:
        try:
            q = fetch_quote(ticker)
            if q["price"] == 0:
                continue

            # Always (re)generate the asset page for tickers updated this run
            build_asset_page(ticker, q, last_et, last_utc)
            created_assets.append(ticker)

            # Put into sections
            if ticker in NASDAQ_TICKERS:
                sections["nasdaq"].append((ticker, q))
            elif ticker in DIVIDEND_TICKERS:
                sections["dividend"].append((ticker, q))
            elif ticker in ETF_TICKERS:
                sections["etf"].append((ticker, q))
            elif ticker in CRYPTO_TICKERS:
                sections["crypto"].append((ticker, q))

            time.sleep(0.15)
        except Exception as e:
            print(f"⚠️ Skip {ticker}: {e}")

    # 3) Finance page must ALWAYS exist; if stocks not updated, still render with whatever exists:
    #    If stock sections are empty on crypto-only run, we read existing asset pages? (keep simple: show crypto section only)
    #    Better UX: keep sections from existing pages not feasible without parsing; we'll show placeholders.
    if not update_stocks:
        # show placeholders for stock sections, crypto will be populated
        placeholder = {"price": 0.0, "change_pct": 0.0, "div_yield_pct": 0.0}
        # Keep Nasdaq/Dividend/ETF empty, Crypto filled
        pass

    build_finance_page(sections, last_et, last_utc)

    # 4) Sitemap: include core pages + AI pages + ONLY pages we actually touched this run
    url_paths = ["/index.html", "/finance.html", "/ai_tools.html", "/blog/index.html"]
    url_paths += [f"/ai/{t['id']}.html" for t in AI_TOOLS_30]
    url_paths += [f"/assets/{t}.html" for t in created_assets]
    build_sitemap(url_paths, lastmod_utc_iso)

    print(f"✅ Build done: updated_assets={len(created_assets)} pages, total in sitemap={len(url_paths)}")

if __name__ == "__main__":
    main()
