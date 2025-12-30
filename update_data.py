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
OUTPUT_DIR = Path("./")
MAX_RETRIES = 4
BASE_DELAY = 1.5
CHUNK_SIZE = 25
PERIOD = "5d"
TIMEZONE = "US/Eastern"


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
# HTML Templates
# =========================================================
CACHE_META = (
    '<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">'
    '<meta http-equiv="Pragma" content="no-cache">'
    '<meta http-equiv="Expires" content="0">'
)

COIN_TEMPLATE = """<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">{cache_meta}<meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Premium Crypto Terminal - Top 100 Real-Time Data</title><style>:root {{ --bg: #05070a; --card-bg: #11141b; --border: #1e222d; --text: #d1d4dc; --accent: #fbbf24; }}body {{ background-color: var(--bg); color: var(--text); font-family: 'Trebuchet MS', sans-serif; margin: 0; padding: 20px; }}.container {{ max-width: 1200px; margin: 0 auto; }}header {{ border-bottom: 2px solid var(--accent); padding-bottom: 20px; margin-bottom: 40px; }}h1 {{ font-size: 38px; color: #ffffff; margin: 0; letter-spacing: -1px; }}.grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 12px; }}.card {{ background: var(--card-bg); border: 1px solid var(--border); padding: 15px; border-radius: 6px; }}.up {{ color: #00ffaa; }}.down {{ color: #ff3b3b; }}.symbol {{ font-weight: bold; font-size: 16px; color: #fff; }}.price {{ font-size: 24px; font-weight: 700; color: #ffffff; }}.pct {{ font-size: 13px; font-weight: bold; padding: 2px 6px; border-radius: 4px; background: rgba(255,255,255,0.05); }}.analysis {{ margin-top: 50px; padding: 30px; background: #11141b; border-radius: 8px; line-height: 1.8; border-left: 4px solid var(--accent); }} footer {{ margin-top: 80px; padding: 40px; text-align: center; font-size: 0.8rem; color: #8b949e; border-top: 1px solid var(--border); }}</style></head><body><div class="container"><header><h1>💎 Crypto Gold Terminal</h1><div style="color:#888;">Real-time blockchain market feed • Top 100 assets</div><div style="font-size:0.8rem; color:#666; margin-top:5px;">Last Update (US/Eastern): {update_time} | Data Success: {success_rate}%</div></header><div class="grid">{content}</div><section class="analysis"><h2>Crypto Market Overview, Volatility, and Risk Notes</h2><p>This page tracks major digital assets across the global cryptocurrency market, including Bitcoin, Ethereum, and widely traded altcoins. The primary objective is to present recent price changes and short-term momentum signals in a compact terminal format.</p><p><strong>How to read this dashboard:</strong> Each card shows the latest adjusted closing price and the percentage change from the prior session. Large moves can reflect macro events, exchange-specific liquidity, news-driven spikes, or broader risk-on/risk-off shifts in global markets.</p><p><strong>Important:</strong> Cryptocurrency markets can be highly volatile and may trade 24/7. Prices may differ slightly across venues. Use this information for research and educational purposes only.</p><p><strong>Disclaimer:</strong> This content is informational only and does not constitute financial advice.</p></section><footer>© 2025 CRYPTO-GOLD-DASHBOARD • Automated Market Pages</footer></div></body></html>"""

DIV_TEMPLATE = """<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">{cache_meta}<meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Premium Dividend Terminal - High Yield Assets</title><style>:root {{ --bg: #05070a; --card-bg: #11141b; --border: #1e222d; --text: #d1d4dc; --accent: #00ffaa; }}body {{ background-color: var(--bg); color: var(--text); font-family: 'Trebuchet MS', sans-serif; margin: 0; padding: 20px; }}.container {{ max-width: 1200px; margin: 0 auto; }}header {{ border-bottom: 2px solid var(--accent); padding-bottom: 20px; margin-bottom: 40px; }}h1 {{ font-size: 38px; color: #ffffff; margin: 0; letter-spacing: -1px; }}.grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 12px; }}.card {{ background: var(--card-bg); border: 1px solid var(--border); padding: 15px; border-radius: 6px; }}.up {{ color: #00ffaa; }}.down {{ color: #ff3b3b; }}.symbol {{ font-weight: bold; font-size: 16px; color: #fff; }}.price {{ font-size: 24px; font-weight: 700; color: #ffffff; }}.pct {{ font-size: 13px; font-weight: bold; padding: 2px 6px; border-radius: 4px; background: rgba(255,255,255,0.05); }}.analysis {{ margin-top: 50px; padding: 30px; background: #11141b; border-radius: 8px; line-height: 1.8; border-left: 4px solid var(--accent); }} footer {{ margin-top: 80px; padding: 40px; text-align: center; font-size: 0.8rem; color: #8b949e; border-top: 1px solid var(--border); }}</style></head><body><div class="container"><header><h1>💰 Dividend Terminal Pro</h1><div style="color:#888;">Income-focused market feed • High-quality dividend assets</div><div style="font-size:0.8rem; color:#666; margin-top:5px;">Last Update (US/Eastern): {update_time} | Data Success: {success_rate}%</div></header><div class="grid">{content}</div><section class="analysis"><h2>Dividend Investing Notes: Yield, Quality, and Risk Controls</h2><p>Dividend strategies aim to generate consistent cash flow through distributions while balancing equity risk. This terminal highlights popular income assets such as dividend ETFs and widely held dividend stocks.</p><p><strong>What matters beyond yield:</strong> payout ratios, free cash flow durability, balance-sheet strength, sector concentration, and interest-rate sensitivity are key factors for long-term income outcomes.</p><p><strong>Reminder:</strong> Dividend payments are not guaranteed. Prices can decline even when yields appear attractive. Always evaluate sustainability rather than headline yield alone.</p><p><strong>Disclaimer:</strong> This content is informational only and does not constitute financial advice.</p></section><footer>© 2025 CRYPTO-GOLD-DASHBOARD • Automated Income Pages</footer></div></body></html>"""

INDEX_TEMPLATE = """<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">{cache_meta}<title>NASDAQ Real-Time Terminal - Tech Sector Intelligence</title><style>body {{ background: #0b0e14; color: #e2e8f0; font-family: sans-serif; padding: 20px; margin: 0; }}.dashboard {{ max-width: 1200px; margin: 0 auto; background: #161b22; border: 1px solid #30363d; padding: 30px; border-radius: 12px; }}.grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }}.stat-card {{ background: #0d1117; padding: 20px; border-radius: 8px; border-top: 4px solid #00ff88; }}.stat-title {{ color: #8b949e; font-size: 0.9rem; margin-bottom: 5px; text-transform: uppercase; }}.price {{ font-size: 2rem; font-weight: bold; color: #ffffff; }}table {{ width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 0.95rem; }}th {{ background: #21262d; color: #8b949e; padding: 15px; text-align: left; border-bottom: 2px solid #30363d; }}td {{ padding: 12px 15px; border-bottom: 1px solid #30363d; }}tr:hover {{ background: #21262d; }}.up {{ color: #39d353; font-weight: bold; }}.down {{ color: #ff7b72; font-weight: bold; }}.analysis {{ margin-top: 50px; padding: 30px; background: #0d1117; border-radius: 8px; line-height: 1.8; border: 1px solid #30363d; }} footer {{ margin-top: 60px; padding: 30px; border-top: 1px solid #30363d; color: #8b949e; font-size: 0.8rem; text-align: center; }}</style></head><body><div class="dashboard"><h1>🚀 NASDAQ-100 Live Intelligence</h1><div style="color:#8b949e; margin-bottom:10px; font-size:0.9rem;">Real-time technology market feed • Last Update (US/Eastern): {update_time} • Sentiment: {sentiment}</div><div style="color:#8b949e; font-size:0.85rem; margin-bottom:20px;">Informational only. Trend labels are derived from simple 1-day price changes and are not investment advice.</div><div class="grid"><div class="stat-card"><div class="stat-title">QQQ ETF Price</div><div class="price">{qqq_price}</div></div><div class="stat-card" style="border-top-color:#58a6ff;"><div class="stat-title">Market Sentiment</div><div class="price" style="font-size:1.5rem;">{sentiment}</div></div><div class="stat-card" style="border-top-color:#e3b341;"><div class="stat-title">Volatility (VIX)</div><div class="price">{vix_price}</div></div></div><table><thead><tr><th>Ticker</th><th>Price ($)</th><th>Change (%)</th><th>1-Day Trend</th></tr></thead><tbody>{content}</tbody></table><section class="analysis"><h2>Technology Sector Commentary and Risk Context</h2><p>The NASDAQ-100 is a key benchmark for large-cap innovation and growth-oriented companies. Monitoring its constituents helps investors understand market leadership, earnings sensitivity, and macro-driven valuation shifts.</p><p><strong>How to use trend labels:</strong> The BULLISH/BEARISH/NEUTRAL markers on this page are based solely on short-term percentage moves and do not predict future performance. They are not a substitute for comprehensive analysis.</p><p><strong>VIX and QQQ:</strong> VIX is a popular proxy for equity volatility expectations. QQQ reflects broader NASDAQ-100 exposure. Together they provide a quick view of risk appetite.</p><p><strong>Disclaimer:</strong> This content is informational only and does not constitute financial advice. No recommendation is made to buy, sell, or hold any security.</p></section><footer>© 2025 CRYPTO-GOLD-DASHBOARD • Automated Index Pages</footer></div></body></html>"""


# =========================================================
# Time helpers
# =========================================================
def us_eastern_now_str() -> str:
    if ZoneInfo:
        tz = ZoneInfo(TIMEZONE)
        return datetime.datetime.now(tz).strftime("%Y-%m-%d %H:%M %Z")
    # Fallback: UTC only if zoneinfo is unavailable
    utc_now = datetime.datetime.now(datetime.timezone.utc)
    return utc_now.strftime("%Y-%m-%d %H:%M UTC")


# =========================================================
# yfinance normalization
# Some yfinance downloads return MultiIndex as (Field, Ticker) instead of (Ticker, Field).
# This function forces it to (Ticker, Field) when possible.
# =========================================================
PRICE_FIELDS = {"Open", "High", "Low", "Close", "Adj Close", "Volume"}

def normalize_yf_columns(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return df
    if isinstance(df.columns, pd.MultiIndex) and df.columns.nlevels == 2:
        lvl0 = set(df.columns.get_level_values(0))
        lvl1 = set(df.columns.get_level_values(1))
        # If level 0 looks like fields, swap to make (Ticker, Field)
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
    # Light sanity checks to catch obvious bad feeds (too small).
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

            # Safer "trend label" (not action)
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
                f"<td style='color:#fff;'>{symbol}</td>"
                f"<td>${price:,.2f}</td>"
                f"<td class='{cls}'>{sign}{change:.2f}%</td>"
                f"<td style='color:{marker_color};'>{marker}</td>"
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
                    f"<td style='color:#fff;'>{symbol}</td>"
                    f"<td>${price:,.2f}</td>"
                    f"<td class='{cls}'>{sign}{change:.2f}%</td>"
                    f"<td style='color:{marker_color};'>{marker}</td>"
                    f"</tr>"
                )
                success += 1
            except Exception:
                html += f"<tr><td>{symbol}</td><td>-</td><td>-</td><td>N/A</td></tr>"

    rate = (success / len(tickers) * 100.0) if tickers else 0.0
    sentiment = "BULLISH" if (ups / max(1, success)) > 0.6 else ("BEARISH" if (ups / max(1, success)) < 0.4 else "NEUTRAL")
    return html, {"rate": rate, "sentiment": sentiment}


# =========================================================
# Main
# =========================================================
def main():
    now_str = us_eastern_now_str()

    # 1) Crypto
    c_batch = fetch_batch_data(COIN_TICKERS, period=PERIOD, chunk_size=CHUNK_SIZE)
    c_html, c_stats = generate_cards(COIN_TICKERS, c_batch, is_crypto=True)
    (OUTPUT_DIR / "coin.html").write_text(
        COIN_TEMPLATE.format(
            cache_meta=CACHE_META,
            update_time=now_str,
            success_rate=f"{c_stats['rate']:.1f}",
            content=c_html
        ),
        encoding="utf-8"
    )

    # 2) Dividend
    d_batch = fetch_batch_data(DIVIDEND_TICKERS, period=PERIOD, chunk_size=CHUNK_SIZE)
    d_html, d_stats = generate_cards(DIVIDEND_TICKERS, d_batch, is_crypto=False)
    (OUTPUT_DIR / "dividend.html").write_text(
        DIV_TEMPLATE.format(
            cache_meta=CACHE_META,
            update_time=now_str,
            success_rate=f"{d_stats['rate']:.1f}",
            content=d_html
        ),
        encoding="utf-8"
    )

    # 3) NASDAQ
    n_batch = fetch_batch_data(NASDAQ_TICKERS + ["QQQ", "^VIX"], period=PERIOD, chunk_size=CHUNK_SIZE)
    n_html, n_stats = generate_table(NASDAQ_TICKERS, n_batch)

    try:
        qqq_df = extract_symbol_df(n_batch, "QQQ").dropna(subset=["Close"])
        vix_df = extract_symbol_df(n_batch, "^VIX").dropna(subset=["Close"])
        qqq = f"${float(qqq_df['Close'].iloc[-1]):,.2f}" if len(qqq_df) else "N/A"
        vix = f"{float(vix_df['Close'].iloc[-1]):,.2f}" if len(vix_df) else "N/A"
    except Exception:
        qqq, vix = "N/A", "N/A"

    (OUTPUT_DIR / "index.html").write_text(
        INDEX_TEMPLATE.format(
            cache_meta=CACHE_META,
            update_time=now_str,
            content=n_html,
            qqq_price=qqq,
            vix_price=vix,
            sentiment=n_stats["sentiment"]
        ),
        encoding="utf-8"
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
