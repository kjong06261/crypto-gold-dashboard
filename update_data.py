import yfinance as yf
import pandas as pd
import datetime
import time
import random
import subprocess
from typing import List, Tuple, Dict
from pathlib import Path

# =========================================================
# Configuration
# =========================================================
OUTPUT_DIR = Path("./")
MAX_RETRIES = 4
BASE_DELAY = 1.5
CHUNK_SIZE = 25  # ✅ yfinance 안정화 핵심: 한 번에 너무 많이 때리지 않기

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
# HTML Templates
# =========================================================
CACHE_META = (
    '<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">'
    '<meta http-equiv="Pragma" content="no-cache"><meta http-equiv="Expires" content="0">'
)

COIN_TEMPLATE = """<!DOCTYPE html><html lang="ko"><head><meta charset="UTF-8">{cache_meta}<meta name="viewport" content="width=device-width, initial-scale=1.0"><title>PREMIUM CRYPTO TERMINAL</title><style>:root {{ --bg: #05070a; --card-bg: #11141b; --border: #1e222d; --text: #d1d4dc; --accent: #fbbf24; }}body {{ background-color: var(--bg); color: var(--text); font-family: 'Trebuchet MS', sans-serif; margin: 0; padding: 20px; }}.container {{ max-width: 1200px; margin: 0 auto; }}header {{ border-bottom: 2px solid var(--accent); padding-bottom: 20px; margin-bottom: 40px; }}h1 {{ font-size: 38px; color: #ffffff; margin: 0; letter-spacing: -1px; }}.grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 12px; }}.card {{ background: var(--card-bg); border: 1px solid var(--border); padding: 15px; border-radius: 6px; transition: all 0.2s; }}.card:hover {{ background: #1c212d; border-color: var(--accent); }}.card-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }}.symbol {{ font-weight: bold; font-size: 16px; color: #fff; }}.price {{ font-size: 24px; font-weight: 700; color: #ffffff; }}.pct {{ font-size: 13px; font-weight: bold; padding: 2px 6px; border-radius: 4px; }}.up {{ color: #00ffaa; background: rgba(0, 255, 170, 0.1); }}.down {{ color: #ff3b3b; background: rgba(255, 59, 59, 0.1); }}.na {{ color: #888; background: rgba(136, 136, 136, 0.1); }}footer {{ margin-top: 80px; padding: 40px; text-align: center; font-size: 0.8rem; color: #8b949e; border-top: 1px solid var(--border); }}</style></head><body><div class="container"><header><h1>💎 CRYPTO GOLD TERMINAL</h1><div style="color:#888;">REAL-TIME BLOCKCHAIN FEED • AUTO-UPDATED</div><div style="font-size:0.8rem; color:#666; margin-top:5px;">Last Update: {update_time} | Success: {success_rate}%</div></header><h2 style="color:var(--accent); border-left:4px solid var(--accent); padding-left:10px;">GLOBAL CRYPTO MARKET (TOP 100)</h2><div class="grid">{content}</div><footer><div style="margin-bottom:20px;"><strong>⚠️ INVESTMENT DISCLAIMER</strong><br>Data provided is for informational purposes only. Not financial advice.</div><div>© 2025 CRYPTO-GOLD-DASHBOARD • GITHUB ACTIONS</div></footer></div></body></html>"""

DIV_TEMPLATE = """<!DOCTYPE html><html lang="ko"><head><meta charset="UTF-8">{cache_meta}<meta name="viewport" content="width=device-width, initial-scale=1.0"><title>PREMIUM DIVIDEND TERMINAL</title><style>:root {{ --bg: #05070a; --card-bg: #11141b; --border: #1e222d; --text: #d1d4dc; --accent: #00ffaa; }}body {{ background-color: var(--bg); color: var(--text); font-family: 'Trebuchet MS', sans-serif; margin: 0; padding: 20px; }}.container {{ max-width: 1200px; margin: 0 auto; }}header {{ border-bottom: 2px solid var(--accent); padding-bottom: 20px; margin-bottom: 40px; }}h1 {{ font-size: 38px; color: #ffffff; margin: 0; letter-spacing: -1px; }}.grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 12px; }}.card {{ background: var(--card-bg); border: 1px solid var(--border); padding: 15px; border-radius: 6px; transition: all 0.2s; }}.card:hover {{ background: #1c212d; border-color: var(--accent); }}.card-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }}.symbol {{ font-weight: bold; font-size: 16px; color: #fff; }}.price {{ font-size: 24px; font-weight: 700; color: #ffffff; }}.pct {{ font-size: 13px; font-weight: bold; padding: 2px 6px; border-radius: 4px; }}.up {{ color: #00ffaa; background: rgba(0, 255, 170, 0.1); }}.down {{ color: #ff3b3b; background: rgba(255, 59, 59, 0.1); }}.na {{ color: #888; background: rgba(136, 136, 136, 0.1); }}footer {{ margin-top: 80px; padding: 40px; text-align: center; font-size: 0.8rem; color: #8b949e; border-top: 1px solid var(--border); }}</style></head><body><div class="container"><header><h1>💰 DIVIDEND TERMINAL PRO</h1><div style="color:#888;">LIVE MARKET DATA • AUTO-UPDATED</div><div style="font-size:0.8rem; color:#666; margin-top:5px;">Last Update: {update_time} | Success: {success_rate}%</div></header><h2 style="color:var(--accent); border-left:4px solid var(--accent); padding-left:10px;">DIVIDEND KINGS (TOP 100)</h2><div class="grid">{content}</div><footer><div style="margin-bottom:20px;"><strong>⚠️ INVESTMENT DISCLAIMER</strong><br>Data provided is for informational purposes only. Not financial advice.</div><div>© 2025 CRYPTO-GOLD-DASHBOARD • GITHUB ACTIONS</div></footer></div></body></html>"""

INDEX_TEMPLATE = """<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">{cache_meta}<title>NASDAQ Real-Time Terminal</title><style>body {{ background: #0b0e14; color: #e2e8f0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; padding: 20px; margin: 0; }}.dashboard {{ max-width: 1200px; margin: 0 auto; background: #161b22; border: 1px solid #30363d; padding: 30px; border-radius: 12px; box-shadow: 0 8px 32px rgba(0,0,0,0.3); }}.grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }}.stat-card {{ background: #0d1117; padding: 20px; border-radius: 8px; border-top: 4px solid #00ff88; transition: transform 0.2s; }}.stat-card:hover {{ transform: translateY(-2px); }}.stat-title {{ color: #8b949e; font-size: 0.9rem; margin-bottom: 5px; text-transform: uppercase; letter-spacing: 0.5px; }}.price {{ font-size: 2rem; font-weight: bold; color: #ffffff; }}table {{ width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 0.95rem; }}th {{ background: #21262d; color: #8b949e; padding: 15px; text-align: left; border-bottom: 2px solid #30363d; text-transform: uppercase; font-size: 0.85rem; letter-spacing: 0.5px; }}td {{ padding: 12px 15px; border-bottom: 1px solid #30363d; }}tr:hover {{ background: #21262d; }}.up {{ color: #39d353; font-weight: bold; }}.down {{ color: #ff7b72; font-weight: bold; }}footer {{ margin-top: 60px; padding-top: 30px; border-top: 1px solid #30363d; color: #8b949e; font-size: 0.8rem; text-align: center; }}</style></head><body><div class="dashboard"><h1>🚀 NASDAQ-100 Live Intelligence</h1><div style="color:#8b949e; margin-bottom:20px; font-size:0.9rem;">Real-time market data • Last Update: {update_time} | Success: {success_rate}%</div><div class="grid"><div class="stat-card"><div class="stat-title">QQQ ETF Price</div><div class="price">{qqq_price}</div></div><div class="stat-card" style="border-top-color:#58a6ff;"><div class="stat-title">Market Sentiment</div><div class="price" style="font-size:1.5rem;">{sentiment}</div></div><div class="stat-card" style="border-top-color:#e3b341;"><div class="stat-title">VIX Index</div><div class="price">{vix_price}</div></div></div><h3 style="color:#fff; margin-top:40px;">Top Technology Constituents</h3><table><thead><tr><th>Ticker</th><th>Price ($)</th><th>Change (%)</th><th>Signal</th></tr></thead><tbody>{content}</tbody></table><footer><strong>⚠️ INVESTMENT DISCLAIMER</strong><br>Auto-updated data. Not financial advice.<br>© 2025 CRYPTO-GOLD-DASHBOARD • GITHUB ACTIONS</footer></div></body></html>"""

# =========================================================
# Core Functions
# =========================================================
def kst_now_str() -> str:
    return (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=9)).strftime("%Y-%m-%d %H:%M KST")

def fetch_batch_data(tickers: List[str], period: str = "5d", chunk_size: int = CHUNK_SIZE) -> pd.DataFrame:
    """
    ✅ yfinance 안정성 핵심:
    - tickers를 chunk로 나눠서 여러 번 다운로드
    - 실패 시 재시도 + jitter
    """
    frames = []
    for i in range(0, len(tickers), chunk_size):
        chunk = tickers[i:i + chunk_size]
        df = pd.DataFrame()

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                print(f"[{attempt}/{MAX_RETRIES}] Fetching chunk {i//chunk_size + 1} ({len(chunk)} tickers)...")
                df = yf.download(
                    chunk,
                    period=period,
                    group_by="ticker",
                    threads=True,
                    progress=False,
                    auto_adjust=True,
                )
                if df is not None and not df.empty:
                    break
            except Exception as e:
                print(f"❌ Attempt {attempt} failed (chunk): {e}")

            if attempt < MAX_RETRIES:
                time.sleep(BASE_DELAY * attempt + random.uniform(0, 0.35))

        if df is not None and not df.empty:
            frames.append(df)

    if not frames:
        return pd.DataFrame()

    # 대부분 MultiIndex로 (ticker, field) 형태로 들어옴 → 열 방향 concat
    if isinstance(frames[0].columns, pd.MultiIndex):
        return pd.concat(frames, axis=1)
    # 단일 형태로 들어오는 경우 (드물지만) → 행 방향 concat
    return pd.concat(frames, axis=0)

def extract_symbol_df(batch_data: pd.DataFrame, symbol: str) -> pd.DataFrame:
    if batch_data is None or batch_data.empty:
        raise ValueError("Empty batch_data")

    sym = symbol
    symU = symbol.upper()

    if isinstance(batch_data.columns, pd.MultiIndex):
        lvl0 = set(map(str, batch_data.columns.levels[0]))
        if sym in lvl0:
            df = batch_data[sym]
        elif symU in lvl0:
            df = batch_data[symU]
        else:
            raise ValueError(f"Symbol not found: {symbol}")
        if "Close" not in df.columns:
            raise ValueError(f"No Close for: {symbol}")
        return df

    # single ticker (columns: Open/High/Low/Close/Volume ...)
    if "Close" in batch_data.columns:
        return batch_data

    raise ValueError("Unsupported data format")

def format_crypto_price(price: float) -> str:
    if price < 0.01:
        return f"${price:,.8f}"
    elif price < 1.0:
        return f"${price:,.6f}"
    else:
        return f"${price:,.2f}"

def calc_change_pct(price: float, prev: float) -> float:
    if prev is None or prev <= 0:
        raise ValueError("Invalid prev price")
    return ((price - prev) / prev) * 100.0

def generate_html_from_batch(
    tickers: List[str],
    batch_data: pd.DataFrame,
    mode: str = "card"
) -> Tuple[str, Dict]:
    html = ""
    success, fail = 0, 0
    ups, downs = 0, 0

    for symbol in tickers:
        try:
            df = extract_symbol_df(batch_data, symbol).dropna(subset=["Close"])
            if len(df) < 2:
                raise ValueError("Too short")

            price = float(df["Close"].iloc[-1])
            prev = float(df["Close"].iloc[-2])
            change = calc_change_pct(price, prev)

            cls, sign = ("up", "+") if change >= 0 else ("down", "")
            if change >= 0:
                ups += 1
            else:
                downs += 1

            if mode == "card":
                p_str = format_crypto_price(price) if "-USD" in symbol else f"${price:,.2f}"
                html += (
                    f'<div class="card"><div class="card-header">'
                    f'<span class="symbol">{symbol.replace("-USD","")}</span>'
                    f'<span class="pct {cls}">{sign}{change:.2f}%</span>'
                    f'</div><div class="price">{p_str}</div></div>'
                )
            elif mode == "table":
                sig = "BUY" if change > 0.5 else ("SELL" if change < -0.5 else "HOLD")
                sig_col = "#39d353" if sig == "BUY" else ("#ff7b72" if sig == "SELL" else "#888")
                html += (
                    f"<tr><td style='color:#fff;'>{symbol}</td>"
                    f"<td>${price:,.2f}</td>"
                    f"<td class='{cls}'>{sign}{change:.2f}%</td>"
                    f"<td style='color:{sig_col};'>{sig}</td></tr>"
                )

            success += 1
        except Exception:
            fail += 1
            if mode == "card":
                html += (
                    f'<div class="card" style="opacity:0.4;">'
                    f'<div class="card-header"><span class="symbol">{symbol.replace("-USD","")}</span>'
                    f'<span class="pct na">N/A</span></div>'
                    f'<div class="price">N/A</div></div>'
                )
            else:
                html += f"<tr><td>{symbol}</td><td>-</td><td>-</td><td>N/A</td></tr>"

    rate = (success / len(tickers) * 100) if tickers else 0.0
    up_ratio = (ups / max(1, (ups + downs))) * 100.0
    sentiment = "BULLISH" if up_ratio >= 60 else ("BEARISH" if up_ratio <= 40 else "NEUTRAL")

    return html, {
        "rate": rate,
        "success": success,
        "fail": fail,
        "ups": ups,
        "downs": downs,
        "up_ratio": up_ratio,
        "sentiment": sentiment,
    }

def safe_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)

def git_push_if_changed(commit_msg: str) -> None:
    try:
        subprocess.run(["git", "config", "user.name", "github-actions"], check=True)
        subprocess.run(["git", "config", "user.email", "github-actions@github.com"], check=True)
        subprocess.run(["git", "add", "."], check=True)

        # ✅ 변경 없으면 스킵 (git commit exit 1 방지)
        diff_check = subprocess.run(["git", "diff", "--cached", "--quiet"])
        if diff_check.returncode == 0:
            print("Git Push Skipped (No changes)")
            return

        subprocess.run(["git", "commit", "-m", commit_msg], check=True)
        subprocess.run(["git", "push"], check=True)
        print("Git Push OK")
    except Exception as e:
        print(f"Git Push Skipped (Error): {e}")

# =========================================================
# Main
# =========================================================
def main():
    now_str = kst_now_str()

    # 1) Crypto
    c_batch = fetch_batch_data(COIN_TICKERS, period="5d")
    c_html, c_stats = generate_html_from_batch(COIN_TICKERS, c_batch, mode="card")
    safe_write_text(
        OUTPUT_DIR / "coin.html",
        COIN_TEMPLATE.format(
            cache_meta=CACHE_META,
            update_time=now_str,
            success_rate=f"{c_stats['rate']:.1f}",
            content=c_html,
        ),
    )
    print(f"[CRYPTO] success={c_stats['success']}, fail={c_stats['fail']}, rate={c_stats['rate']:.1f}%")

    # 2) Dividend
    d_batch = fetch_batch_data(DIVIDEND_TICKERS, period="5d")
    d_html, d_stats = generate_html_from_batch(DIVIDEND_TICKERS, d_batch, mode="card")
    safe_write_text(
        OUTPUT_DIR / "dividend.html",
        DIV_TEMPLATE.format(
            cache_meta=CACHE_META,
            update_time=now_str,
            success_rate=f"{d_stats['rate']:.1f}",
            content=d_html,
        ),
    )
    print(f"[DIVIDEND] success={d_stats['success']}, fail={d_stats['fail']}, rate={d_stats['rate']:.1f}%")

    # 3) Nasdaq (plus QQQ & VIX)
    extra = ["QQQ", "^VIX"]
    n_batch = fetch_batch_data(NASDAQ_TICKERS + extra, period="5d")
    n_html, n_stats = generate_html_from_batch(NASDAQ_TICKERS, n_batch, mode="table")

    # QQQ / VIX 값 (별도 안전 추출)
    try:
        qqq_val = float(extract_symbol_df(n_batch, "QQQ")["Close"].iloc[-1])
        qqq = f"${qqq_val:,.2f}"
    except Exception:
        qqq = "N/A"

    try:
        vix_val = float(extract_symbol_df(n_batch, "^VIX")["Close"].iloc[-1])
        vix = f"{vix_val:,.2f}"
    except Exception:
        vix = "N/A"

    # ✅ sentiment는 나스닥 상승 비율 기반 자동
    safe_write_text(
        OUTPUT_DIR / "index.html",
        INDEX_TEMPLATE.format(
            cache_meta=CACHE_META,
            update_time=now_str,
            success_rate=f"{n_stats['rate']:.1f}",
            content=n_html,
            qqq_price=qqq,
            vix_price=vix,
            sentiment=n_stats["sentiment"],
        ),
    )
    print(f"[NASDAQ] success={n_stats['success']}, fail={n_stats['fail']}, rate={n_stats['rate']:.1f}%, sentiment={n_stats['sentiment']}")

    # Git Push
    git_push_if_changed(f"🚀 Update: {now_str}")

if __name__ == "__main__":
    main()
