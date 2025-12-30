"""
🚀 GitHub Actions 최적화 버전
======================================
- Schedule 모듈 제거 (GitHub Actions cron 사용)
- 1회 실행 후 종료
- Git commit & push 자동화
- 경량화 (불필요한 Enterprise 기능 제거)
"""

import yfinance as yf
import pandas as pd
import datetime
import time
import random
import os
import json
import hashlib
import subprocess
from typing import Optional, List, Tuple, Dict
from pathlib import Path

# =========================================================
# Configuration
# =========================================================
OUTPUT_DIR = Path("./")  # GitHub Pages용 루트 디렉토리
LOGS_DIR = Path("./logs")
LOGS_DIR.mkdir(exist_ok=True)

MAX_RETRIES = 4
BASE_DELAY = 1.5

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
    '<meta http-equiv="Pragma" content="no-cache">'
    '<meta http-equiv="Expires" content="0">'
)

COIN_TEMPLATE = f"""<!DOCTYPE html><html lang="ko"><head><meta charset="UTF-8">{CACHE_META}<meta name="viewport" content="width=device-width, initial-scale=1.0"><title>PREMIUM CRYPTO TERMINAL</title><style>:root {{{{ --bg: #05070a; --card-bg: #11141b; --border: #1e222d; --text: #d1d4dc; --accent: #fbbf24; }}}}body {{{{ background-color: var(--bg); color: var(--text); font-family: 'Trebuchet MS', sans-serif; margin: 0; padding: 20px; }}}}.container {{{{ max-width: 1200px; margin: 0 auto; }}}}header {{{{ border-bottom: 2px solid var(--accent); padding-bottom: 20px; margin-bottom: 40px; }}}}h1 {{{{ font-size: 38px; color: #ffffff; margin: 0; letter-spacing: -1px; }}}}.grid {{{{ display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 12px; }}}}.card {{{{ background: var(--card-bg); border: 1px solid var(--border); padding: 15px; border-radius: 6px; transition: all 0.2s; }}}}.card:hover {{{{ background: #1c212d; border-color: var(--accent); }}}}.card-header {{{{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }}}}.symbol {{{{ font-weight: bold; font-size: 16px; color: #fff; }}}}.price {{{{ font-size: 24px; font-weight: 700; color: #ffffff; }}}}.pct {{{{ font-size: 13px; font-weight: bold; padding: 2px 6px; border-radius: 4px; }}}}.up {{{{ color: #00ffaa; background: rgba(0, 255, 170, 0.1); }}}}.down {{{{ color: #ff3b3b; background: rgba(255, 59, 59, 0.1); }}}}.na {{{{ color: #888; background: rgba(136, 136, 136, 0.1); }}}}footer {{{{ margin-top: 80px; padding: 40px; text-align: center; font-size: 0.8rem; color: #8b949e; border-top: 1px solid var(--border); }}}}</style></head><body><div class="container"><header><h1>💎 CRYPTO GOLD TERMINAL</h1><div style="color:#888;">REAL-TIME BLOCKCHAIN FEED • AUTO-UPDATED</div><div style="font-size:0.8rem; color:#666; margin-top:5px;">Last Update: {update_time} | Success: {success_rate}%</div></header><h2 style="color:var(--accent); border-left:4px solid var(--accent); padding-left:10px;">GLOBAL CRYPTO MARKET (TOP 100)</h2><div class="grid">{content}</div><footer><div style="margin-bottom:20px;"><strong>⚠️ INVESTMENT DISCLAIMER</strong><br>Data provided is for informational purposes only. Not financial advice.</div><div>© 2025 CRYPTO-GOLD-DASHBOARD • AUTO-UPDATED VIA GITHUB ACTIONS</div></footer></div></body></html>"""

DIV_TEMPLATE = f"""<!DOCTYPE html><html lang="ko"><head><meta charset="UTF-8">{CACHE_META}<meta name="viewport" content="width=device-width, initial-scale=1.0"><title>PREMIUM DIVIDEND TERMINAL</title><style>:root {{{{ --bg: #05070a; --card-bg: #11141b; --border: #1e222d; --text: #d1d4dc; --accent: #00ffaa; }}}}body {{{{ background-color: var(--bg); color: var(--text); font-family: 'Trebuchet MS', sans-serif; margin: 0; padding: 20px; }}}}.container {{{{ max-width: 1200px; margin: 0 auto; }}}}header {{{{ border-bottom: 2px solid var(--accent); padding-bottom: 20px; margin-bottom: 40px; }}}}h1 {{{{ font-size: 38px; color: #ffffff; margin: 0; letter-spacing: -1px; }}}}.grid {{{{ display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 12px; }}}}.card {{{{ background: var(--card-bg); border: 1px solid var(--border); padding: 15px; border-radius: 6px; transition: all 0.2s; }}}}.card:hover {{{{ background: #1c212d; border-color: var(--accent); }}}}.card-header {{{{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }}}}.symbol {{{{ font-weight: bold; font-size: 16px; color: #fff; }}}}.price {{{{ font-size: 24px; font-weight: 700; color: #ffffff; }}}}.pct {{{{ font-size: 13px; font-weight: bold; padding: 2px 6px; border-radius: 4px; }}}}.up {{{{ color: #00ffaa; background: rgba(0, 255, 170, 0.1); }}}}.down {{{{ color: #ff3b3b; background: rgba(255, 59, 59, 0.1); }}}}.na {{{{ color: #888; background: rgba(136, 136, 136, 0.1); }}}}footer {{{{ margin-top: 80px; padding: 40px; text-align: center; font-size: 0.8rem; color: #8b949e; border-top: 1px solid var(--border); }}}}</style></head><body><div class="container"><header><h1>💰 DIVIDEND TERMINAL PRO</h1><div style="color:#888;">LIVE MARKET DATA • AUTO-UPDATED</div><div style="font-size:0.8rem; color:#666; margin-top:5px;">Last Update: {update_time} | Success: {success_rate}%</div></header><h2 style="color:var(--accent); border-left:4px solid var(--accent); padding-left:10px;">DIVIDEND KINGS (TOP 100)</h2><div class="grid">{content}</div><footer><div style="margin-bottom:20px;"><strong>⚠️ INVESTMENT DISCLAIMER</strong><br>Data provided is for informational purposes only. Not financial advice.</div><div>© 2025 CRYPTO-GOLD-DASHBOARD • AUTO-UPDATED VIA GITHUB ACTIONS</div></footer></div></body></html>"""

INDEX_TEMPLATE = f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">{CACHE_META}<title>NASDAQ Real-Time Terminal</title><style>body {{{{ background: #0b0e14; color: #e2e8f0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; padding: 20px; margin: 0; }}}}.dashboard {{{{ max-width: 1200px; margin: 0 auto; background: #161b22; border: 1px solid #30363d; padding: 30px; border-radius: 12px; box-shadow: 0 8px 32px rgba(0,0,0,0.3); }}}}.grid {{{{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }}}}.stat-card {{{{ background: #0d1117; padding: 20px; border-radius: 8px; border-top: 4px solid #00ff88; transition: transform 0.2s; }}}}.stat-card:hover {{{{ transform: translateY(-2px); }}}}.stat-title {{{{ color: #8b949e; font-size: 0.9rem; margin-bottom: 5px; text-transform: uppercase; letter-spacing: 0.5px; }}}}.price {{{{ font-size: 2rem; font-weight: bold; color: #ffffff; }}}}table {{{{ width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 0.95rem; }}}}th {{{{ background: #21262d; color: #8b949e; padding: 15px; text-align: left; border-bottom: 2px solid #30363d; text-transform: uppercase; font-size: 0.85rem; letter-spacing: 0.5px; }}}}td {{{{ padding: 12px 15px; border-bottom: 1px solid #30363d; }}}}tr:hover {{{{ background: #21262d; }}}}.up {{{{ color: #39d353; font-weight: bold; }}}}.down {{{{ color: #ff7b72; font-weight: bold; }}}}footer {{{{ margin-top: 60px; padding-top: 30px; border-top: 1px solid #30363d; color: #8b949e; font-size: 0.8rem; text-align: center; }}}}</style></head><body><div class="dashboard"><h1>🚀 NASDAQ-100 Live Intelligence</h1><div style="color:#8b949e; margin-bottom:20px; font-size:0.9rem;">Real-time market data • Last Update: {update_time} | Success: {success_rate}%</div><div class="grid"><div class="stat-card"><div class="stat-title">QQQ ETF Price</div><div class="price">{qqq_price}</div></div><div class="stat-card" style="border-top-color:#58a6ff;"><div class="stat-title">Market Sentiment</div><div class="price" style="font-size:1.5rem;">{sentiment}</div></div><div class="stat-card" style="border-top-color:#e3b341;"><div class="stat-title">VIX Index</div><div class="price">{vix_price}</div></div></div><h3 style="color:#fff; margin-top:40px;">Top Technology Constituents</h3><table><thead><tr><th>Ticker</th><th>Price ($)</th><th>Change (%)</th><th>Signal</th></tr></thead><tbody>{content}</tbody></table><footer><strong>⚠️ INVESTMENT DISCLAIMER</strong><br>Auto-updated data. Not financial advice.<br>© 2025 CRYPTO-GOLD-DASHBOARD • GITHUB ACTIONS</footer></div></body></html>"""

# =========================================================
# Core Functions
# =========================================================
def fetch_batch_data(tickers: List[str], period: str = "5d") -> pd.DataFrame:
    """yfinance로 배치 데이터 가져오기 (재시도 포함)"""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(f"[{attempt}/{MAX_RETRIES}] Fetching {len(tickers)} tickers...")
            
            data = yf.download(
                tickers,
                period=period,
                group_by='ticker',
                threads=True,
                progress=False,
                auto_adjust=True
            )
            
            if data is not None and not data.empty:
                print(f"✓ Successfully fetched {len(tickers)} tickers")
                return data
            
            print("⚠️ Empty data returned")
            
        except Exception as e:
            print(f"❌ Attempt {attempt} failed: {e}")
        
        if attempt < MAX_RETRIES:
            sleep_s = (BASE_DELAY * (2 ** (attempt - 1))) + random.uniform(0, 0.7)
            print(f"⏳ Retrying in {sleep_s:.1f}s...")
            time.sleep(sleep_s)
    
    print("❌ All attempts failed")
    return pd.DataFrame()

def extract_symbol_df(batch_data: pd.DataFrame, symbol: str) -> pd.DataFrame:
    """배치 데이터에서 심볼 추출"""
    if batch_data is None or batch_data.empty:
        raise ValueError(f"Empty batch for {symbol}")
    
    cols = batch_data.columns
    
    if isinstance(cols, pd.MultiIndex):
        tickers_set = set(cols.get_level_values(0))
        symbol_upper = symbol.upper()
        
        for ticker in tickers_set:
            if str(ticker).upper() == symbol_upper:
                return batch_data[ticker]
        
        raise ValueError(f"{symbol} not in batch")
    
    if isinstance(cols, pd.Index) and 'Close' in cols:
        return batch_data
    
    raise ValueError(f"Unsupported structure for {symbol}")

def format_crypto_price(price: float) -> str:
    """암호화폐 가격 포맷팅"""
    if price < 0.01:
        return f"${price:,.8f}"
    elif price < 1.0:
        return f"${price:,.6f}"
    elif price < 10.0:
        return f"${price:,.4f}"
    else:
        return f"${price:,.2f}"

def calculate_sentiment(batch_data: pd.DataFrame, tickers: List[str]) -> str:
    """시장 심리 계산"""
    try:
        positive = 0
        total = 0
        sample = random.sample(tickers, min(40, len(tickers)))
        
        for symbol in sample:
            try:
                df = extract_symbol_df(batch_data, symbol)
                if 'Close' in df.columns and len(df) >= 2:
                    df = df.dropna(subset=['Close'])
                    if len(df) >= 2:
                        prev = float(df['Close'].iloc[-2])
                        curr = float(df['Close'].iloc[-1])
                        if prev > 0:
                            total += 1
                            if curr > prev:
                                positive += 1
            except:
                continue
        
        if total >= 10:
            ratio = positive / total
            if ratio >= 0.7:
                return "GREED 🔥"
            elif ratio >= 0.5:
                return "NEUTRAL 😐"
            else:
                return "FEAR 🥶"
    except:
        pass
    
    return "NEUTRAL 😐"

def generate_html_from_batch(tickers: List[str], batch_data: pd.DataFrame, mode: str = "card") -> Tuple[str, Dict]:
    """HTML 생성"""
    html = ""
    success = 0
    fail = 0
    
    for symbol in tickers:
        name = symbol.replace("-USD", "")
        
        try:
            df = extract_symbol_df(batch_data, symbol)
            
            if 'Close' not in df.columns:
                raise ValueError("No Close")
            
            df = df.dropna(subset=['Close'])
            if len(df) < 2:
                raise ValueError("Insufficient data")
            
            price = float(df['Close'].iloc[-1])
            prev = float(df['Close'].iloc[-2])
            
            if prev == 0:
                raise ValueError("Prev price zero")
            
            change = ((price - prev) / prev) * 100.0
            cls = "up" if change >= 0 else "down"
            sign = "+" if change >= 0 else ""
            
            if mode == "card":
                display_price = format_crypto_price(price) if "-USD" in symbol else f"${price:,.2f}"
                html += f"""
                <div class="card">
                    <div class="card-header">
                        <span class="symbol">{name}</span>
                        <span class="pct {cls}">{sign}{change:.2f}%</span>
                    </div>
                    <div class="price">{display_price}</div>
                </div>"""
            
            elif mode == "table":
                signal = "HOLD"
                if change > 3:
                    signal = "STRONG BUY"
                elif change > 0.5:
                    signal = "BUY"
                elif change < -2:
                    signal = "STRONG SELL"
                elif change < -0.5:
                    signal = "SELL"
                
                colors = {
                    "STRONG BUY": "#00ff88",
                    "BUY": "#39d353",
                    "SELL": "#ff7b72",
                    "STRONG SELL": "#ff3b3b",
                    "HOLD": "#8b949e"
                }
                
                html += f"""
                <tr>
                    <td style="color:#fff; font-weight:bold;">{symbol}</td>
                    <td style="color:#fff;">${price:,.2f}</td>
                    <td class="{cls}">{sign}{change:.2f}%</td>
                    <td style="color:{colors[signal]}; font-weight:bold;">{signal}</td>
                </tr>"""
            
            success += 1
        
        except:
            fail += 1
            
            if mode == "card":
                html += f"""
                <div class="card" style="opacity:0.5; border-color:#333;">
                    <div class="card-header">
                        <span class="symbol" style="color:#666;">{name}</span>
                        <span class="pct na">N/A</span>
                    </div>
                    <div class="price" style="color:#666; font-size:1.2rem;">No Data</div>
                </div>"""
            elif mode == "table":
                html += f"""
                <tr style="opacity:0.4;">
                    <td style="color:#666;">{symbol}</td>
                    <td style="color:#444;">$0.00</td>
                    <td style="color:#444;">0.00%</td>
                    <td style="color:#444;">NO DATA</td>
                </tr>"""
    
    total = len(tickers)
    success_rate = (success / total * 100) if total > 0 else 0
    
    print(f"[{mode.upper()}] ✓ {success} | ✗ {fail} ({success_rate:.1f}%)")
    
    return html, {"success": success, "fail": fail, "total": total, "rate": success_rate}

def get_price_from_batch(batch_data: pd.DataFrame, symbol: str) -> str:
    """단일 가격 추출"""
    try:
        df = extract_symbol_df(batch_data, symbol)
        df = df.dropna(subset=['Close'])
        if len(df) > 0:
            return f"${float(df['Close'].iloc[-1]):,.2f}"
    except:
        pass
    return "$0.00"

def git_commit_and_push():
    """Git commit & push"""
    try:
        subprocess.run(["git", "config", "user.name", "github-actions"], check=True)
        subprocess.run(["git", "config", "user.email", "github-actions@github.com"], check=True)
        subprocess.run(["git", "add", "coin.html", "dividend.html", "index.html", "status.json"], check=True)
        subprocess.run(["git", "commit", "-m", "🤖 Auto-update market data"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("✓ Git push successful")
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Git operation failed: {e}")
    except Exception as e:
        print(f"⚠️ Unexpected git error: {e}")

# =========================================================
# Main
# =========================================================
def main():
    start_time = time.time()
    
    kst_now = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=9)
    update_time_str = kst_now.strftime("%Y-%m-%d %H:%M KST")
    
    print("=" * 60)
    print(f"🚀 GitHub Actions Update Start ({update_time_str})")
    print("=" * 60)
    
    # 1) Crypto
    print("\n>>> Crypto Markets")
    coin_batch = fetch_batch_data(COIN_TICKERS, period="5d")
    coin_html, coin_stats = generate_html_from_batch(COIN_TICKERS, coin_batch, mode="card")
    
    coin_final = COIN_TEMPLATE.format(
        update_time=update_time_str,
        content=coin_html,
        success_rate=f"{coin_stats['rate']:.1f}"
    )
    
    with open(OUTPUT_DIR / "coin.html", "w", encoding="utf-8") as f:
        f.write(coin_final)
    print("✓ coin.html created")
    
    # 2) Dividend
    print("\n>>> Dividend Stocks")
    div_batch = fetch_batch_data(DIVIDEND_TICKERS, period="5d")
    div_html, div_stats = generate_html_from_batch(DIVIDEND_TICKERS, div_batch, mode="card")
    
    div_final = DIV_TEMPLATE.format(
        update_time=update_time_str,
        content=div_html,
        success_rate=f"{div_stats['rate']:.1f}"
    )
    
    with open(OUTPUT_DIR / "dividend.html", "w", encoding="utf-8") as f:
        f.write(div_final)
    print("✓ dividend.html created")
    
    # 3) Nasdaq
    print("\n>>> NASDAQ-100")
    all_nasdaq = NASDAQ_TICKERS + ["QQQ", "^VIX"]
    nasdaq_batch = fetch_batch_data(all_nasdaq, period="5d")
    
    nasdaq_html, nasdaq_stats = generate_html_from_batch(NASDAQ_TICKERS, nasdaq_batch, mode="table")
    
    qqq_price = get_price_from_batch(nasdaq_batch, "QQQ")
    vix_price = get_price_from_batch(nasdaq_batch, "^VIX")
    sentiment = calculate_sentiment(nasdaq_batch, NASDAQ_TICKERS)
    
    index_final = INDEX_TEMPLATE.format(
        update_time=update_time_str,
        content=nasdaq_html,
        qqq_price=qqq_price,
        vix_price=vix_price,
        sentiment=sentiment,
        success_rate=f"{nasdaq_stats['rate']:.1f}"
    )
    
    with open(OUTPUT_DIR / "index.html", "w", encoding="utf-8") as f:
        f.write(index_final)
    print("✓ index.html created")
    
    # 4) Status JSON
    overall_success = coin_stats['success'] + div_stats['success'] + nasdaq_stats['success']
    overall_total = coin_stats['total'] + div_stats['total'] + nasdaq_stats['total']
    overall_rate = (overall_success / overall_total * 100) if overall_total > 0 else 0
    
    duration = time.time() - start_time
    
    status = {
        "update_time": update_time_str,
        "duration_seconds": round(duration, 2),
        "stats": {
            "crypto": coin_stats,
            "dividend": div_stats,
            "nasdaq": nasdaq_stats
        },
        "overall_success_rate": round(overall_rate, 2)
    }
    
    with open(OUTPUT_DIR / "status.json", "w", encoding="utf-8") as f:
        json.dump(status, f, indent=2)
    print("✓ status.json created")
    
    # 5) Git Commit & Push
    print("\n>>> Git Push")
    git_commit_and_push()
    
    print("\n" + "=" * 60)
    print(f"🏁 Complete! Overall Success: {overall_rate:.1f}% ({duration:.1f}s)")
    print("=" * 60)

if __name__ == "__main__":
    main()
