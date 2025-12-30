import yfinance as yf
import pandas as pd
import datetime
import time
import subprocess
from typing import List, Tuple, Dict, Optional
from pathlib import Path

try:
    from zoneinfo import ZoneInfo  # Python 3.9+
except Exception:
    ZoneInfo = None

# =========================================================
# Configuration
# =========================================================
# IMPORTANT: Your GitHub Pages is built from /docs (per your settings).
# So we must write files into ./docs
OUTPUT_DIR = Path("./docs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

MAX_RETRIES = 4
BASE_DELAY = 1.5
CHUNK_SIZE = 25
PERIOD = "5d"
TIMEZONE = "US/Eastern"

SITE_DOMAIN = "https://us-dividend-pro.com"
SITE_NAME = "US Dividend Pro"
CONTACT_EMAIL = "contact@us-dividend-pro.com"

# =========================================================
# Tickers
# =========================================================
NASDAQ_TICKERS = [
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

COIN_TICKERS = [
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

DIVIDEND_TICKERS = [
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
# Known states / fallbacks
# =========================================================
DELISTED = {
    "SPLK": "INACTIVE / DELISTED"
}

# Optional alias list for symbols that sometimes fail in batch mode
CRYPTO_ALIASES: Dict[str, List[str]] = {
    "MATIC-USD": ["MATIC-USD", "POL28321-USD"],
    "RNDR-USD": ["RNDR-USD", "RENDER-USD"],
}

# =========================================================
# Shared HTML pieces
# =========================================================
CACHE_META = (
    '<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">'
    '<meta http-equiv="Pragma" content="no-cache">'
    '<meta http-equiv="Expires" content="0">'
)

NAV_HTML = f"""
<nav style="display:flex;gap:12px;flex-wrap:wrap;margin:0 0 18px 0;">
  <a href="/index.html" style="color:#fff;text-decoration:none;font-weight:700;">Home</a>
  <a href="/coin.html" style="color:#8b949e;text-decoration:none;">Crypto</a>
  <a href="/dividend.html" style="color:#8b949e;text-decoration:none;">Dividend</a>
  <a href="/nasdaq.html" style="color:#8b949e;text-decoration:none;">NASDAQ</a>
  <span style="color:#30363d;">|</span>
  <a href="/about.html" style="color:#8b949e;text-decoration:none;">About</a>
  <a href="/privacy.html" style="color:#8b949e;text-decoration:none;">Privacy</a>
  <a href="/terms.html" style="color:#8b949e;text-decoration:none;">Terms</a>
  <a href="/contact.html" style="color:#8b949e;text-decoration:none;">Contact</a>
</nav>
"""

# =========================================================
# Templates
# =========================================================
COIN_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">{cache_meta}
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Crypto Gold Terminal — Top 100 Market Prices & Notes</title>
<style>
:root {{ --bg:#05070a; --card-bg:#11141b; --border:#1e222d; --text:#d1d4dc; --accent:#fbbf24; }}
body {{ background:var(--bg); color:var(--text); font-family:system-ui,-apple-system,Segoe UI,sans-serif; margin:0; padding:20px; }}
.container {{ max-width:1200px; margin:0 auto; }}
header {{ border-bottom:2px solid var(--accent); padding-bottom:16px; margin-bottom:18px; }}
h1 {{ font-size:34px; color:#fff; margin:0; }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fill, minmax(180px, 1fr)); gap:12px; }}
.card {{ background:var(--card-bg); border:1px solid var(--border); padding:14px; border-radius:8px; }}
.up {{ color:#00ffaa; }}
.down {{ color:#ff3b3b; }}
.symbol {{ font-weight:800; font-size:15px; color:#fff; }}
.price {{ font-size:22px; font-weight:800; color:#fff; margin-top:8px; }}
.pct {{ font-size:13px; font-weight:800; padding:2px 6px; border-radius:6px; background:rgba(255,255,255,0.06); }}
.analysis {{ margin-top:26px; padding:22px; background:#11141b; border-radius:10px; line-height:1.85; border-left:4px solid var(--accent); }}
footer {{ margin-top:44px; padding-top:18px; border-top:1px solid var(--border); color:#8b949e; font-size:0.85rem; }}
small {{ color:#8b949e; }}
</style>
</head>
<body>
<div class="container">
<header>
{nav}
<h1>💎 Crypto Gold Terminal</h1>
<div style="color:#8b949e;">Real-time blockchain market feed • Top 100 assets</div>
<div style="font-size:0.85rem; color:#8b949e; margin-top:6px;">
Last Update (US/Eastern): {update_time} | Data Success: {success_rate}%
</div>
</header>

<div class="grid">{content}</div>

<section class="analysis">
<h2>Crypto Market Overview, Volatility, and Risk Notes</h2>
<p>This page monitors a broad list of digital assets commonly referenced by market participants. The goal is to offer a compact view of recent price changes, with a consistent layout that can be checked quickly across devices. Prices are fetched from public market data sources and may not match every exchange tick-for-tick.</p>
<p><strong>How to read this dashboard:</strong> Each tile shows the latest available close and the percentage change versus the prior available close. On crypto markets, “prior close” can reflect the vendor’s session boundaries and is not always aligned to a specific exchange’s midnight cut-off.</p>
<p><strong>Why changes can look large:</strong> Digital assets can move materially on liquidity shifts, headlines, and broader risk-on/risk-off regimes. Smaller-cap assets may show bigger swings due to thinner order books.</p>
<p><strong>Educational context:</strong> Price movement alone is not a trading plan. Consider market structure, volatility, liquidity, and position sizing before taking any action. If you are learning, focus first on risk controls, not return targets.</p>
<p><strong>Disclaimer:</strong> This content is informational only and does not constitute financial advice. No recommendation is made to buy, sell, or hold any asset.</p>
</section>

<footer>
© 2025 {site_name} • Market Data & Commentary • {domain}
</footer>
</div>
</body>
</html>
"""

DIV_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">{cache_meta}
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Dividend Terminal Pro — Income Assets & Risk Notes</title>
<style>
:root {{ --bg:#05070a; --card-bg:#11141b; --border:#1e222d; --text:#d1d4dc; --accent:#00ffaa; }}
body {{ background:var(--bg); color:var(--text); font-family:system-ui,-apple-system,Segoe UI,sans-serif; margin:0; padding:20px; }}
.container {{ max-width:1200px; margin:0 auto; }}
header {{ border-bottom:2px solid var(--accent); padding-bottom:16px; margin-bottom:18px; }}
h1 {{ font-size:34px; color:#fff; margin:0; }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fill, minmax(180px, 1fr)); gap:12px; }}
.card {{ background:var(--card-bg); border:1px solid var(--border); padding:14px; border-radius:8px; }}
.up {{ color:#00ffaa; }}
.down {{ color:#ff3b3b; }}
.symbol {{ font-weight:800; font-size:15px; color:#fff; }}
.price {{ font-size:22px; font-weight:800; color:#fff; margin-top:8px; }}
.pct {{ font-size:13px; font-weight:800; padding:2px 6px; border-radius:6px; background:rgba(255,255,255,0.06); }}
.analysis {{ margin-top:26px; padding:22px; background:#11141b; border-radius:10px; line-height:1.85; border-left:4px solid var(--accent); }}
footer {{ margin-top:44px; padding-top:18px; border-top:1px solid var(--border); color:#8b949e; font-size:0.85rem; }}
</style>
</head>
<body>
<div class="container">
<header>
{nav}
<h1>💰 Dividend Terminal Pro</h1>
<div style="color:#8b949e;">Income-focused market feed • High-quality dividend assets</div>
<div style="font-size:0.85rem; color:#8b949e; margin-top:6px;">
Last Update (US/Eastern): {update_time} | Data Success: {success_rate}%
</div>
</header>

<div class="grid">{content}</div>

<section class="analysis">
<h2>Dividend Investing Notes: Yield, Quality, and Risk Controls</h2>
<p>Dividend strategies aim to generate cash flow through distributions while still participating in equity market returns. Many investors focus on “headline yield,” but long-term outcomes are usually driven by business quality, payout sustainability, and portfolio construction.</p>
<p><strong>Yield is not the whole story:</strong> A high yield can signal genuine cash-flow strength, but it can also reflect a falling price due to elevated risk. Evaluating payout ratios, free cash flow coverage, and balance-sheet flexibility helps separate durable income from fragile income.</p>
<p><strong>Rate sensitivity:</strong> Some income-oriented assets move with interest rate expectations. When rates rise, the required yield for certain sectors can increase, pressuring prices even if dividends are unchanged. Diversification across sectors and styles can reduce single-factor exposure.</p>
<p><strong>Risk controls:</strong> Avoid concentrating in a single theme. Consider position sizing, drawdown tolerance, and liquidity needs. A stable plan is often more important than chasing the highest current yield.</p>
<p><strong>Disclaimer:</strong> This content is informational only and does not constitute financial advice. No recommendation is made to buy, sell, or hold any security.</p>
</section>

<footer>
© 2025 {site_name} • Market Data & Commentary • {domain}
</footer>
</div>
</body>
</html>
"""

NASDAQ_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">{cache_meta}
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>NASDAQ-100 Live Intelligence — Tech Sector Monitor</title>
<style>
body {{ background:#0b0e14; color:#e2e8f0; font-family:system-ui,-apple-system,Segoe UI,sans-serif; padding:20px; margin:0; }}
.dashboard {{ max-width:1200px; margin:0 auto; background:#161b22; border:1px solid #30363d; padding:26px; border-radius:12px; }}
h1 {{ margin:0; font-size:30px; color:#fff; }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fit, minmax(240px, 1fr)); gap:14px; margin:16px 0 18px 0; }}
.stat-card {{ background:#0d1117; padding:16px; border-radius:10px; border-top:4px solid #00ff88; }}
.stat-title {{ color:#8b949e; font-size:0.85rem; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:6px; }}
.price {{ font-size:1.8rem; font-weight:900; color:#fff; }}
table {{ width:100%; border-collapse:collapse; margin-top:14px; font-size:0.95rem; }}
th {{ background:#21262d; color:#8b949e; padding:12px; text-align:left; border-bottom:2px solid #30363d; text-transform:uppercase; font-size:0.8rem; letter-spacing:0.5px; }}
td {{ padding:10px 12px; border-bottom:1px solid #30363d; }}
tr:hover {{ background:#21262d; }}
.up {{ color:#39d353; font-weight:800; }}
.down {{ color:#ff7b72; font-weight:800; }}
.note {{ color:#8b949e; font-size:0.86rem; margin-top:6px; line-height:1.6; }}
.analysis {{ margin-top:22px; padding:18px; background:#0d1117; border-radius:10px; line-height:1.85; border:1px solid #30363d; }}
footer {{ margin-top:28px; padding-top:16px; border-top:1px solid #30363d; color:#8b949e; font-size:0.85rem; text-align:center; }}
</style>
</head>
<body>
<div class="dashboard">
{nav}
<h1>🚀 NASDAQ-100 Live Intelligence</h1>
<div class="note">Real-time technology market feed • Last Update (US/Eastern): {update_time} • Sentiment: <strong style="color:#fff;">{sentiment}</strong></div>
<div class="note">Informational only. Trend labels are derived from simple 1-day price changes and are not investment advice.</div>

<div class="grid">
  <div class="stat-card">
    <div class="stat-title">QQQ ETF Price</div>
    <div class="price">{qqq_price}</div>
  </div>
  <div class="stat-card" style="border-top-color:#58a6ff;">
    <div class="stat-title">Market Sentiment</div>
    <div class="price" style="font-size:1.4rem;">{sentiment}</div>
  </div>
  <div class="stat-card" style="border-top-color:#e3b341;">
    <div class="stat-title">Volatility (VIX)</div>
    <div class="price">{vix_price}</div>
  </div>
</div>

<table>
  <thead>
    <tr><th>Ticker</th><th>Price ($)</th><th>Change (%)</th><th>1-Day Trend</th></tr>
  </thead>
  <tbody>{content}</tbody>
</table>

<section class="analysis">
<h2>Technology Sector Commentary and Risk Context</h2>
<p>The NASDAQ-100 is a widely followed benchmark for large-cap innovation companies. Monitoring constituents can help readers understand leadership rotations, earnings sensitivity, and macro-driven valuation changes.</p>
<p><strong>How to use trend labels:</strong> The BULLISH/BEARISH/NEUTRAL markers on this page are based solely on 1-day percentage moves and do not predict future performance. They are not a substitute for comprehensive analysis.</p>
<p><strong>VIX and QQQ:</strong> VIX is commonly referenced as a proxy for implied volatility expectations. QQQ reflects broad NASDAQ-100 exposure. Together they provide a quick snapshot of risk appetite.</p>
<p><strong>Disclaimer:</strong> This content is informational only and does not constitute financial advice. No recommendation is made to buy, sell, or hold any security.</p>
</section>

<footer>
© 2025 {site_name} • Market Data & Commentary • {domain}
</footer>
</div>
</body>
</html>
"""

HOME_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">{cache_meta}
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{site_name} — Market Terminals</title>
<style>
body {{ background:#0b0e14; color:#e2e8f0; font-family:system-ui,-apple-system,Segoe UI,sans-serif; margin:0; padding:20px; }}
.wrap {{ max-width:1100px; margin:0 auto; }}
.card {{ background:#161b22; border:1px solid #30363d; border-radius:14px; padding:22px; }}
h1 {{ margin:0; color:#fff; font-size:34px; }}
p {{ color:#8b949e; line-height:1.8; }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fit, minmax(240px, 1fr)); gap:14px; margin-top:18px; }}
a.btn {{ display:block; background:#0d1117; border:1px solid #30363d; border-radius:12px; padding:16px; text-decoration:none; color:#fff; }}
a.btn:hover {{ border-color:#58a6ff; }}
small {{ color:#8b949e; }}
footer {{ margin-top:22px; color:#8b949e; font-size:0.85rem; }}
</style>
</head>
<body>
<div class="wrap">
<div class="card">
{nav}
<h1>{site_name}</h1>
<p>
Welcome to a lightweight set of market terminals. Pages are designed for fast loading and consistent layout, with brief educational context.
Data is informational only and does not constitute financial advice. No recommendation is made to buy, sell, or hold any asset or security.
</p>

<div class="grid">
  <a class="btn" href="/dividend.html"><strong>💰 Dividend Terminal</strong><br><small>Income assets and risk notes</small></a>
  <a class="btn" href="/coin.html"><strong>💎 Crypto Terminal</strong><br><small>Top 100 assets with volatility context</small></a>
  <a class="btn" href="/nasdaq.html"><strong>🚀 NASDAQ-100 Terminal</strong><br><small>Constituents + simple 1-day trend labels</small></a>
</div>

<footer>
Last Update (US/Eastern): {update_time}<br>
© 2025 {site_name} • {domain}
</footer>
</div>
</div>
</body>
</html>
"""

STATIC_PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">{cache_meta}
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} — {site_name}</title>
<style>
body {{ background:#0b0e14; color:#e2e8f0; font-family:system-ui,-apple-system,Segoe UI,sans-serif; margin:0; padding:20px; }}
.wrap {{ max-width:980px; margin:0 auto; }}
.card {{ background:#161b22; border:1px solid #30363d; border-radius:14px; padding:22px; }}
h1 {{ margin:0 0 10px 0; color:#fff; }}
p, li {{ color:#c9d1d9; line-height:1.85; }}
small {{ color:#8b949e; }}
hr {{ border:0; border-top:1px solid #30363d; margin:18px 0; }}
</style>
</head>
<body>
<div class="wrap">
<div class="card">
{nav}
<h1>{title}</h1>
{body}
<hr>
<small>© 2025 {site_name} • {domain}</small>
</div>
</div>
</body>
</html>
"""

# =========================================================
# Time helpers
# =========================================================
def us_eastern_now_str() -> str:
    if ZoneInfo:
        tz = ZoneInfo(TIMEZONE)
        return datetime.datetime.now(tz).strftime("%Y-%m-%d %H:%M %Z")
    utc_now = datetime.datetime.now(datetime.timezone.utc)
    return utc_now.strftime("%Y-%m-%d %H:%M UTC")

# =========================================================
# yfinance normalization
# Some downloads return MultiIndex as (Field, Ticker) instead of (Ticker, Field).
# =========================================================
PRICE_FIELDS = {"Open", "High", "Low", "Close", "Adj Close", "Volume"}

def normalize_yf_columns(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return df
    if isinstance(df.columns, pd.MultiIndex) and df.columns.nlevels == 2:
        lvl0 = set(df.columns.get_level_values(0))
        lvl1 = set(df.columns.get_level_values(1))
        if len(lvl0 & PRICE_FIELDS) >= 3 and len(lvl1 & PRICE_FIELDS) == 0:
            df = df.copy()
            df.columns = df.columns.swaplevel(0, 1)
            df = df.sort_index(axis=1)
    return df

def fetch_single(symbol: str, period: str = PERIOD) -> pd.DataFrame:
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            df = yf.download(symbol, period=period, progress=False, auto_adjust=True, threads=False)
            df = normalize_yf_columns(df)
            if df is not None and not df.empty:
                return df
        except Exception:
            pass
        if attempt < MAX_RETRIES:
            time.sleep(BASE_DELAY * attempt)
    return pd.DataFrame()

def fetch_batch_data(tickers: List[str], period: str = PERIOD, chunk_size: int = CHUNK_SIZE) -> pd.DataFrame:
    frames = []
    for i in range(0, len(tickers), chunk_size):
        chunk = tickers[i:i + chunk_size]
        df = None
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                df = yf.download(chunk, period=period, group_by="ticker", threads=True, progress=False, auto_adjust=True)
                df = normalize_yf_columns(df)
                if df is not None and not df.empty:
                    break
            except Exception:
                df = None
            if attempt < MAX_RETRIES:
                time.sleep(BASE_DELAY * attempt)
        if df is not None and not df.empty:
            frames.append(df)

    if not frames:
        return pd.DataFrame()

    merged = pd.concat(frames, axis=1)
    return normalize_yf_columns(merged)

def extract_symbol_df(batch_data: pd.DataFrame, symbol: str) -> pd.DataFrame:
    if batch_data is None or batch_data.empty:
        raise ValueError("Empty batch")
    if isinstance(batch_data.columns, pd.MultiIndex):
        if symbol in batch_data.columns.levels[0]:
            return batch_data[symbol]
        if symbol.upper() in batch_data.columns.levels[0]:
            return batch_data[symbol.upper()]
    if "Close" in batch_data.columns:
        return batch_data
    raise ValueError("Not found")

# =========================================================
# Formatting / sanity
# =========================================================
def format_crypto_price(price: float) -> str:
    if price < 0.01:
        return f"${price:,.8f}"
    if price < 1.0:
        return f"${price:,.6f}"
    return f"${price:,.2f}"

def is_plausible_crypto(symbol: str, price: float) -> bool:
    # Keep sanity checks minimal to avoid false N/A.
    if price is None or price <= 0:
        return False
    s = symbol.replace("-USD", "")
    if s == "BTC" and price < 1000:
        return False
    if s == "ETH" and price < 10:
        return False
    return True

def get_crypto_frame_with_alias(symbol: str, period: str = PERIOD) -> Optional[pd.DataFrame]:
    candidates = CRYPTO_ALIASES.get(symbol, [symbol])
    for cand in candidates:
        df = fetch_single(cand, period=period)
        if df is not None and not df.empty and "Close" in df.columns and df["Close"].dropna().shape[0] >= 2:
            return df
    return None

# =========================================================
# HTML generation
# =========================================================
def generate_cards(
    tickers: List[str],
    batch_data: pd.DataFrame,
    is_crypto: bool = False
) -> Tuple[str, Dict]:
    html = ""
    success = 0

    for symbol in tickers:
        if symbol in DELISTED:
            html += (
                f'<div class="card" style="opacity:0.55;">'
                f'<span class="symbol">{symbol}</span>'
                f'<div class="price">{DELISTED[symbol]}</div>'
                f"</div>"
            )
            continue

        try:
            df = extract_symbol_df(batch_data, symbol).dropna(subset=["Close"])
            if len(df) < 2:
                raise ValueError("Short")
            price = float(df["Close"].iloc[-1])
            prev = float(df["Close"].iloc[-2])

            if is_crypto and not is_plausible_crypto(symbol, price):
                raise ValueError("Implausible crypto price")

            change = ((price - prev) / prev) * 100.0
            cls = "up" if change >= 0 else "down"
            sign = "+" if change >= 0 else ""

            p_str = format_crypto_price(price) if is_crypto else f"${price:,.2f}"
            shown = symbol.replace("-USD", "")
            html += (
                f'<div class="card">'
                f'<div class="card-header" style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">'
                f'<span class="symbol">{shown}</span>'
                f'<span class="pct {cls}">{sign}{change:.2f}%</span>'
                f"</div>"
                f'<div class="price">{p_str}</div>'
                f"</div>"
            )
            success += 1
        except Exception:
            df2 = get_crypto_frame_with_alias(symbol) if is_crypto else fetch_single(symbol)
            try:
                if df2 is None or df2.empty:
                    raise ValueError("No single data")
                df2 = df2.dropna(subset=["Close"])
                if len(df2) < 2:
                    raise ValueError("Short single")

                price = float(df2["Close"].iloc[-1])
                prev = float(df2["Close"].iloc[-2])

                if is_crypto and not is_plausible_crypto(symbol, price):
                    raise ValueError("Implausible crypto price (single)")

                change = ((price - prev) / prev) * 100.0
                cls = "up" if change >= 0 else "down"
                sign = "+" if change >= 0 else ""

                p_str = format_crypto_price(price) if is_crypto else f"${price:,.2f}"
                shown = symbol.replace("-USD", "")
                html += (
                    f'<div class="card">'
                    f'<div class="card-header" style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">'
                    f'<span class="symbol">{shown}</span>'
                    f'<span class="pct {cls}">{sign}{change:.2f}%</span>'
                    f"</div>"
                    f'<div class="price">{p_str}</div>'
                    f"</div>"
                )
                success += 1
            except Exception:
                html += (
                    f'<div class="card" style="opacity:0.4;">'
                    f'<span class="symbol">{symbol.replace("-USD","")}</span>'
                    f'<div class="price">N/A</div>'
                    f"</div>"
                )

    rate = (success / len(tickers) * 100.0) if tickers else 0.0
    return html, {"rate": rate}

def generate_table(tickers: List[str], batch_data: pd.DataFrame) -> Tuple[str, Dict]:
    html = ""
    success = 0
    ups = 0

    for symbol in tickers:
        if symbol in DELISTED:
            html += f"<tr><td>{symbol}</td><td>-</td><td>-</td><td>{DELISTED[symbol]}</td></tr>"
            continue

        def row_from_df(df: pd.DataFrame) -> Optional[str]:
            nonlocal success, ups
            df = df.dropna(subset=["Close"])
            if len(df) < 2:
                return None

            price = float(df["Close"].iloc[-1])
            prev = float(df["Close"].iloc[-2])
            change = ((price - prev) / prev) * 100.0

            cls = "up" if change >= 0 else "down"
            sign = "+" if change >= 0 else ""
            if change >= 0:
                ups += 1

            # Trend label (NOT an action)
            if change > 0.5:
                marker = "BULLISH"
                marker_color = "#39d353"
            elif change < -0.5:
                marker = "BEARISH"
                marker_color = "#ff7b72"
            else:
                marker = "NEUTRAL"
                marker_color = "#888"

            success += 1
            return (
                f"<tr>"
                f"<td style='color:#fff;'>{symbol}</td>"
                f"<td>${price:,.2f}</td>"
                f"<td class='{cls}'>{sign}{change:.2f}%</td>"
                f"<td style='color:{marker_color};font-weight:800;'>{marker}</td>"
                f"</tr>"
            )

        try:
            df = extract_symbol_df(batch_data, symbol)
            r = row_from_df(df)
            if r:
                html += r
            else:
                raise ValueError("Short")
        except Exception:
            df2 = fetch_single(symbol)
            r2 = row_from_df(df2) if df2 is not None and not df2.empty else None
            html += r2 if r2 else f"<tr><td>{symbol}</td><td>-</td><td>-</td><td>N/A</td></tr>"

    rate = (success / len(tickers) * 100.0) if tickers else 0.0
    sentiment = "BULLISH" if (ups / max(1, success)) > 0.6 else ("BEARISH" if (ups / max(1, success)) < 0.4 else "NEUTRAL")
    return html, {"rate": rate, "sentiment": sentiment}

# =========================================================
# Static pages + SEO files
# =========================================================
def write_static_pages(now_str: str) -> None:
    about_body = f"""
<p><strong>{SITE_NAME}</strong> provides lightweight market terminals for educational use. The site is built to be fast, consistent, and readable on mobile devices. We focus on clear presentation and short educational notes rather than personalized recommendations.</p>
<p>Data on this website is sourced from public market data providers. While we aim to keep pages reliable, information may be delayed, incomplete, or temporarily unavailable. Always verify prices and corporate actions using official sources before making decisions.</p>
<p><strong>Important:</strong> We do not provide investment, tax, or legal advice. Nothing on this website should be interpreted as a recommendation to buy, sell, or hold any asset or security.</p>
<p><small>Last updated: {now_str} (US/Eastern)</small></p>
"""

    privacy_body = f"""
<p>This Privacy Policy explains how {SITE_NAME} handles information.</p>
<ul>
  <li><strong>No account required:</strong> We do not require user accounts to access our pages.</li>
  <li><strong>Server logs:</strong> Like most websites, basic server logs (e.g., IP address, user agent, timestamps) may be recorded by hosting providers for security and performance.</li>
  <li><strong>Cookies:</strong> We do not intentionally set first-party tracking cookies. Third-party services (e.g., analytics or advertising) may set cookies if enabled in the future.</li>
  <li><strong>External links:</strong> We may link to third-party sites. Their policies apply on those sites.</li>
</ul>
<p>If you have questions about privacy, contact us at <a href="mailto:{CONTACT_EMAIL}" style="color:#58a6ff;">{CONTACT_EMAIL}</a>.</p>
"""

    terms_body = f"""
<p>By accessing {SITE_NAME}, you agree to the following terms:</p>
<ul>
  <li><strong>Informational use only:</strong> Content is provided for educational purposes and is not financial advice.</li>
  <li><strong>No warranty:</strong> We provide content “as is” without warranties of any kind. Data may be delayed or inaccurate.</li>
  <li><strong>Limitation of liability:</strong> {SITE_NAME} is not liable for losses or damages arising from the use of the website.</li>
  <li><strong>Third-party data:</strong> Market data may come from third parties. Availability and accuracy can vary.</li>
</ul>
<p>If you do not agree, please discontinue use of the site.</p>
"""

    contact_body = f"""
<p>For inquiries, please contact:</p>
<ul>
  <li>Email: <a href="mailto:{CONTACT_EMAIL}" style="color:#58a6ff;">{CONTACT_EMAIL}</a></li>
  <li>Website: <a href="{SITE_DOMAIN}" style="color:#58a6ff;">{SITE_DOMAIN}</a></li>
</ul>
<p><small>We do not provide personalized investment advice via email.</small></p>
"""

    pages = [
        ("about.html", "About", about_body),
        ("privacy.html", "Privacy Policy", privacy_body),
        ("terms.html", "Terms of Service", terms_body),
        ("contact.html", "Contact", contact_body),
    ]

    for filename, title, body in pages:
        (OUTPUT_DIR / filename).write_text(
            STATIC_PAGE_TEMPLATE.format(
                cache_meta=CACHE_META,
                title=title,
                site_name=SITE_NAME,
                domain=SITE_DOMAIN,
                nav=NAV_HTML,
                body=body,
            ),
            encoding="utf-8",
        )

def write_robots_and_sitemap() -> None:
    # robots.txt
    (OUTPUT_DIR / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\nSitemap: {SITE_DOMAIN}/sitemap.xml\n",
        encoding="utf-8",
    )

    # sitemap.xml (basic)
    urls = [
        f"{SITE_DOMAIN}/index.html",
        f"{SITE_DOMAIN}/dividend.html",
        f"{SITE_DOMAIN}/coin.html",
        f"{SITE_DOMAIN}/nasdaq.html",
        f"{SITE_DOMAIN}/about.html",
        f"{SITE_DOMAIN}/privacy.html",
        f"{SITE_DOMAIN}/terms.html",
        f"{SITE_DOMAIN}/contact.html",
    ]

    now_iso = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    sitemap = ['<?xml version="1.0" encoding="UTF-8"?>',
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        sitemap.append("  <url>")
        sitemap.append(f"    <loc>{u}</loc>")
        sitemap.append(f"    <lastmod>{now_iso}</lastmod>")
        sitemap.append("    <changefreq>hourly</changefreq>")
        sitemap.append("    <priority>0.8</priority>")
        sitemap.append("  </url>")
    sitemap.append("</urlset>\n")

    (OUTPUT_DIR / "sitemap.xml").write_text("\n".join(sitemap), encoding="utf-8")

# =========================================================
# Main
# =========================================================
def main():
    now_str = us_eastern_now_str()

    # Static/SEO pages first
    write_static_pages(now_str)
    write_robots_and_sitemap()

    # Home page
    (OUTPUT_DIR / "index.html").write_text(
        HOME_TEMPLATE.format(
            cache_meta=CACHE_META,
            nav=NAV_HTML,
            site_name=SITE_NAME,
            domain=SITE_DOMAIN,
            update_time=now_str,
        ),
        encoding="utf-8",
    )

    # 1) Crypto
    c_batch = fetch_batch_data(COIN_TICKERS, period=PERIOD, chunk_size=CHUNK_SIZE)
    c_html, c_stats = generate_cards(COIN_TICKERS, c_batch, is_crypto=True)
    (OUTPUT_DIR / "coin.html").write_text(
        COIN_TEMPLATE.format(
            cache_meta=CACHE_META,
            nav=NAV_HTML,
            update_time=now_str,
            success_rate=f"{c_stats['rate']:.1f}",
            content=c_html,
            site_name=SITE_NAME,
            domain=SITE_DOMAIN,
        ),
        encoding="utf-8",
    )

    # 2) Dividend
    d_batch = fetch_batch_data(DIVIDEND_TICKERS, period=PERIOD, chunk_size=CHUNK_SIZE)
    d_html, d_stats = generate_cards(DIVIDEND_TICKERS, d_batch, is_crypto=False)
    (OUTPUT_DIR / "dividend.html").write_text(
        DIV_TEMPLATE.format(
            cache_meta=CACHE_META,
            nav=NAV_HTML,
            update_time=now_str,
            success_rate=f"{d_stats['rate']:.1f}",
            content=d_html,
            site_name=SITE_NAME,
            domain=SITE_DOMAIN,
        ),
        encoding="utf-8",
    )

    # 3) NASDAQ (write as nasdaq.html to avoid clobbering home index.html)
    n_batch = fetch_batch_data(NASDAQ_TICKERS + ["QQQ", "^VIX"], period=PERIOD, chunk_size=CHUNK_SIZE)
    n_html, n_stats = generate_table(NASDAQ_TICKERS, n_batch)

    try:
        qqq_df = extract_symbol_df(n_batch, "QQQ").dropna(subset=["Close"])
        vix_df = extract_symbol_df(n_batch, "^VIX").dropna(subset=["Close"])
        qqq = f"${float(qqq_df['Close'].iloc[-1]):,.2f}" if len(qqq_df) else "N/A"
        vix = f"{float(vix_df['Close'].iloc[-1]):,.2f}" if len(vix_df) else "N/A"
    except Exception:
        qqq, vix = "N/A", "N/A"

    (OUTPUT_DIR / "nasdaq.html").write_text(
        NASDAQ_TEMPLATE.format(
            cache_meta=CACHE_META,
            nav=NAV_HTML,
            update_time=now_str,
            content=n_html,
            qqq_price=qqq,
            vix_price=vix,
            sentiment=n_stats["sentiment"],
            site_name=SITE_NAME,
            domain=SITE_DOMAIN,
        ),
        encoding="utf-8",
    )

    # Git Push (optional)
    try:
        subprocess.run(["git", "config", "user.name", "github-actions"], check=True)
        subprocess.run(["git", "config", "user.email", "github-actions@github.com"], check=True)
        subprocess.run(["git", "add", "."], check=True)
        if subprocess.run(["git", "diff", "--cached", "--quiet"]).returncode != 0:
            subprocess.run(["git", "commit", "-m", f"🚀 Update (US/Eastern): {now_str}"], check=True)
            subprocess.run(["git", "push"], check=True)
    except Exception:
        pass

if __name__ == "__main__":
    main()
