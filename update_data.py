import yfinance as yf
import pandas as pd
import datetime
import time
import random
import os
import json
import subprocess
from typing import Optional, List, Tuple, Dict
from pathlib import Path

# =========================================================
# Configuration
# =========================================================
OUTPUT_DIR = Path("./")
MAX_RETRIES = 4
BASE_DELAY = 1.5

# =========================================================
# Tickers (100개 리스트 유지)
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
# HTML Templates (f 빼고 변수 지연 주입)
# =========================================================
CACHE_META = '<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate"><meta http-equiv="Pragma" content="no-cache"><meta http-equiv="Expires" content="0">'

COIN_TEMPLATE = """<!DOCTYPE html><html lang="ko"><head><meta charset="UTF-8">{cache_meta}<meta name="viewport" content="width=device-width, initial-scale=1.0"><title>PREMIUM CRYPTO TERMINAL</title><style>:root {{ --bg: #05070a; --card-bg: #11141b; --border: #1e222d; --text: #d1d4dc; --accent: #fbbf24; }}body {{ background-color: var(--bg); color: var(--text); font-family: 'Trebuchet MS', sans-serif; margin: 0; padding: 20px; }}.container {{ max-width: 1200px; margin: 0 auto; }}header {{ border-bottom: 2px solid var(--accent); padding-bottom: 20px; margin-bottom: 40px; }}h1 {{ font-size: 38px; color: #ffffff; margin: 0; letter-spacing: -1px; }}.grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 12px; }}.card {{ background: var(--card-bg); border: 1px solid var(--border); padding: 15px; border-radius: 6px; transition: all 0.2s; }}.card:hover {{ background: #1c212d; border-color: var(--accent); }}.card-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }}.symbol {{ font-weight: bold; font-size: 16px; color: #fff; }}.price {{ font-size: 24px; font-weight: 700; color: #ffffff; }}.pct {{ font-size: 13px; font-weight: bold; padding: 2px 6px; border-radius: 4px; }}.up {{ color: #00ffaa; background: rgba(0, 255, 170, 0.1); }}.down {{ color: #ff3b3b; background: rgba(255, 59, 59, 0.1); }}.na {{ color: #888; background: rgba(136, 136, 136, 0.1); }}footer {{ margin-top: 80px; padding: 40px; text-align: center; font-size: 0.8rem; color: #8b949e; border-top: 1px solid var(--border); }}</style></head><body><div class="container"><header><h1>💎 CRYPTO GOLD TERMINAL</h1><div style="color:#888;">REAL-TIME BLOCKCHAIN FEED • AUTO-UPDATED</div><div style="font-size:0.8rem; color:#666; margin-top:5px;">Last Update: {update_time} | Success: {success_rate}%</div></header><h2 style="color:var(--accent); border-left:4px solid var(--accent); padding-left:10px;">GLOBAL CRYPTO MARKET (TOP 100)</h2><div class="grid">{content}</div><footer><div style="margin-bottom:20px;"><strong>⚠️ INVESTMENT DISCLAIMER</strong><br>Data provided is for informational purposes only. Not financial advice.</div><div>© 2025 CRYPTO-GOLD-DASHBOARD • GITHUB ACTIONS</div></footer></div></body></html>"""

DIV_TEMPLATE = """<!DOCTYPE html><html lang="ko"><head><meta charset="UTF-8">{cache_meta}<meta name="viewport" content="width=device-width, initial-scale=1.0"><title>PREMIUM DIVIDEND TERMINAL</title><style>:root {{ --bg: #05070a; --card-bg: #11141b; --border: #1e222d; --text: #d1d4dc; --accent: #00ffaa; }}body {{ background-color: var(--bg); color: var(--text); font-family: 'Trebuchet MS', sans-serif; margin: 0; padding: 20px; }}.container {{ max-width: 1200px; margin: 0 auto; }}header {{ border-bottom: 2px solid var(--accent); padding-bottom: 20px; margin-bottom: 40px; }}h1 {{ font-size: 38px; color: #ffffff; margin: 0; letter-spacing: -1px; }}.grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 12px; }}.card {{ background: var(--card-bg); border: 1px solid var(--border); padding: 15px; border-radius: 6px; transition: all 0.2s; }}.card:hover {{ background: #1c212d; border-color: var(--accent); }}.card-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }}.symbol {{ font-weight: bold; font-size: 16px; color: #fff; }}.price {{ font-size: 24px; font-weight: 700; color: #ffffff; }}.pct {{ font-size: 13px; font-weight: bold; padding: 2px 6px; border-radius: 4px; }}.up {{ color: #00ffaa; background: rgba(0, 255, 170, 0.1); }}.down {{ color: #ff3b3b; background: rgba(255, 59, 59, 0.1); }}.na {{ color: #888; background: rgba(136, 136, 136, 0.1); }}footer {{ margin-top: 80px; padding: 40px; text-align: center; font-size: 0.8rem; color: #8b949e; border-top: 1px solid var(--border); }}</style></head><body><div class="container"><header><h1>💰 DIVIDEND TERMINAL PRO</h1><div style="color:#888;">LIVE MARKET DATA • AUTO-UPDATED</div><div style="font-size:0.8rem; color:#666; margin-top:5px;">Last Update: {update_time} | Success: {success_rate}%</div></header><h2 style="color:var(--accent); border-left:4px solid var(--accent); padding-left:10px;">DIVIDEND KINGS (TOP 100)</h2><div class="grid">{content}</div><footer><div style="margin-bottom:20px;"><strong>⚠️ INVESTMENT DISCLAIMER</strong><br>Data provided is for informational purposes only. Not financial advice.</div><div>© 2025 CRYPTO-GOLD-DASHBOARD • GITHUB ACTIONS</div></footer></div></body></html>"""

INDEX_TEMPLATE = """<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">{cache_meta}<title>NASDAQ Real-Time Terminal</title><style>body {{ background: #0b0e14; color: #e2e8f0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; padding: 20px; margin: 0; }}.dashboard {{ max-width: 1200px; margin: 0 auto; background: #161b22; border: 1px solid #30363d; padding: 30px; border-radius: 12px; box-shadow: 0 8px 32px rgba(0,0,0,0.3); }}.grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }}.stat-card {{ background: #0d1117; padding: 20px; border-radius: 8px; border-top: 4px solid #00ff88; transition: transform 0.2s; }}.stat-card:hover {{ transform: translateY(-2px); }}.stat-title {{ color: #8b949e; font-size: 0.9rem; margin-bottom: 5px; text-transform: uppercase; letter-spacing: 0.5px; }}.price {{ font-size: 2rem; font-weight: bold; color: #ffffff; }}table {{ width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 0.95rem; }}th {{ background: #21262d; color: #8b949e; padding: 15px; text-align: left; border-bottom: 2px solid #30363d; text-transform: uppercase; font-size: 0.85rem; letter-spacing: 0.5px; }}td {{ padding: 12px 15px; border-bottom: 1px solid #30363d; }}tr:hover {{ background: #21262d; }}.up {{ color: #39d353; font-weight: bold; }}.down {{ color: #ff7b72; font-weight: bold; }}footer {{ margin-top: 60px; padding-top: 30px; border-top: 1px solid #30363d; color: #8b949e; font-size: 0.8rem; text-align: center; }}</style></head><body><div class="dashboard"><h1>🚀 NASDAQ-100 Live Intelligence</h1><div style="color:#8b949e; margin-bottom:20px; font-size:0.9rem;">Real-time market data • Last Update: {update_time} | Success: {success_rate}%</div><div class="grid"><div class="stat-card"><div class="stat-title">QQQ ETF Price</div><div class="price">{qqq_price}</div></div><div class="stat-card" style="border-top-color:#58a6ff;"><div class="stat-title">Market Sentiment</div><div class="price" style="font-size:1.5rem;">{sentiment}</div></div><div class="stat-card" style="border-top-color:#e3b341;"><div class="stat-title">VIX Index</div><div class="price">{vix_price}</div></div></div><h3 style="color:#fff; margin-top:40px;">Top Technology Constituents</h3><table><thead><tr><th>Ticker</th><th>Price ($)</th><th>Change (%)</th><th>Signal</th></tr></thead><tbody>{content}</tbody></table><footer><strong>⚠️ INVESTMENT DISCLAIMER</strong><br>Auto-updated data. Not financial advice.<br>© 2025 CRYPTO-GOLD-DASHBOARD • GITHUB ACTIONS</footer></div></body></html>"""

# =========================================================
# Core Functions
# =========================================================
def fetch_batch_data(tickers: List[str], period: str = "5d") -> pd.DataFrame:
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(f"[{attempt}/{MAX_RETRIES}] Fetching {len(tickers)} tickers...")
            data = yf.download(tickers, period=period, group_by='ticker', threads=True, progress=False, auto_adjust=True)
            if data is not None and not data.empty:
                return data
        except Exception as e:
            print(f"❌ Attempt {attempt} failed: {e}")
        if attempt < MAX_RETRIES:
            time.sleep(BASE_DELAY * attempt)
    return pd.DataFrame()

def extract_symbol_df(batch_data: pd.DataFrame, symbol: str) -> pd.DataFrame:
    if batch_data.empty: raise ValueError("Empty")
    if isinstance(batch_data.columns, pd.MultiIndex):
        if symbol in batch_data.columns.levels[0]: return batch_data[symbol]
        if symbol.upper() in batch_data.columns.levels[0]: return batch_data[symbol.upper()]
    elif 'Close' in batch_data.columns: return batch_data
    raise ValueError("Not Found")

def format_crypto_price(price: float) -> str:
    if price < 0.01: return f"${price:,.8f}"
    elif price < 1.0: return f"${price:,.6f}"
    else: return f"${price:,.2f}"

def generate_html_from_batch(tickers: List[str], batch_data: pd.DataFrame, mode: str = "card") -> Tuple[str, Dict]:
    html = ""
    success, fail = 0, 0
    for symbol in tickers:
        try:
            df = extract_symbol_df(batch_data, symbol).dropna(subset=['Close'])
            if len(df) < 2: raise ValueError("Short")
            price, prev = float(df['Close'].iloc[-1]), float(df['Close'].iloc[-2])
            change = ((price - prev) / prev) * 100.0
            cls, sign = ("up", "+") if change >= 0 else ("down", "")
            
            if mode == "card":
                p_str = format_crypto_price(price) if "-USD" in symbol else f"${price:,.2f}"
                html += f'<div class="card"><div class="card-header"><span class="symbol">{symbol.replace("-USD","")}</span><span class="pct {cls}">{sign}{change:.2f}%</span></div><div class="price">{p_str}</div></div>'
            elif mode == "table":
                sig = "BUY" if change > 0.5 else ("SELL" if change < -0.5 else "HOLD")
                sig_col = "#39d353" if sig=="BUY" else ("#ff7b72" if sig=="SELL" else "#888")
                html += f'<tr><td style="color:#fff;">{symbol}</td><td>${price:,.2f}</td><td class="{cls}">{sign}{change:.2f}%</td><td style="color:{sig_col};">{sig}</td></tr>'
            success += 1
        except:
            fail += 1
            if mode == "card": html += f'<div class="card" style="opacity:0.4;"><span class="symbol">{symbol}</span><div class="price">N/A</div></div>'
            else: html += f'<tr><td>{symbol}</td><td>-</td><td>-</td><td>N/A</td></tr>'
    return html, {"rate": (success/len(tickers)*100) if tickers else 0}

def main():
    start_t = time.time()
    now_str = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=9)).strftime("%Y-%m-%d %H:%M KST")
    
    # 1. Crypto
    c_batch = fetch_batch_data(COIN_TICKERS)
    c_html, c_stats = generate_html_from_batch(COIN_TICKERS, c_batch, "card")
    with open("coin.html", "w", encoding="utf-8") as f:
        f.write(COIN_TEMPLATE.format(cache_meta=CACHE_META, update_time=now_str, success_rate=f"{c_stats['rate']:.1f}", content=c_html))
    
    # 2. Dividend
    d_batch = fetch_batch_data(DIVIDEND_TICKERS)
    d_html, d_stats = generate_html_from_batch(DIVIDEND_TICKERS, d_batch, "card")
    with open("dividend.html", "w", encoding="utf-8") as f:
        f.write(DIV_TEMPLATE.format(cache_meta=CACHE_META, update_time=now_str, success_rate=f"{d_stats['rate']:.1f}", content=d_html))
        
    # 3. Nasdaq
    n_batch = fetch_batch_data(NASDAQ_TICKERS + ["QQQ", "^VIX"])
    n_html, n_stats = generate_html_from_batch(NASDAQ_TICKERS, n_batch, "table")
    try:
        qqq = f"${float(extract_symbol_df(n_batch,'QQQ')['Close'].iloc[-1]):,.2f}"
        vix = f"{float(extract_symbol_df(n_batch,'^VIX')['Close'].iloc[-1]):,.2f}"
    except: qqq, vix = "N/A", "N/A"
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(INDEX_TEMPLATE.format(cache_meta=CACHE_META, update_time=now_str, success_rate=f"{n_stats['rate']:.1f}", content=n_html, qqq_price=qqq, vix_price=vix, sentiment="NEUTRAL"))

    # Git Push
    try:
        subprocess.run(["git", "config", "user.name", "github-actions"], check=True)
        subprocess.run(["git", "config", "user.email", "github-actions@github.com"], check=True)
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", f"🚀 Update: {now_str}"], check=True)
        subprocess.run(["git", "push"], check=True)
    except: print("Git Push Skipped (No changes or error)")

if __name__ == "__main__":
    main()
