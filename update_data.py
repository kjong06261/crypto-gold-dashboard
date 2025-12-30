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
OUTPUT_DIR = Path("./docs")  # GitHub Pages Source = /docs
MAX_RETRIES = 4
BASE_DELAY = 1.5
CHUNK_SIZE = 25
PERIOD = "5d"
TIMEZONE = "US/Eastern"

# Your custom domain (used for sitemap + CNAME)
CUSTOM_DOMAIN = "us-dividend-pro.com"
BASE_URL = f"https://{CUSTOM_DOMAIN}".rstrip("/")

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
    "SPLK": "DELISTED (Acquired by Cisco, Mar 2024)"
}

# Optional alias list for symbols that sometimes fail in batch mode
CRYPTO_ALIASES: Dict[str, List[str]] = {
    "MATIC-USD": ["MATIC-USD", "POL28321-USD"],
    "RNDR-USD": ["RNDR-USD", "RENDER-USD"],
}

# =========================================================
# HTML Base / UI
# =========================================================
CACHE_META = (
    '<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">'
    '<meta http-equiv="Pragma" content="no-cache">'
    '<meta http-equiv="Expires" content="0">'
)

BASE_CSS = """
:root{
  --bg:#05070a; --panel:#11141b; --border:#1e222d; --text:#d1d4dc;
  --muted:#8b949e; --link:#58a6ff;
  --accent-coin:#fbbf24; --accent-div:#00ffaa; --accent-idx:#00ff88;
}
*{box-sizing:border-box}
body{margin:0;padding:20px;background:var(--bg);color:var(--text);font-family:system-ui,-apple-system,Segoe UI,Roboto,Arial}
.container{max-width:1200px;margin:0 auto}
a{color:var(--link);text-decoration:none}
a:hover{text-decoration:underline}
.nav{
  display:flex;flex-wrap:wrap;gap:10px;align-items:center;
  padding:12px 14px;border:1px solid var(--border);border-radius:10px;
  background:#0b0e14;margin-bottom:18px
}
.nav .brand{font-weight:800;color:#fff;margin-right:8px}
.nav a{padding:6px 10px;border-radius:8px;background:rgba(255,255,255,0.03)}
.nav a:hover{background:rgba(255,255,255,0.06);text-decoration:none}
header{padding-bottom:18px;margin-bottom:18px;border-bottom:1px solid var(--border)}
h1{margin:0;color:#fff;letter-spacing:-0.5px}
.sub{margin-top:6px;color:var(--muted)}
.meta{margin-top:6px;color:#666;font-size:.9rem}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:12px}
.card{
  background:var(--panel); border:1px solid var(--border); padding:14px; border-radius:10px;
  min-height:92px;
}
.card .row{display:flex;justify-content:space-between;align-items:center;margin-bottom:8px}
.symbol{font-weight:800;color:#fff}
.price{font-size:22px;font-weight:800;color:#fff}
.pct{font-weight:800;font-size:13px;padding:2px 7px;border-radius:8px;background:rgba(255,255,255,0.05)}
.up{color:#00ffaa}
.down{color:#ff3b3b}
.analysis{
  margin-top:26px; padding:22px; background:var(--panel); border:1px solid var(--border);
  border-radius:12px; line-height:1.75
}
.analysis h2{margin-top:0;color:#fff}
footer{
  margin-top:30px; padding-top:18px; border-top:1px solid var(--border);
  color:var(--muted); font-size:.85rem
}
table{width:100%;border-collapse:collapse;margin-top:10px;font-size:.95rem}
th{background:#21262d;color:var(--muted);padding:12px;text-align:left;border-bottom:1px solid #30363d}
td{padding:10px;border-bottom:1px solid #30363d}
tr:hover{background:#21262d}
.badge{font-weight:800}
"""

NAV_HTML = """
<div class="nav">
  <div class="brand">US Market Terminals</div>
  <a href="/coin.html">Crypto</a>
  <a href="/dividend.html">Dividend</a>
  <a href="/index.html">NASDAQ</a>
  <a href="/blog/index.html">Blog</a>
  <a href="/about.html">About</a>
  <a href="/privacy.html">Privacy</a>
  <a href="/terms.html">Terms</a>
  <a href="/contact.html">Contact</a>
  <a href="/disclaimer.html">Disclaimer</a>
</div>
""".strip()

def wrap_page(title: str, body_html: str, extra_head: str = "") -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
{CACHE_META}
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{title} - educational market context, pricing snapshots, and risk notes. Informational only.">
<style>{BASE_CSS}</style>
{extra_head}
</head>
<body>
<div class="container">
{NAV_HTML}
{body_html}
<footer>
  <div><strong>Informational only.</strong> No recommendation is made to buy, sell, or hold any security or digital asset.</div>
  <div>© 2025 US Market Terminals</div>
</footer>
</div>
</body>
</html>"""

# =========================================================
# Time helpers
# =========================================================
def us_eastern_now_str() -> str:
    if ZoneInfo:
        tz = ZoneInfo(TIMEZONE)
        return datetime.datetime.now(tz).strftime("%Y-%m-%d %H:%M %Z")
    utc_now = datetime.datetime.now(datetime.timezone.utc)
    return utc_now.strftime("%Y-%m-%d %H:%M UTC")

def iso_utc_now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

# =========================================================
# yfinance normalization
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
    merged = normalize_yf_columns(merged)
    return merged

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
# Formatting / validation
# =========================================================
def format_crypto_price(price: float) -> str:
    if price < 0.01:
        return f"${price:,.8f}"
    if price < 1.0:
        return f"${price:,.6f}"
    return f"${price:,.2f}"

def is_plausible_crypto(symbol: str, price: float) -> bool:
    if price <= 0:
        return False
    s = symbol.replace("-USD", "")
    if s == "BTC" and price < 1000:
        return False
    if s == "ETH" and price < 10:
        return False
    if s in {"ARB", "OP", "UNI", "MATIC", "SUI"} and price < 0.01:
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
def generate_cards(tickers: List[str], batch_data: pd.DataFrame, is_crypto: bool = False) -> Tuple[str, Dict]:
    html = ""
    success = 0

    for symbol in tickers:
        if symbol in DELISTED:
            html += (
                f'<div class="card" style="opacity:0.55;">'
                f'<div class="row"><span class="symbol">{symbol}</span><span class="pct">N/A</span></div>'
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
                f'<div class="row"><span class="symbol">{shown}</span><span class="pct {cls}">{sign}{change:.2f}%</span></div>'
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
                    f'<div class="row"><span class="symbol">{shown}</span><span class="pct {cls}">{sign}{change:.2f}%</span></div>'
                    f'<div class="price">{p_str}</div>'
                    f"</div>"
                )
                success += 1
            except Exception:
                html += (
                    f'<div class="card" style="opacity:0.4;">'
                    f'<div class="row"><span class="symbol">{symbol.replace("-USD","")}</span><span class="pct">N/A</span></div>'
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

        try:
            df = extract_symbol_df(batch_data, symbol).dropna(subset=["Close"])
            if len(df) < 2:
                raise ValueError("Short")

            price = float(df["Close"].iloc[-1])
            prev = float(df["Close"].iloc[-2])
            change = ((price - prev) / prev) * 100.0

            cls = "up" if change >= 0 else "down"
            sign = "+" if change >= 0 else ""
            if change >= 0:
                ups += 1

            # Trend label (not an action)
            if change > 0.5:
                marker = "BULLISH"
                marker_color = "#39d353"
            elif change < -0.5:
                marker = "BEARISH"
                marker_color = "#ff7b72"
            else:
                marker = "NEUTRAL"
                marker_color = "#888"

            html += (
                f"<tr>"
                f"<td style='color:#fff; font-weight:800;'>{symbol}</td>"
                f"<td>${price:,.2f}</td>"
                f"<td class='{cls}'>{sign}{change:.2f}%</td>"
                f"<td style='color:{marker_color}; font-weight:800;'>{marker}</td>"
                f"</tr>"
            )
            success += 1
        except Exception:
            df2 = fetch_single(symbol)
            try:
                if df2 is None or df2.empty:
                    raise ValueError("No single data")

                df2 = df2.dropna(subset=["Close"])
                if len(df2) < 2:
                    raise ValueError("Short single")

                price = float(df2["Close"].iloc[-1])
                prev = float(df2["Close"].iloc[-2])
                change = ((price - prev) / prev) * 100.0

                cls = "up" if change >= 0 else "down"
                sign = "+" if change >= 0 else ""
                if change >= 0:
                    ups += 1

                if change > 0.5:
                    marker = "BULLISH"
                    marker_color = "#39d353"
                elif change < -0.5:
                    marker = "BEARISH"
                    marker_color = "#ff7b72"
                else:
                    marker = "NEUTRAL"
                    marker_color = "#888"

                html += (
                    f"<tr>"
                    f"<td style='color:#fff; font-weight:800;'>{symbol}</td>"
                    f"<td>${price:,.2f}</td>"
                    f"<td class='{cls}'>{sign}{change:.2f}%</td>"
                    f"<td style='color:{marker_color}; font-weight:800;'>{marker}</td>"
                    f"</tr>"
                )
                success += 1
            except Exception:
                html += f"<tr><td>{symbol}</td><td>-</td><td>-</td><td>N/A</td></tr>"

    rate = (success / len(tickers) * 100.0) if tickers else 0.0
    sentiment = "BULLISH" if (ups / max(1, success)) > 0.6 else ("BEARISH" if (ups / max(1, success)) < 0.4 else "NEUTRAL")
    return html, {"rate": rate, "sentiment": sentiment}

# =========================================================
# Static pages (Trust + Adsense readiness)
# =========================================================
def write_static_pages(now_str: str):
    # Home (keep separate name if you already use index.html for NASDAQ)
    home_body = f"""
<header>
  <h1>US Market Terminals</h1>
  <div class="sub">Pricing snapshots + education-first market context. Built for readability and risk awareness.</div>
  <div class="meta">Last refresh stamp (US/Eastern): {now_str}</div>
</header>

<div class="grid">
  <div class="card">
    <div class="row"><span class="symbol">Crypto</span><span class="pct up">LIVE</span></div>
    <div class="price"><a href="/coin.html">Open Crypto Terminal →</a></div>
  </div>
  <div class="card">
    <div class="row"><span class="symbol">Dividend</span><span class="pct up">LIVE</span></div>
    <div class="price"><a href="/dividend.html">Open Dividend Terminal →</a></div>
  </div>
  <div class="card">
    <div class="row"><span class="symbol">NASDAQ-100</span><span class="pct up">LIVE</span></div>
    <div class="price"><a href="/index.html">Open NASDAQ Terminal →</a></div>
  </div>
  <div class="card">
    <div class="row"><span class="symbol">Education</span><span class="pct">BLOG</span></div>
    <div class="price"><a href="/blog/index.html">Read Guides →</a></div>
  </div>
</div>

<section class="analysis">
  <h2>What this site is (and what it is not)</h2>
  <p><strong>Educational purpose:</strong> We publish market snapshots and beginner-friendly explanations of common investing concepts—volatility, yield, risk controls, portfolio concentration, and how to interpret basic price moves.</p>
  <p><strong>No recommendations:</strong> We do not provide personalized financial advice and we do not recommend buying or selling any asset. Trend labels (when present) are descriptive summaries of 1-day price change thresholds.</p>
  <p><strong>Data limitations:</strong> Market data may be delayed or differ by venue. Always verify prices with your broker/exchange before making decisions.</p>
</section>
"""
    (OUTPUT_DIR / "index-home.html").write_text(wrap_page("US Market Terminals - Home", home_body), encoding="utf-8")

    about_body = """
<header>
  <h1>About</h1>
  <div class="sub">A small project focused on clarity, education, and risk-aware market context.</div>
</header>
<section class="analysis">
  <h2>Mission</h2>
  <p>We present simple market terminals for widely followed assets (cryptocurrency benchmarks, dividend-focused equities, and NASDAQ-100 constituents). The goal is to make common metrics easier to read and to pair them with plain-language educational notes.</p>
  <h2>What you will find here</h2>
  <ul>
    <li>Compact pricing snapshots and 1-day percentage changes.</li>
    <li>Basic context: volatility, yield, cash-flow sustainability, concentration risk, and interest-rate sensitivity.</li>
    <li>Education articles that explain concepts without making trade recommendations.</li>
  </ul>
  <h2>What you will not find here</h2>
  <ul>
    <li>No individualized investment advice.</li>
    <li>No instructions to buy or sell specific securities.</li>
    <li>No guarantee of accuracy, timeliness, or completeness of third-party data.</li>
  </ul>
</section>
"""
    (OUTPUT_DIR / "about.html").write_text(wrap_page("About - US Market Terminals", about_body), encoding="utf-8")

    privacy_body = """
<header><h1>Privacy Policy</h1><div class="sub">Summary of how information may be handled on this website.</div></header>
<section class="analysis">
  <h2>Information we collect</h2>
  <p>This site is a static website. We do not intentionally collect personal information such as your name, address, or payment details.</p>
  <h2>Cookies and analytics</h2>
  <p>Third-party services (such as analytics or advertising networks) may use cookies or similar technologies. If ads are enabled, ad partners may collect information about your device and interactions to provide ads and measure performance.</p>
  <h2>External links</h2>
  <p>Pages may link to external sites. We are not responsible for the privacy practices of external websites.</p>
  <h2>Contact</h2>
  <p>If you have privacy questions, please use the contact page.</p>
</section>
"""
    (OUTPUT_DIR / "privacy.html").write_text(wrap_page("Privacy Policy - US Market Terminals", privacy_body), encoding="utf-8")

    terms_body = """
<header><h1>Terms of Use</h1><div class="sub">Please read these terms before using the website.</div></header>
<section class="analysis">
  <h2>Informational content</h2>
  <p>All content is provided for informational and educational purposes only. Nothing on this site constitutes financial, legal, or professional advice.</p>
  <h2>No warranties</h2>
  <p>Market data may be inaccurate, delayed, or incomplete. We provide the site “as is” without warranties of any kind.</p>
  <h2>Limitation of liability</h2>
  <p>We are not liable for losses or damages arising from use of the site or reliance on any information presented.</p>
  <h2>Changes</h2>
  <p>We may update these terms at any time. Continued use indicates acceptance of the updated terms.</p>
</section>
"""
    (OUTPUT_DIR / "terms.html").write_text(wrap_page("Terms of Use - US Market Terminals", terms_body), encoding="utf-8")

    contact_body = """
<header><h1>Contact</h1><div class="sub">For general inquiries or corrections.</div></header>
<section class="analysis">
  <h2>Email</h2>
  <p>Please contact: <strong>support@us-dividend-pro.com</strong></p>
  <h2>Notes</h2>
  <p>We can accept feedback about broken links, obvious data issues, or page accessibility. We cannot respond to requests for personalized investment recommendations.</p>
</section>
"""
    (OUTPUT_DIR / "contact.html").write_text(wrap_page("Contact - US Market Terminals", contact_body), encoding="utf-8")

    disclaimer_body = """
<header><h1>Disclaimer</h1><div class="sub">Important risk and responsibility notice.</div></header>
<section class="analysis">
  <h2>Not financial advice</h2>
  <p>This website provides general information only. Nothing on this site should be interpreted as a recommendation to buy, sell, or hold any security or digital asset.</p>
  <h2>Market risk</h2>
  <p>All investing involves risk, including possible loss of principal. Past performance does not guarantee future results.</p>
  <h2>Data limitations</h2>
  <p>Prices and metrics may be delayed or differ by data provider and venue. Always verify with an official source before making decisions.</p>
  <h2>Trend labels</h2>
  <p>Any “BULLISH/BEARISH/NEUTRAL” labels are simple summaries derived from 1-day percentage changes. They do not predict future performance.</p>
</section>
"""
    (OUTPUT_DIR / "disclaimer.html").write_text(wrap_page("Disclaimer - US Market Terminals", disclaimer_body), encoding="utf-8")

def write_robots_and_sitemap(urls: List[str]):
    robots = f"""User-agent: *
Allow: /

Sitemap: {BASE_URL}/sitemap.xml
"""
    (OUTPUT_DIR / "robots.txt").write_text(robots, encoding="utf-8")

    now = iso_utc_now()
    items = []
    for u in urls:
        items.append(f"<url><loc>{BASE_URL}{u}</loc><lastmod>{now}</lastmod></url>")
    sitemap = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{''.join(items)}
</urlset>
"""
    (OUTPUT_DIR / "sitemap.xml").write_text(sitemap, encoding="utf-8")

def write_cname():
    if CUSTOM_DOMAIN and CUSTOM_DOMAIN.strip():
        (OUTPUT_DIR / "CNAME").write_text(CUSTOM_DOMAIN.strip() + "\n", encoding="utf-8")

# =========================================================
# Blog generator (12 posts)
# =========================================================
BLOG_TOPICS = [
    ("dividend-investing-101", "Dividend Investing 101: Yield, Quality, and Sustainability"),
    ("schd-vs-jepi", "SCHD vs JEPI: Different Income Styles (What to Compare)"),
    ("payout-ratio-explained", "Payout Ratio Explained: Why Yield Alone Can Mislead"),
    ("free-cash-flow-basics", "Free Cash Flow Basics: A Practical Checklist for Income Stocks"),
    ("reits-interest-rates", "REITs and Interest Rates: Why Prices Move When Rates Change"),
    ("portfolio-concentration", "Portfolio Concentration Risk: Diversification That Actually Helps"),
    ("crypto-volatility", "Crypto Volatility 101: Liquidity, Leverage, and 24/7 Markets"),
    ("btc-eth-differences", "Bitcoin vs Ethereum: What They Are (Without Hype)"),
    ("macro-risk-on-off", "Risk-On / Risk-Off: A Simple Way to Read Macro Regimes"),
    ("nasdaq-growth-vs-value", "NASDAQ Growth vs Value: Understanding Rate Sensitivity"),
    ("vix-explained", "VIX Explained: What It Measures and What It Does Not"),
    ("how-to-use-terminals", "How to Use These Terminals: Practical Reading Rules (No Predictions)"),
]

def blog_article_html(slug: str, title: str) -> str:
    # Create topic-specific sections so content is not identical boilerplate
    sections = {
        "dividend-investing-101": [
            ("What dividend investing tries to do", "Dividend investing aims to create repeatable cash flow while still participating in equity returns. The tradeoff is that higher yield can come with higher business risk, leverage, or unstable payouts."),
            ("The three inputs that matter most", "Start with business durability (cash generation), then payout policy (how much is distributed), then valuation (what you pay today). Yield is a result, not a guarantee."),
            ("A basic safety checklist", "Look for stable operating cash flow, moderate payout ratios, manageable debt maturities, and a history of consistent policy. Avoid relying on one quarter’s yield spike.")
        ],
        "schd-vs-jepi": [
            ("Two different ideas of 'income'", "Broad dividend ETFs often emphasize quality screens and long-term dividend growth. Covered-call funds focus on option premium that can smooth distributions but may cap upside in strong rallies."),
            ("Compare the right metrics", "Compare distribution consistency, fees, tax characteristics, and behavior in different regimes (sideways vs trending markets)."),
            ("When comparisons go wrong", "Investors often compare trailing yield only. A better approach is total return over a full cycle and how the product behaves when volatility rises.")
        ],
        "payout-ratio-explained": [
            ("What payout ratio means", "Payout ratio is the share of earnings paid as dividends. A very high payout ratio can be fine for stable businesses but can also signal limited reinvestment or fragile coverage."),
            ("Earnings vs cash flow", "Earnings can be noisy. Free cash flow coverage often gives a clearer view of dividend sustainability."),
            ("Practical thresholds", "There is no universal cutoff. Use sector context and look for consistency rather than a single number.")
        ],
        "free-cash-flow-basics": [
            ("Why free cash flow matters", "Dividends ultimately come from cash. Free cash flow approximates what remains after operating costs and required investment."),
            ("A simple reading rule", "If cash flow is consistently positive and the dividend is covered, the payout has a stronger foundation. If coverage relies on debt issuance, risk rises."),
            ("Watch the cycle", "Cash flow can be cyclical. Look across multiple years rather than one strong quarter.")
        ],
        "reits-interest-rates": [
            ("Why rates affect REIT pricing", "REITs often carry leverage and are valued partly on yield spreads. When rates rise, financing costs and discount rates can pressure valuations."),
            ("What to examine", "Lease duration, tenant quality, refinancing schedule, and property type fundamentals matter more than short-term price moves."),
            ("Common misunderstanding", "Rates are one factor. Property cash flow and balance-sheet management can offset rate headwinds.")
        ],
        "portfolio-concentration": [
            ("Concentration risk in plain terms", "If one sector or one theme dominates your portfolio, one macro shock can harm everything at once."),
            ("Diversification that works", "Diversify across cash-flow drivers: consumer staples, utilities, healthcare, quality tech, and different geographic revenue exposure."),
            ("A simple stress test", "Ask: what happens if rates jump, recession hits, or the dollar strengthens? If everything breaks together, concentration is high.")
        ],
        "crypto-volatility": [
            ("Why crypto moves fast", "Crypto trades 24/7 and is sensitive to liquidity, leverage, and news. Thin order books amplify moves."),
            ("Volatility is not a strategy", "High volatility can create opportunity, but it also increases error costs. Position sizing and risk limits matter."),
            ("Venue differences", "Prices can differ by exchange. Treat snapshots as references, not execution quotes.")
        ],
        "btc-eth-differences": [
            ("Different design goals", "Bitcoin emphasizes scarcity and settlement, while Ethereum supports programmable applications and smart contracts."),
            ("What adoption looks like", "Adoption can be viewed through network security, developer activity, and real-world use cases, not just price charts."),
            ("Risk framing", "Both carry regulatory, technical, and liquidity risks. Understand those before focusing on upside scenarios.")
        ],
        "macro-risk-on-off": [
            ("Risk-on vs risk-off", "Markets rotate between seeking return (risk-on) and seeking safety (risk-off). Liquidity and rates often drive the switch."),
            ("Indicators to watch", "Credit spreads, volatility, and major index breadth can provide context. No single indicator is perfect."),
            ("Avoid false certainty", "Macro regimes shift quickly. Use regime language as context, not as a prediction engine.")
        ],
        "nasdaq-growth-vs-value": [
            ("Why growth is rate-sensitive", "High-growth companies are valued on future cash flows. Higher discount rates can reduce present value of long-dated earnings."),
            ("What to compare", "Compare profitability quality, margin trends, and balance-sheet strength—especially during tightening cycles."),
            ("Use the index carefully", "Indexes can hide dispersion. Some constituents can thrive even when the index is flat.")
        ],
        "vix-explained": [
            ("What VIX measures", "VIX is derived from option prices and reflects implied volatility expectations, not certainty of a crash."),
            ("How it is used", "Traders use VIX as a risk thermometer. Rising VIX suggests higher demand for protection."),
            ("Common misread", "A high VIX does not guarantee lower prices tomorrow; it indicates uncertainty and expensive options.")
        ],
        "how-to-use-terminals": [
            ("What a snapshot is good for", "Use the terminals to notice relative moves, not to forecast. Identify which assets are moving and then research why."),
            ("Reading rules", "Treat 1-day changes as noise unless they align with a larger context. Use multiple timeframes before drawing conclusions."),
            ("Trend labels", "Labels are derived from simple thresholds. They are descriptive summaries, not trade signals.")
        ],
    }

    parts = sections.get(slug, [])
    # Expand into a longer article with additional educational blocks
    extra_blocks = [
        ("Risk controls that scale", "Use a written rule for position sizing, maximum drawdown tolerance, and what would make you reduce exposure. Rules prevent emotion from becoming strategy."),
        ("Information hygiene", "Prefer primary sources for fundamentals: filings, earnings calls, and official disclosures. Use secondary commentary as a supplement, not a replacement."),
        ("A closing reminder", "Education helps you avoid obvious mistakes, but it cannot remove market risk. If something feels too certain, it usually is.")
    ]

    def para_block(h, p):
        return f"<h2>{h}</h2><p>{p}</p>"

    body = f"""
<header>
  <h1>{title}</h1>
  <div class="sub">Education-first market note. Informational only.</div>
</header>
<section class="analysis">
  <p><strong>Purpose:</strong> This article explains core concepts in plain language. It does not provide personalized advice and does not recommend transactions.</p>
  {''.join(para_block(h,p) for (h,p) in parts)}
  {''.join(para_block(h,p) for (h,p) in extra_blocks)}
  <h2>Summary</h2>
  <ul>
    <li>Focus on sustainability and risk controls, not headline numbers.</li>
    <li>Use snapshots as pointers for research, not as predictions.</li>
    <li>Verify critical data with official sources before acting.</li>
  </ul>
</section>
"""
    return wrap_page(title, body)

def write_blog(now_str: str) -> List[str]:
    blog_dir = OUTPUT_DIR / "blog"
    blog_dir.mkdir(parents=True, exist_ok=True)

    urls = []
    cards = []
    for slug, title in BLOG_TOPICS:
        html = blog_article_html(slug, title)
        path = blog_dir / f"{slug}.html"
        path.write_text(html, encoding="utf-8")
        urls.append(f"/blog/{slug}.html")

        cards.append(f"""
        <div class="card">
          <div class="row"><span class="symbol">{title}</span><span class="pct">GUIDE</span></div>
          <div class="price" style="font-size:16px;"><a href="/blog/{slug}.html">Read →</a></div>
        </div>
        """)

    index_body = f"""
<header>
  <h1>Education Blog</h1>
  <div class="sub">Practical guides on yield, volatility, macro context, and reading rules.</div>
  <div class="meta">Updated stamp (US/Eastern): {now_str}</div>
</header>
<div class="grid">
  {''.join(cards)}
</div>
<section class="analysis">
  <h2>How to use these guides</h2>
  <p>Start with the basics (yield, payout ratios, cash flow), then move to context (rates, volatility, macro regimes). The goal is to improve decision quality—not to generate trade calls.</p>
</section>
"""
    (blog_dir / "index.html").write_text(wrap_page("Blog - US Market Terminals", index_body), encoding="utf-8")
    urls.append("/blog/index.html")
    return urls

# =========================================================
# Main
# =========================================================
def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    now_str = us_eastern_now_str()

    # --- Static trust pages + blog ---
    write_cname()
    write_static_pages(now_str)
    blog_urls = write_blog(now_str)

    # 1) Crypto
    c_batch = fetch_batch_data(COIN_TICKERS, period=PERIOD, chunk_size=CHUNK_SIZE)
    c_cards, c_stats = generate_cards(COIN_TICKERS, c_batch, is_crypto=True)

    coin_body = f"""
<header>
  <h1>💎 Crypto Gold Terminal</h1>
  <div class="sub">Real-time blockchain market feed • Top 100 assets</div>
  <div class="meta">Last Update (US/Eastern): {now_str} | Data Success: {c_stats['rate']:.1f}%</div>
</header>
<div class="grid">{c_cards}</div>
<section class="analysis">
  <h2>Crypto Market Overview, Volatility, and Risk Notes</h2>
  <p>This page tracks major digital assets across the global cryptocurrency market, including Bitcoin, Ethereum, and widely traded altcoins.</p>
  <p><strong>How to read:</strong> Each card shows the latest adjusted closing price and the percentage change from the prior session. Large moves may reflect liquidity shifts, macro events, and venue-specific flows.</p>
  <p><strong>Risk note:</strong> Crypto markets are volatile and trade 24/7. Prices may differ across venues. Use this for research and education only.</p>
</section>
"""
    (OUTPUT_DIR / "coin.html").write_text(wrap_page("Crypto Gold Terminal - Top 100", coin_body), encoding="utf-8")

    # 2) Dividend
    d_batch = fetch_batch_data(DIVIDEND_TICKERS, period=PERIOD, chunk_size=CHUNK_SIZE)
    d_cards, d_stats = generate_cards(DIVIDEND_TICKERS, d_batch, is_crypto=False)

    div_body = f"""
<header>
  <h1>💰 Dividend Terminal Pro</h1>
  <div class="sub">Income-focused market feed • High-quality dividend assets</div>
  <div class="meta">Last Update (US/Eastern): {now_str} | Data Success: {d_stats['rate']:.1f}%</div>
</header>
<div class="grid">{d_cards}</div>
<section class="analysis">
  <h2>Dividend Investing Notes: Yield, Quality, and Risk Controls</h2>
  <p>Dividend strategies aim to generate consistent cash flow through distributions while balancing equity risk. This terminal highlights popular income assets such as dividend ETFs and widely held dividend stocks.</p>
  <p><strong>What matters beyond yield:</strong> payout ratios, free cash flow durability, balance-sheet strength, sector concentration, and interest-rate sensitivity are key factors for long-term outcomes.</p>
  <p><strong>Reminder:</strong> Dividends are not guaranteed. Always evaluate sustainability rather than headline yield alone.</p>
</section>
"""
    (OUTPUT_DIR / "dividend.html").write_text(wrap_page("Dividend Terminal Pro - High Yield Assets", div_body), encoding="utf-8")

    # 3) NASDAQ
    n_batch = fetch_batch_data(NASDAQ_TICKERS + ["QQQ", "^VIX"], period=PERIOD, chunk_size=CHUNK_SIZE)
    n_rows, n_stats = generate_table(NASDAQ_TICKERS, n_batch)

    try:
        qqq_df = extract_symbol_df(n_batch, "QQQ").dropna(subset=["Close"])
        vix_df = extract_symbol_df(n_batch, "^VIX").dropna(subset=["Close"])
        qqq = f"${float(qqq_df['Close'].iloc[-1]):,.2f}" if len(qqq_df) else "N/A"
        vix = f"{float(vix_df['Close'].iloc[-1]):,.2f}" if len(vix_df) else "N/A"
    except Exception:
        qqq, vix = "N/A", "N/A"

    idx_body = f"""
<header>
  <h1>🚀 NASDAQ-100 Live Intelligence</h1>
  <div class="sub">Real-time technology market feed • Sentiment: {n_stats['sentiment']}</div>
  <div class="meta">Last Update (US/Eastern): {now_str}</div>
  <div class="meta" style="color:#777;">Informational only. Trend labels are derived from simple 1-day price-change thresholds and are not investment advice.</div>
</header>

<div class="grid">
  <div class="card"><div class="row"><span class="symbol">QQQ ETF</span><span class="pct up">REF</span></div><div class="price">{qqq}</div></div>
  <div class="card"><div class="row"><span class="symbol">Sentiment</span><span class="pct">BREADTH</span></div><div class="price" style="font-size:18px;">{n_stats['sentiment']}</div></div>
  <div class="card"><div class="row"><span class="symbol">VIX</span><span class="pct">RISK</span></div><div class="price">{vix}</div></div>
</div>

<table>
  <thead><tr><th>Ticker</th><th>Price ($)</th><th>Change (%)</th><th>1-Day Trend</th></tr></thead>
  <tbody>{n_rows}</tbody>
</table>

<section class="analysis">
  <h2>Technology Sector Commentary and Risk Context</h2>
  <p>The NASDAQ-100 is a key benchmark for large-cap innovation and growth-oriented companies. Monitoring its constituents can help you understand leadership rotation and broad market risk appetite.</p>
  <p><strong>How to use trend labels:</strong> BULLISH/BEARISH/NEUTRAL markers here are descriptive summaries based on 1-day moves. They do not predict future performance and do not represent a recommendation.</p>
  <p><strong>VIX and QQQ:</strong> VIX is derived from options and reflects implied volatility expectations. QQQ represents NASDAQ-100 exposure. Together they provide a quick risk context.</p>
</section>
"""
    (OUTPUT_DIR / "index.html").write_text(wrap_page("NASDAQ-100 Live Intelligence", idx_body), encoding="utf-8")

    # --- robots + sitemap ---
    urls = [
        "/index.html",
        "/coin.html",
        "/dividend.html",
        "/index-home.html",
        "/about.html",
        "/privacy.html",
        "/terms.html",
        "/contact.html",
        "/disclaimer.html",
    ] + blog_urls
    write_robots_and_sitemap(urls)

    # Git Push (optional; works in GitHub Actions)
    try:
        subprocess.run(["git", "config", "user.name", "github-actions"], check=True)
        subprocess.run(["git", "config", "user.email", "github-actions@github.com"], check=True)
        subprocess.run(["git", "add", "docs"], check=True)
        if subprocess.run(["git", "diff", "--cached", "--quiet"]).returncode != 0:
            subprocess.run(["git", "commit", "-m", f"Update site (US/Eastern): {now_str}"], check=True)
            subprocess.run(["git", "push"], check=True)
    except Exception:
        pass

if __name__ == "__main__":
    main()
