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
# CONFIG (GitHub Pages: /docs 빌드 기준)
# =========================================================
OUTPUT_DIR = Path("./docs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

ASSETS_DIR = OUTPUT_DIR / "assets"
BLOG_DIR = OUTPUT_DIR / "blog"
ASSETS_DIR.mkdir(parents=True, exist_ok=True)
BLOG_DIR.mkdir(parents=True, exist_ok=True)

TIMEZONE = "US/Eastern"
PERIOD = "5d"
CHUNK_SIZE = 25
MAX_RETRIES = 4
BASE_DELAY = 1.5

# ✅ 커스텀 도메인: "도메인만" 넣으세요 (https:// 금지, 경로 금지)
CUSTOM_DOMAIN = "us-dividend-pro.com"
BASE_URL = f"https://{CUSTOM_DOMAIN}"

SITE_NAME = "US Market Terminals"
CONTACT_EMAIL = "support@us-dividend-pro.com"

# =========================================================
# AdSense
# =========================================================
ADSENSE_HEAD = """<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3030006828946894"
     crossorigin="anonymous"></script>"""

# ✅ AdSense에서 준 ads.txt 라인 (필요하면 여기만 바꾸면 됨)
ADS_TXT_LINE = "google.com, pub-3030006828946894, DIRECT, f08c47fec0942fa0"


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

CRYPTO_ALIASES: Dict[str, List[str]] = {
    "MATIC-USD": ["MATIC-USD", "POL28321-USD"],
    "RNDR-USD": ["RNDR-USD", "RENDER-USD"],
}

PRICE_FIELDS = {"Open", "High", "Low", "Close", "Adj Close", "Volume"}


# =========================================================
# UI / Layout
# =========================================================
CACHE_META = (
    '<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">'
    '<meta http-equiv="Pragma" content="no-cache">'
    '<meta http-equiv="Expires" content="0">'
)

BASE_CSS = """
:root{
  --bg:#05070a; --panel:#11141b; --border:#1e222d;
  --text:#d1d4dc; --muted:#8b949e; --link:#58a6ff; --accent:#fbbf24;
}
body{margin:0;padding:18px;background:var(--bg);color:var(--text);font-family:system-ui, -apple-system, Segoe UI, Roboto, sans-serif}
.container{max-width:1200px;margin:0 auto}
.nav{display:flex;flex-wrap:wrap;gap:10px;padding:12px;background:#0b0e14;margin-bottom:16px;border-radius:12px;border:1px solid var(--border)}
.nav a{color:var(--link);text-decoration:none;padding:6px 10px;background:rgba(255,255,255,0.03);border-radius:8px}
header{padding:6px 2px 16px 2px;margin-bottom:14px;border-bottom:1px solid var(--border)}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px, 1fr));gap:12px}
.card{background:var(--panel);border:1px solid var(--border);padding:14px;border-radius:12px}
.symbol{font-weight:800;color:#fff}
.price{font-size:22px;font-weight:800;color:#fff;margin-top:8px}
.pct{font-size:12px;font-weight:800;padding:3px 8px;border-radius:999px;background:rgba(255,255,255,0.05)}
.up{color:#00ffaa}.down{color:#ff3b3b}
.analysis{margin-top:22px;padding:18px;background:var(--panel);border-radius:12px;line-height:1.75;border:1px solid var(--border)}
table{width:100%;border-collapse:collapse;margin-top:10px}
th,td{padding:10px;text-align:left;border-bottom:1px solid #30363d}
th{color:var(--muted);font-weight:700;background:#0b0e14}
footer{margin-top:30px;padding:18px;border-top:1px solid var(--border);color:var(--muted);font-size:12px}
"""

NAV_HTML = f"""
<div class="nav">
  <strong style="color:#fff">{SITE_NAME}</strong>
  <a href="/index.html">Home</a>
  <a href="/coin.html">Crypto</a>
  <a href="/dividend.html">Dividend</a>
  <a href="/nasdaq.html">NASDAQ</a>
  <a href="/assets/index.html">Assets</a>
  <a href="/blog/index.html">Blog</a>
  <a href="/about.html">About</a>
  <a href="/privacy.html">Privacy</a>
  <a href="/terms.html">Terms</a>
  <a href="/contact.html">Contact</a>
</div>
"""

def wrap_page(title: str, body_html: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="UTF-8">{ADSENSE_HEAD}{CACHE_META}
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{title}</title>
<style>{BASE_CSS}</style>
</head>
<body><div class="container">
{NAV_HTML}
{body_html}
<footer>
  <div>© 2025 {SITE_NAME}. Informational only. No investment advice.</div>
</footer>
</div></body></html>"""


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
# yfinance helpers
# =========================================================
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
# Formatting
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
# Terminals
# =========================================================
def generate_cards(tickers: List[str], batch_data: pd.DataFrame, is_crypto: bool = False) -> Tuple[str, float]:
    html = ""
    success = 0

    for symbol in tickers:
        if symbol in DELISTED:
            html += (
                f'<div class="card" style="opacity:0.55;">'
                f'<div class="symbol">{symbol}</div>'
                f'<div class="price">{DELISTED[symbol]}</div>'
                f"</div>"
            )
            continue

        def build_card(price: float, prev: float):
            nonlocal html, success
            change = ((price - prev) / prev) * 100.0
            cls = "up" if change >= 0 else "down"
            sign = "+" if change >= 0 else ""
            p_str = format_crypto_price(price) if is_crypto else f"${price:,.2f}"
            shown = symbol.replace("-USD", "")
            html += (
                f'<div class="card">'
                f'  <div style="display:flex;justify-content:space-between;align-items:center;">'
                f'    <div class="symbol">{shown}</div>'
                f'    <div class="pct {cls}">{sign}{change:.2f}%</div>'
                f'  </div>'
                f'  <div class="price">{p_str}</div>'
                f"</div>"
            )
            success += 1

        try:
            df = extract_symbol_df(batch_data, symbol).dropna(subset=["Close"])
            if len(df) < 2:
                raise ValueError("Short")
            price = float(df["Close"].iloc[-1])
            prev = float(df["Close"].iloc[-2])
            if is_crypto and not is_plausible_crypto(symbol, price):
                raise ValueError("Implausible")
            build_card(price, prev)
        except Exception:
            df2 = get_crypto_frame_with_alias(symbol) if is_crypto else fetch_single(symbol)
            try:
                if df2 is None or df2.empty:
                    raise ValueError("No single")
                df2 = df2.dropna(subset=["Close"])
                if len(df2) < 2:
                    raise ValueError("Short single")
                price = float(df2["Close"].iloc[-1])
                prev = float(df2["Close"].iloc[-2])
                if is_crypto and not is_plausible_crypto(symbol, price):
                    raise ValueError("Implausible single")
                build_card(price, prev)
            except Exception:
                html += (
                    f'<div class="card" style="opacity:0.4;">'
                    f'<div class="symbol">{symbol.replace("-USD","")}</div>'
                    f'<div class="price">N/A</div>'
                    f"</div>"
                )

    rate = (success / len(tickers) * 100.0) if tickers else 0.0
    return html, rate

def generate_nasdaq_table(tickers: List[str], batch_data: pd.DataFrame) -> Tuple[str, float, str]:
    html = ""
    success = 0
    ups = 0

    for symbol in tickers:
        if symbol in DELISTED:
            html += f"<tr><td>{symbol}</td><td>-</td><td>-</td><td>{DELISTED[symbol]}</td></tr>"
            continue

        def build_row(df_: pd.DataFrame):
            nonlocal html, success, ups
            df_ = df_.dropna(subset=["Close"])
            if len(df_) < 2:
                raise ValueError("Short")
            price = float(df_["Close"].iloc[-1])
            prev = float(df_["Close"].iloc[-2])
            change = ((price - prev) / prev) * 100.0
            cls = "up" if change >= 0 else "down"
            sign = "+" if change >= 0 else ""
            if change >= 0:
                ups += 1

            # ✅ “Signal”이 아니라 “Trend label”
            if change > 0.5:
                marker, color = "BULLISH", "#39d353"
            elif change < -0.5:
                marker, color = "BEARISH", "#ff7b72"
            else:
                marker, color = "NEUTRAL", "#888"

            html += (
                f"<tr>"
                f"<td style='color:#fff;font-weight:800'>{symbol}</td>"
                f"<td>${price:,.2f}</td>"
                f"<td class='{cls}'>{sign}{change:.2f}%</td>"
                f"<td style='color:{color};font-weight:800'>{marker}</td>"
                f"</tr>"
            )
            success += 1

        try:
            build_row(extract_symbol_df(batch_data, symbol))
        except Exception:
            try:
                df2 = fetch_single(symbol)
                if df2 is None or df2.empty:
                    raise ValueError("No single")
                build_row(df2)
            except Exception:
                html += f"<tr><td>{symbol}</td><td>-</td><td>-</td><td>N/A</td></tr>"

    rate = (success / len(tickers) * 100.0) if tickers else 0.0
    up_ratio = (ups / max(1, success))
    sentiment = "BULLISH" if up_ratio > 0.6 else ("BEARISH" if up_ratio < 0.4 else "NEUTRAL")
    return html, rate, sentiment


# =========================================================
# Blog (12개)
# =========================================================
BLOG_POSTS = [
    ("dividend-growth-investing", "Dividend Growth Investing: A Practical Framework",
     "Dividend growth strategies focus on companies that consistently raise payouts over time. "
     "Rather than chasing the highest yield, the goal is to combine income with business durability. "
     "Key checks include free cash flow coverage, payout ratios, and balance-sheet resilience. "
     "This approach can reduce the probability of dividend cuts during downturns.\n\n"
     "A simple checklist: (1) stable cash generation, (2) conservative leverage, (3) long operating history, "
     "(4) sector risk awareness, and (5) realistic expectations for total return."),

    ("yield-vs-safety", "Yield vs. Safety: How to Avoid Dividend Traps",
     "High yield can be attractive, but sometimes it reflects elevated risk rather than opportunity. "
     "Dividend traps often show weak cash flow, rising debt, or declining fundamentals. "
     "A safer process is to validate sustainability first and yield second.\n\n"
     "Look for warning signs: payout ratios consistently above cash generation, repeated one-time adjustments, "
     "and sectors that are highly rate-sensitive without strong pricing power."),

    ("reits-rate-sensitivity", "REITs and Interest Rates: What Actually Matters",
     "REIT performance can be sensitive to rate cycles, but the impact is not uniform. "
     "Lease structure, debt maturity ladder, and property type matter more than headlines. "
     "When rates rise, REITs with strong rent escalators and conservative balance sheets can still do well.\n\n"
     "A practical lens: compare same-store NOI trends, occupancy, and refinancing needs over the next 24 months."),

    ("covered-call-etfs", "Covered-Call Income ETFs: When They Help (and When They Hurt)",
     "Covered-call income products can provide smoother distributions, but they trade off upside in strong bull runs. "
     "They may fit investors who prioritize cash flow and lower volatility, but they are not a free lunch.\n\n"
     "Consider: tax profile, implied volatility regime, and whether you accept capped upside in exchange for distributions."),

    ("crypto-risk-management", "Crypto Volatility: A Risk-First Survival Guide",
     "Crypto markets trade 24/7 and can reprice quickly on macro shifts, liquidity events, or exchange-specific news. "
     "A risk-first plan emphasizes position sizing, diversification, and avoiding leverage.\n\n"
     "Practical rules: define maximum drawdown tolerance, avoid concentration in thin-liquidity tokens, "
     "and treat large single-day moves as normal rather than exceptional."),

    ("btc-vs-eth", "Bitcoin vs Ethereum: A Simple Comparison for Beginners",
     "Bitcoin is often treated as a macro-sensitive digital asset with strong brand dominance. "
     "Ethereum is a programmable settlement layer with ecosystem-driven demand. "
     "Their risk drivers differ: BTC often reacts to liquidity and macro, while ETH adds tech and ecosystem factors.\n\n"
     "A balanced view: understand correlations, avoid overconfidence, and treat both as volatile risk assets."),

    ("nasdaq-earnings-sensitivity", "NASDAQ-100: Why Earnings Sensitivity Matters",
     "Growth-heavy indices can be highly sensitive to earnings revisions and discount rates. "
     "When rates rise or growth expectations fall, multiples can compress.\n\n"
     "A practical habit: track earnings season tone, guidance, and margin trends rather than only daily price changes."),

    ("simple-trend-labels", "Trend Labels Are Not Recommendations",
     "This site uses simple 1-day change thresholds to label BULLISH/BEARISH/NEUTRAL. "
     "These are descriptive labels, not advice. They do not predict future performance.\n\n"
     "For real decision-making, combine multiple horizons (weekly/monthly), fundamentals, and risk limits."),

    ("diversification-basics", "Diversification Basics for Income Portfolios",
     "Income portfolios can become unintentionally concentrated: one sector, one factor, or one rate regime. "
     "Diversification means spreading across cash flow sources and risk drivers.\n\n"
     "Consider mixing: dividend equities, quality factors, REIT sub-sectors, and defensives—while limiting single-name exposure."),

    ("payout-ratio-explained", "Payout Ratio Explained (Without the Confusion)",
     "Payout ratio is useful, but context matters. Earnings can be cyclical and accounting-based, "
     "so free cash flow coverage often provides a clearer picture.\n\n"
     "A practical check: compare dividends paid vs. operating cash flow and capex needs over several years."),

    ("risk-disclaimer", "Research-Only Market Pages: What This Site Is (and Isn’t)",
     "This site is a compact research dashboard. It provides quotes, simple daily changes, and educational articles. "
     "It does not provide personalized financial advice.\n\n"
     "Markets involve risk. Prices can fall, dividends can change, and crypto can be highly volatile."),

    ("how-to-use-this-site", "How to Use These Terminals Efficiently",
     "Use the terminals as a quick monitor: identify what moved and where volatility is clustering. "
     "Then validate with deeper sources when making decisions.\n\n"
     "Suggested workflow: (1) scan changes, (2) check risk notes, (3) read one relevant article, (4) decide nothing in haste.")
]


# =========================================================
# Assets (자산 페이지)
# =========================================================
def all_asset_symbols() -> List[str]:
    # 통일: Crypto는 -USD 제거한 심볼로 페이지 생성
    out = set()
    for t in NASDAQ_TICKERS + DIVIDEND_TICKERS:
        out.add(t)
    for t in COIN_TICKERS:
        out.add(t.replace("-USD", ""))
    return sorted(out)

def symbol_to_yf(symbol: str) -> str:
    # Assets 페이지에서 가격도 찍어주기 위해 yfinance 심볼로 변환
    if symbol in NASDAQ_TICKERS or symbol in DIVIDEND_TICKERS:
        return symbol
    # crypto
    return f"{symbol}-USD"


# =========================================================
# Static pages
# =========================================================
def write_static_pages():
    about = f"""
    <header><h1>About</h1><div style="color:var(--muted)">What this site does</div></header>
    <div class="analysis">
      <p><strong>{SITE_NAME}</strong> publishes compact, auto-updated market monitoring pages for educational and research purposes.
      The goal is to help users scan price moves and volatility at a glance, with clear risk notes and no personalized advice.</p>
      <p>Contact: <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a></p>
      <p style="color:var(--muted)">Disclaimer: informational only. No investment advice. No recommendation to buy/sell/hold.</p>
    </div>
    """
    privacy = """
    <header><h1>Privacy Policy</h1></header>
    <div class="analysis">
      <p>This site does not ask you to create an account and does not intentionally collect personal information.</p>
      <p>Third-party vendors (including Google) may use cookies to serve ads based on prior visits.
      You can manage ad personalization through Google’s ad settings.</p>
    </div>
    """
    terms = """
    <header><h1>Terms</h1></header>
    <div class="analysis">
      <p>By using this site, you agree that all content is provided for informational and educational purposes only.</p>
      <p>No content on this site is financial, legal, or professional advice. You are responsible for your own decisions.</p>
      <p>Market data may be delayed or incomplete. We do not guarantee accuracy or availability.</p>
    </div>
    """
    contact = f"""
    <header><h1>Contact</h1></header>
    <div class="analysis">
      <p>For questions or corrections, email: <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a></p>
    </div>
    """

    (OUTPUT_DIR / "about.html").write_text(wrap_page("About", about), encoding="utf-8")
    (OUTPUT_DIR / "privacy.html").write_text(wrap_page("Privacy Policy", privacy), encoding="utf-8")
    (OUTPUT_DIR / "terms.html").write_text(wrap_page("Terms", terms), encoding="utf-8")
    (OUTPUT_DIR / "contact.html").write_text(wrap_page("Contact", contact), encoding="utf-8")


# =========================================================
# Blog writer (✅ f-string 백슬래시 오류 제거 완료)
# =========================================================
def write_blog():
    items = [f"<li><a href='/blog/{slug}.html'>{title}</a></li>" for slug, title, _ in BLOG_POSTS]
    items_html = "".join(items)  # ✅ f-string {} 안에서 join 안함(안전)

    index_body = f"""
    <header><h1>Blog</h1><div style="color:var(--muted)">Educational market notes</div></header>
    <div class="analysis"><ul>{items_html}</ul></div>
    """
    (BLOG_DIR / "index.html").write_text(wrap_page("Blog", index_body), encoding="utf-8")

    for slug, title, content in BLOG_POSTS:
        # ✅ f-string {} 안에서 "\n\n" split/join을 하지 않고, 밖에서 먼저 처리
        paragraphs = "</p><p>".join(content.split("\n\n"))

        body = f"""
        <header><h1>{title}</h1><div style="color:var(--muted)">Educational article • Research-only</div></header>
        <div class="analysis"><p>{paragraphs}</p></div>
        """
        (BLOG_DIR / f"{slug}.html").write_text(wrap_page(title, body), encoding="utf-8")


# =========================================================
# Assets writer
# =========================================================
def write_assets_pages(now_str: str):
    symbols = all_asset_symbols()
    links = "".join([f"<li><a href='/assets/{s}.html'>{s}</a></li>" for s in symbols])
    index_body = f"""
    <header><h1>Assets</h1><div style="color:var(--muted)">Auto-generated reference pages ({len(symbols)} assets)</div></header>
    <div class="analysis">
      <p>These pages provide a lightweight snapshot and risk notes for research. Data may be delayed or incomplete.</p>
      <ul>{links}</ul>
    </div>
    """
    (ASSETS_DIR / "index.html").write_text(wrap_page("Assets", index_body), encoding="utf-8")

    # 배치로 한 번에 가져오기 (가능하면)
    yf_symbols = [symbol_to_yf(s) for s in symbols]
    batch = fetch_batch_data(yf_symbols, period=PERIOD, chunk_size=CHUNK_SIZE)

    for s in symbols:
        yf_sym = symbol_to_yf(s)

        price_str = "N/A"
        chg_str = "N/A"
        note = "Data may be unavailable for some symbols."

        try:
            df = extract_symbol_df(batch, yf_sym).dropna(subset=["Close"])
            if len(df) >= 2:
                price = float(df["Close"].iloc[-1])
                prev = float(df["Close"].iloc[-2])
                chg = ((price - prev) / prev) * 100.0
                if yf_sym.endswith("-USD"):
                    price_str = format_crypto_price(price)
                else:
                    price_str = f"${price:,.2f}"
                sign = "+" if chg >= 0 else ""
                chg_str = f"{sign}{chg:.2f}%"
                note = "Snapshot is based on recent daily closes (short horizon)."
        except Exception:
            pass

        edu = (
            f"<p><strong>Risk notes:</strong> Prices can move quickly. For dividends, payouts may change. "
            f"For crypto, 24/7 volatility is normal. Use this page as a starting point for research—not a decision engine.</p>"
        )

        body = f"""
        <header>
          <h1>{s} Report</h1>
          <div style="color:var(--muted)">Last Update (US/Eastern): {now_str}</div>
        </header>
        <div class="analysis">
          <p><strong>Latest snapshot:</strong> {price_str} • <strong>1-day change:</strong> {chg_str}</p>
          <p style="color:var(--muted)">{note}</p>
          {edu}
          <p style="color:var(--muted)">Disclaimer: informational only. No recommendation to buy, sell, or hold.</p>
        </div>
        """
        (ASSETS_DIR / f"{s}.html").write_text(wrap_page(f"{s} Report", body), encoding="utf-8")


# =========================================================
# Sitemap / robots
# =========================================================
def write_robots():
    # GitHub Pages에서 robots는 간단히
    robots = f"""User-agent: *
Allow: /
Sitemap: {BASE_URL}/sitemap.xml
"""
    (OUTPUT_DIR / "robots.txt").write_text(robots, encoding="utf-8")

def write_sitemap(extra_paths: List[str]):
    # 사이트 전체 URL 수집
    urls = set(extra_paths)

    # blog
    urls.add("/blog/index.html")
    for slug, _, _ in BLOG_POSTS:
        urls.add(f"/blog/{slug}.html")

    # assets
    urls.add("/assets/index.html")
    for s in all_asset_symbols():
        urls.add(f"/assets/{s}.html")

    now_iso = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    items = []
    for path in sorted(urls):
        items.append(f"<url><loc>{BASE_URL}{path}</loc><lastmod>{now_iso}</lastmod></url>")

    sitemap = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{''.join(items)}
</urlset>
"""
    (OUTPUT_DIR / "sitemap.xml").write_text(sitemap, encoding="utf-8")


# =========================================================
# Terminal pages
# =========================================================
def write_terminals(now_str: str):
    # Crypto
    c_batch = fetch_batch_data(COIN_TICKERS, period=PERIOD, chunk_size=CHUNK_SIZE)
    c_cards, c_rate = generate_cards(COIN_TICKERS, c_batch, is_crypto=True)
    coin_body = f"""
    <header><h1>💎 Crypto Gold Terminal</h1>
    <div style="color:var(--muted)">Top assets • Research-only</div>
    <div style="color:var(--muted);font-size:12px;margin-top:6px;">Last Update (US/Eastern): {now_str} | Data Success: {c_rate:.1f}%</div>
    </header>
    <div class="grid">{c_cards}</div>
    <div class="analysis">
      <h2>Risk Notes</h2>
      <p>Crypto markets are volatile and trade 24/7. Prices may differ across venues. Use this page for research only.</p>
      <p><strong>Disclaimer:</strong> informational only and not financial advice.</p>
    </div>
    """
    (OUTPUT_DIR / "coin.html").write_text(wrap_page("Crypto Terminal", coin_body), encoding="utf-8")

    # Dividend
    d_batch = fetch_batch_data(DIVIDEND_TICKERS, period=PERIOD, chunk_size=CHUNK_SIZE)
    d_cards, d_rate = generate_cards(DIVIDEND_TICKERS, d_batch, is_crypto=False)
    div_body = f"""
    <header><h1>💰 Dividend Terminal Pro</h1>
    <div style="color:var(--muted)">Income-focused watchlist snapshot • Research-only</div>
    <div style="color:var(--muted);font-size:12px;margin-top:6px;">Last Update (US/Eastern): {now_str} | Data Success: {d_rate:.1f}%</div>
    </header>
    <div class="grid">{d_cards}</div>
    <div class="analysis">
      <h2>Yield, Quality, and Sustainability</h2>
      <p>Dividend payments are not guaranteed. Evaluate payout sustainability, free cash flow, and balance-sheet strength.</p>
      <p><strong>Disclaimer:</strong> informational only and not financial advice.</p>
    </div>
    """
    (OUTPUT_DIR / "dividend.html").write_text(wrap_page("Dividend Terminal", div_body), encoding="utf-8")

    # NASDAQ
    n_batch = fetch_batch_data(NASDAQ_TICKERS + ["QQQ", "^VIX"], period=PERIOD, chunk_size=CHUNK_SIZE)
    table_html, n_rate, sentiment = generate_nasdaq_table(NASDAQ_TICKERS, n_batch)

    qqq = "N/A"
    vix = "N/A"
    try:
        qqq_df = extract_symbol_df(n_batch, "QQQ").dropna(subset=["Close"])
        vix_df = extract_symbol_df(n_batch, "^VIX").dropna(subset=["Close"])
        if len(qqq_df):
            qqq = f"${float(qqq_df['Close'].iloc[-1]):,.2f}"
        if len(vix_df):
            vix = f"{float(vix_df['Close'].iloc[-1]):,.2f}"
    except Exception:
        pass

    nasdaq_body = f"""
    <header><h1>🚀 NASDAQ-100 Live Intelligence</h1>
      <div style="color:var(--muted)">Last Update (US/Eastern): {now_str} • Sentiment: <strong>{sentiment}</strong> • Data Success: {n_rate:.1f}%</div>
      <div style="color:var(--muted);font-size:12px;margin-top:6px;">
        Trend labels (BULLISH/BEARISH/NEUTRAL) are based on simple 1-day % moves and are not investment advice.
      </div>
    </header>

    <div class="analysis">
      <p><strong>QQQ:</strong> {qqq} &nbsp; | &nbsp; <strong>VIX:</strong> {vix}</p>
    </div>

    <table>
      <thead><tr><th>Ticker</th><th>Price ($)</th><th>Change (%)</th><th>1-Day Trend</th></tr></thead>
      <tbody>{table_html}</tbody>
    </table>

    <div class="analysis">
      <h2>Context</h2>
      <p>This is a monitoring dashboard. Trend labels are descriptive and do not predict future performance.</p>
      <p><strong>Disclaimer:</strong> informational only. No recommendation to buy, sell, or hold any security.</p>
    </div>
    """
    (OUTPUT_DIR / "nasdaq.html").write_text(wrap_page("NASDAQ Terminal", nasdaq_body), encoding="utf-8")


# =========================================================
# Home
# =========================================================
def write_home(now_str: str):
    body = f"""
    <header>
      <h1>{SITE_NAME}</h1>
      <div style="color:var(--muted)">Auto-updated market terminals • Research & education only</div>
      <div style="color:var(--muted);font-size:12px;margin-top:6px;">Last Update (US/Eastern): {now_str}</div>
    </header>

    <div class="analysis">
      <h2>Start here</h2>
      <ul>
        <li><a href="/coin.html">Crypto Terminal</a> — major digital assets snapshot</li>
        <li><a href="/dividend.html">Dividend Terminal</a> — income-focused watchlist snapshot</li>
        <li><a href="/nasdaq.html">NASDAQ Terminal</a> — tech index monitoring with trend labels</li>
        <li><a href="/assets/index.html">Assets</a> — individual reference pages</li>
        <li><a href="/blog/index.html">Blog</a> — educational articles</li>
      </ul>
      <p style="color:var(--muted)">Disclaimer: informational only. No investment advice.</p>
    </div>
    """
    (OUTPUT_DIR / "index.html").write_text(wrap_page("Home", body), encoding="utf-8")


# =========================================================
# Main
# =========================================================
def main():
    now_str = us_eastern_now_str()

    # 1) Domain files
    (OUTPUT_DIR / "CNAME").write_text(CUSTOM_DOMAIN + "\n", encoding="utf-8")
    (OUTPUT_DIR / "ads.txt").write_text(ADS_TXT_LINE + "\n", encoding="utf-8")

    # 2) Static pages
    write_static_pages()

    # 3) Blog + Assets
    write_blog()
    write_assets_pages(now_str)

    # 4) Terminals + Home
    write_terminals(now_str)
    write_home(now_str)

    # 5) SEO
    write_robots()
    write_sitemap(extra_paths=[
        "/index.html", "/coin.html", "/dividend.html", "/nasdaq.html",
        "/about.html", "/privacy.html", "/terms.html", "/contact.html",
    ])

    # 6) Git Push (Actions에서만 의미)
    try:
        subprocess.run(["git", "config", "user.name", "github-actions"], check=True)
        subprocess.run(["git", "config", "user.email", "github-actions@github.com"], check=True)
        subprocess.run(["git", "add", "."], check=True)
        if subprocess.run(["git", "diff", "--cached", "--quiet"]).returncode != 0:
            subprocess.run(["git", "commit", "-m", f"🚀 Build: {now_str}"], check=True)
            subprocess.run(["git", "push"], check=True)
    except Exception:
        pass


if __name__ == "__main__":
    main()
