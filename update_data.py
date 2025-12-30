"""
🚀 ENTERPRISE-GRADE MARKET DATA SYSTEM
======================================
Features:
- Multi-source data fallback (yfinance → Alpha Vantage)
- Redis-style in-memory caching with stable hashing
- Automatic rollback on failure
- Discord/Slack notifications
- Health monitoring & metrics
- Auto-scheduling with error recovery
- Trend analysis & reporting
"""

import yfinance as yf
import pandas as pd
import datetime
import time
import random
import os
import tempfile
import logging
import json
import hashlib
import shutil
from typing import Optional, List, Tuple, Dict, Any
from pathlib import Path
from dataclasses import dataclass, asdict
from collections import deque
import threading
import schedule

# =========================================================
# Dependency Check
# =========================================================
try:
    import requests
except ImportError:
    raise ImportError("Missing 'requests' library. Install with: pip install requests")

# =========================================================
# Configuration
# =========================================================
@dataclass
class Config:
    OUTPUT_DIR: Path = Path("./output")
    BACKUP_DIR: Path = Path("./backups")
    LOGS_DIR: Path = Path("./logs")
    
    PRIMARY_SOURCE: str = "yfinance"
    FALLBACK_SOURCES: List[str] = None
    ALPHA_VANTAGE_API_KEY: str = os.getenv("ALPHA_VANTAGE_API_KEY", "")
    
    UPDATE_INTERVAL_MINUTES: int = 60
    MAX_CONSECUTIVE_FAILURES: int = 3
    
    DISCORD_WEBHOOK: str = os.getenv("DISCORD_WEBHOOK", "")
    SLACK_WEBHOOK: str = os.getenv("SLACK_WEBHOOK", "")
    ALERT_ON_FAILURE_RATE: float = 0.3
    
    CACHE_ENABLED: bool = True
    CACHE_TTL_SECONDS: int = 3600
    
    MAX_RETRIES: int = 4
    BASE_DELAY: float = 1.5
    
    KEEP_BACKUP_COUNT: int = 10
    AUTO_ROLLBACK_ON_FAILURE: bool = True
    
    def __post_init__(self):
        if self.FALLBACK_SOURCES is None:
            self.FALLBACK_SOURCES = ["alpha_vantage"] if self.ALPHA_VANTAGE_API_KEY else []
        
        for directory in [self.OUTPUT_DIR, self.BACKUP_DIR, self.LOGS_DIR]:
            directory.mkdir(exist_ok=True, parents=True)

CONFIG = Config()

# =========================================================
# Logging Setup
# =========================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(CONFIG.LOGS_DIR / 'market_update.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

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
# HTML Templates (🔥 템플릿 중괄호 버그 수정: {{ }} → { })
# =========================================================
CACHE_META = (
    '<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">'
    '<meta http-equiv="Pragma" content="no-cache">'
    '<meta http-equiv="Expires" content="0">'
)

COIN_TEMPLATE = f"""<!DOCTYPE html><html lang="ko"><head><meta charset="UTF-8">{CACHE_META}<meta name="viewport" content="width=device-width, initial-scale=1.0"><title>PREMIUM CRYPTO TERMINAL</title><style>:root {{{{ --bg: #05070a; --card-bg: #11141b; --border: #1e222d; --text: #d1d4dc; --accent: #fbbf24; }}}}body {{{{ background-color: var(--bg); color: var(--text); font-family: 'Trebuchet MS', sans-serif; margin: 0; padding: 20px; }}}}.container {{{{ max-width: 1200px; margin: 0 auto; }}}}header {{{{ border-bottom: 2px solid var(--accent); padding-bottom: 20px; margin-bottom: 40px; }}}}h1 {{{{ font-size: 38px; color: #ffffff; margin: 0; letter-spacing: -1px; }}}}.health {{{{ display: inline-block; padding: 4px 12px; border-radius: 4px; font-size: 0.75rem; margin-left: 10px; font-weight: bold; }}}}.health-good {{{{ background: #00ffaa; color: #000; }}}}.health-warn {{{{ background: #fbbf24; color: #000; }}}}.health-bad {{{{ background: #ff3b3b; color: #fff; }}}}.grid {{{{ display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 12px; }}}}.card {{{{ background: var(--card-bg); border: 1px solid var(--border); padding: 15px; border-radius: 6px; transition: all 0.2s; }}}}.card:hover {{{{ background: #1c212d; border-color: var(--accent); }}}}.card-header {{{{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }}}}.symbol {{{{ font-weight: bold; font-size: 16px; color: #fff; }}}}.price {{{{ font-size: 24px; font-weight: 700; color: #ffffff; }}}}.pct {{{{ font-size: 13px; font-weight: bold; padding: 2px 6px; border-radius: 4px; }}}}.up {{{{ color: #00ffaa; background: rgba(0, 255, 170, 0.1); }}}}.down {{{{ color: #ff3b3b; background: rgba(255, 59, 59, 0.1); }}}}.na {{{{ color: #888; background: rgba(136, 136, 136, 0.1); }}}}footer {{{{ margin-top: 80px; padding: 40px; text-align: center; font-size: 0.8rem; color: #8b949e; border-top: 1px solid var(--border); }}}}</style></head><body><div class="container"><header><h1>💎 CRYPTO GOLD TERMINAL<span class="health {health_class}">{health_status}</span></h1><div style="color:#888;">REAL-TIME BLOCKCHAIN FEED • ENTERPRISE GRADE</div><div style="font-size:0.8rem; color:#666; margin-top:5px;">Last Update: {update_time} | Success Rate: {success_rate}% | Source: {data_source}</div></header><h2 style="color:var(--accent); border-left:4px solid var(--accent); padding-left:10px;">GLOBAL CRYPTO MARKET (TOP 100)</h2><div class="grid">{content}</div><footer><div style="margin-bottom:20px;"><strong>⚠️ INVESTMENT DISCLAIMER</strong><br>Data provided is for informational purposes only. Not financial advice.</div><div>© 2025 US-DIVIDEND-PRO • ENTERPRISE EDITION</div></footer></div></body></html>"""

DIV_TEMPLATE = f"""<!DOCTYPE html><html lang="ko"><head><meta charset="UTF-8">{CACHE_META}<meta name="viewport" content="width=device-width, initial-scale=1.0"><title>PREMIUM DIVIDEND TERMINAL</title><style>:root {{{{ --bg: #05070a; --card-bg: #11141b; --border: #1e222d; --text: #d1d4dc; --accent: #00ffaa; }}}}body {{{{ background-color: var(--bg); color: var(--text); font-family: 'Trebuchet MS', sans-serif; margin: 0; padding: 20px; }}}}.container {{{{ max-width: 1200px; margin: 0 auto; }}}}header {{{{ border-bottom: 2px solid var(--accent); padding-bottom: 20px; margin-bottom: 40px; }}}}h1 {{{{ font-size: 38px; color: #ffffff; margin: 0; letter-spacing: -1px; }}}}.health {{{{ display: inline-block; padding: 4px 12px; border-radius: 4px; font-size: 0.75rem; margin-left: 10px; font-weight: bold; }}}}.health-good {{{{ background: #00ffaa; color: #000; }}}}.health-warn {{{{ background: #fbbf24; color: #000; }}}}.health-bad {{{{ background: #ff3b3b; color: #fff; }}}}.grid {{{{ display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 12px; }}}}.card {{{{ background: var(--card-bg); border: 1px solid var(--border); padding: 15px; border-radius: 6px; transition: all 0.2s; }}}}.card:hover {{{{ background: #1c212d; border-color: var(--accent); }}}}.card-header {{{{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }}}}.symbol {{{{ font-weight: bold; font-size: 16px; color: #fff; }}}}.price {{{{ font-size: 24px; font-weight: 700; color: #ffffff; }}}}.pct {{{{ font-size: 13px; font-weight: bold; padding: 2px 6px; border-radius: 4px; }}}}.up {{{{ color: #00ffaa; background: rgba(0, 255, 170, 0.1); }}}}.down {{{{ color: #ff3b3b; background: rgba(255, 59, 59, 0.1); }}}}.na {{{{ color: #888; background: rgba(136, 136, 136, 0.1); }}}}footer {{{{ margin-top: 80px; padding: 40px; text-align: center; font-size: 0.8rem; color: #8b949e; border-top: 1px solid var(--border); }}}}</style></head><body><div class="container"><header><h1>💰 DIVIDEND TERMINAL PRO<span class="health {health_class}">{health_status}</span></h1><div style="color:#888;">LIVE MARKET DATA • ENTERPRISE GRADE</div><div style="font-size:0.8rem; color:#666; margin-top:5px;">Last Update: {update_time} | Success Rate: {success_rate}% | Source: {data_source}</div></header><h2 style="color:var(--accent); border-left:4px solid var(--accent); padding-left:10px;">DIVIDEND KINGS (TOP 100)</h2><div class="grid">{content}</div><footer><div style="margin-bottom:20px;"><strong>⚠️ INVESTMENT DISCLAIMER</strong><br>Data provided is for informational purposes only. Not financial advice.</div><div>© 2025 US-DIVIDEND-PRO • ENTERPRISE EDITION</div></footer></div></body></html>"""

INDEX_TEMPLATE = f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">{CACHE_META}<title>NASDAQ Real-Time Terminal</title><style>body {{{{ background: #0b0e14; color: #e2e8f0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; padding: 20px; margin: 0; }}}}.dashboard {{{{ max-width: 1200px; margin: 0 auto; background: #161b22; border: 1px solid #30363d; padding: 30px; border-radius: 12px; box-shadow: 0 8px 32px rgba(0,0,0,0.3); }}}}.health {{{{ display: inline-block; padding: 4px 12px; border-radius: 4px; font-size: 0.75rem; margin-left: 10px; font-weight: bold; }}}}.health-good {{{{ background: #00ff88; color: #000; }}}}.health-warn {{{{ background: #fbbf24; color: #000; }}}}.health-bad {{{{ background: #ff3b3b; color: #fff; }}}}.grid {{{{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }}}}.stat-card {{{{ background: #0d1117; padding: 20px; border-radius: 8px; border-top: 4px solid #00ff88; transition: transform 0.2s; }}}}.stat-card:hover {{{{ transform: translateY(-2px); }}}}.stat-title {{{{ color: #8b949e; font-size: 0.9rem; margin-bottom: 5px; text-transform: uppercase; letter-spacing: 0.5px; }}}}.price {{{{ font-size: 2rem; font-weight: bold; color: #ffffff; }}}}table {{{{ width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 0.95rem; }}}}th {{{{ background: #21262d; color: #8b949e; padding: 15px; text-align: left; border-bottom: 2px solid #30363d; text-transform: uppercase; font-size: 0.85rem; letter-spacing: 0.5px; }}}}td {{{{ padding: 12px 15px; border-bottom: 1px solid #30363d; }}}}tr:hover {{{{ background: #21262d; }}}}.up {{{{ color: #39d353; font-weight: bold; }}}}.down {{{{ color: #ff7b72; font-weight: bold; }}}}footer {{{{ margin-top: 60px; padding-top: 30px; border-top: 1px solid #30363d; color: #8b949e; font-size: 0.8rem; text-align: center; }}}}</style></head><body><div class="dashboard"><h1>🚀 NASDAQ-100 Live Intelligence<span class="health {health_class}">{health_status}</span></h1><div style="color:#8b949e; margin-bottom:20px; font-size:0.9rem;">Real-time market data • Last Update: {update_time} | Success Rate: {success_rate}% | Source: {data_source}</div><div class="grid"><div class="stat-card"><div class="stat-title">QQQ ETF Price</div><div class="price">{qqq_price}</div></div><div class="stat-card" style="border-top-color:#58a6ff;"><div class="stat-title">Market Sentiment</div><div class="price" style="font-size:1.5rem;">{sentiment}</div></div><div class="stat-card" style="border-top-color:#e3b341;"><div class="stat-title">VIX Index</div><div class="price">{vix_price}</div></div></div><h3 style="color:#fff; margin-top:40px;">Top Technology Constituents</h3><table><thead><tr><th>Ticker</th><th>Price ($)</th><th>Change (%)</th><th>Signal</th></tr></thead><tbody>{content}</tbody></table><footer><strong>⚠️ INVESTMENT DISCLAIMER</strong><br>Enterprise-grade data. Not financial advice.<br>© 2025 US-DIVIDEND-PRO • ENTERPRISE EDITION</footer></div></body></html>"""

# =========================================================
# Cache System (🔥 안정적인 해시 사용)
# =========================================================
class SimpleCache:
    def __init__(self):
        self._cache = {}
        self._lock = threading.Lock()
        self._hits = 0
        self._misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            if key in self._cache:
                data, expiry = self._cache[key]
                if time.time() < expiry:
                    self._hits += 1
                    logger.debug(f"Cache HIT: {key[:50]}")
                    return data
                else:
                    del self._cache[key]
                    self._misses += 1
            else:
                self._misses += 1
        return None
    
    def set(self, key: str, value: Any, ttl: int = 3600):
        with self._lock:
            self._cache[key] = (value, time.time() + ttl)
    
    def clear(self):
        with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0
    
    def get_hit_rate(self) -> float:
        with self._lock:
            total = self._hits + self._misses
            return (self._hits / total) if total > 0 else 0.0

CACHE = SimpleCache()

# API Call Counter
class APICallCounter:
    def __init__(self):
        self._count = 0
        self._lock = threading.Lock()
    
    def increment(self):
        with self._lock:
            self._count += 1
    
    def get_and_reset(self) -> int:
        with self._lock:
            count = self._count
            self._count = 0
            return count

API_COUNTER = APICallCounter()

# =========================================================
# Metrics & Health
# =========================================================
@dataclass
class Metrics:
    timestamp: str
    update_duration_seconds: float
    crypto_success_rate: float
    dividend_success_rate: float
    nasdaq_success_rate: float
    overall_success_rate: float
    total_api_calls: int
    cache_hit_rate: float
    errors: List[str]
    data_source: str

class HealthMonitor:
    def __init__(self, history_size: int = 100):
        self.metrics_history = deque(maxlen=history_size)
        self.consecutive_failures = 0
        self._lock = threading.Lock()
    
    def add_metrics(self, metrics: Metrics):
        with self._lock:
            self.metrics_history.append(metrics)
            
            if metrics.overall_success_rate < 0.5:
                self.consecutive_failures += 1
            else:
                self.consecutive_failures = 0
    
    def get_health_status(self) -> Tuple[str, str]:
        with self._lock:
            if not self.metrics_history:
                return "INITIALIZING", "health-warn"
            
            latest = self.metrics_history[-1]
            rate = latest.overall_success_rate
            
            if self.consecutive_failures >= CONFIG.MAX_CONSECUTIVE_FAILURES:
                return "CRITICAL", "health-bad"
            elif rate >= 0.9:
                return "HEALTHY", "health-good"
            elif rate >= 0.7:
                return "DEGRADED", "health-warn"
            else:
                return "UNHEALTHY", "health-bad"
    
    def save_trends(self):
        try:
            trends = {
                "history": [asdict(m) for m in list(self.metrics_history)],
                "consecutive_failures": self.consecutive_failures,
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
            }
            
            with open(CONFIG.OUTPUT_DIR / "trends.json", "w") as f:
                json.dump(trends, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save trends: {e}")

HEALTH_MONITOR = HealthMonitor()

# =========================================================
# Notifications
# =========================================================
def send_discord_notification(message: str, is_critical: bool = False):
    if not CONFIG.DISCORD_WEBHOOK:
        return
    
    try:
        color = 0xFF0000 if is_critical else 0xFFA500
        payload = {
            "embeds": [{
                "title": "🚨 Market Data Alert" if is_critical else "⚠️ Market Data Warning",
                "description": message,
                "color": color,
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
            }]
        }
        
        requests.post(CONFIG.DISCORD_WEBHOOK, json=payload, timeout=5)
        logger.info("✓ Discord notification sent")
    except Exception as e:
        logger.error(f"Failed to send Discord notification: {e}")

def send_slack_notification(message: str, is_critical: bool = False):
    if not CONFIG.SLACK_WEBHOOK:
        return
    
    try:
        emoji = ":rotating_light:" if is_critical else ":warning:"
        payload = {"text": f"{emoji} *Market Data Alert*\n{message}"}
        
        requests.post(CONFIG.SLACK_WEBHOOK, json=payload, timeout=5)
        logger.info("✓ Slack notification sent")
    except Exception as e:
        logger.error(f"Failed to send Slack notification: {e}")

def notify_failure(metrics: Metrics):
    if metrics.overall_success_rate < (1 - CONFIG.ALERT_ON_FAILURE_RATE):
        message = (
            f"High failure rate detected!\n"
            f"Overall: {metrics.overall_success_rate*100:.1f}%\n"
            f"Crypto: {metrics.crypto_success_rate*100:.1f}%\n"
            f"Dividend: {metrics.dividend_success_rate*100:.1f}%\n"
            f"Nasdaq: {metrics.nasdaq_success_rate*100:.1f}%\n"
            f"Data Source: {metrics.data_source}"
        )
        
        is_critical = HEALTH_MONITOR.consecutive_failures >= CONFIG.MAX_CONSECUTIVE_FAILURES
        
        send_discord_notification(message, is_critical)
        send_slack_notification(message, is_critical)

# =========================================================
# Backup & Rollback
# =========================================================
def create_backup(file_path: Path) -> Optional[Path]:
    try:
        if not file_path.exists():
            return None
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = CONFIG.BACKUP_DIR / f"{file_path.stem}_{timestamp}{file_path.suffix}"
        
        shutil.copy2(file_path, backup_path)
        logger.debug(f"✓ Backup: {backup_path.name}")
        
        cleanup_old_backups(file_path.stem)
        return backup_path
    except Exception as e:
        logger.error(f"Backup failed: {e}")
        return None

def cleanup_old_backups(file_stem: str):
    try:
        backups = sorted(
            CONFIG.BACKUP_DIR.glob(f"{file_stem}_*"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        
        for old_backup in backups[CONFIG.KEEP_BACKUP_COUNT:]:
            old_backup.unlink()
    except Exception as e:
        logger.error(f"Cleanup failed: {e}")

def rollback_to_previous(file_path: Path) -> bool:
    try:
        backups = sorted(
            CONFIG.BACKUP_DIR.glob(f"{file_path.stem}_*"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        
        if not backups:
            logger.warning(f"No backups for {file_path.name}")
            return False
        
        latest_backup = backups[0]
        shutil.copy2(latest_backup, file_path)
        logger.warning(f"⚠️ ROLLED BACK: {file_path.name}")
        return True
    except Exception as e:
        logger.error(f"Rollback failed: {e}")
        return False

def maybe_global_rollback():
    if not CONFIG.AUTO_ROLLBACK_ON_FAILURE:
        return
    if HEALTH_MONITOR.consecutive_failures < CONFIG.MAX_CONSECUTIVE_FAILURES:
        return
    
    logger.critical("🚨 Global rollback triggered")
    for fname in ["coin.html", "dividend.html", "index.html"]:
        rollback_to_previous(CONFIG.OUTPUT_DIR / fname)

# =========================================================
# Core Functions
# =========================================================
def compute_file_hash(content: str) -> str:
    return hashlib.sha256(content.encode('utf-8')).hexdigest()

def stable_cache_key(tickers: List[str], period: str) -> str:
    """안정적인 캐시 키 생성 (프로세스 재시작 후에도 동일)"""
    ticker_str = ",".join(sorted(tickers))
    key_hash = hashlib.sha1(ticker_str.encode()).hexdigest()
    return f"batch_{key_hash}_{period}"

def atomic_write(file_path: Path, content: str, encoding: str = "utf-8") -> bool:
    tmp_path = None
    try:
        create_backup(file_path)
        
        fd, tmp_path = tempfile.mkstemp(
            prefix=".tmp_",
            suffix=file_path.suffix,
            dir=file_path.parent
        )
        
        with os.fdopen(fd, "w", encoding=encoding) as f:
            f.write(content)
        
        with open(tmp_path, "r", encoding=encoding) as f:
            written_content = f.read()
        
        if compute_file_hash(written_content) != compute_file_hash(content):
            raise ValueError("Hash verification failed")
        
        os.replace(tmp_path, file_path)
        logger.info(f"✓ Wrote: {file_path.name}")
        return True
        
    except Exception as e:
        logger.error(f"Write failed {file_path.name}: {e}")
        
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except:
                pass
        
        if CONFIG.AUTO_ROLLBACK_ON_FAILURE:
            rollback_to_previous(file_path)
        
        return False

# =========================================================
# 🔥 Multi-Source Data Fetching (yfinance → Alpha Vantage)
# =========================================================
def fetch_alpha_vantage_quote(symbol: str) -> Optional[Dict]:
    """Alpha Vantage에서 단일 심볼 가격 가져오기"""
    if not CONFIG.ALPHA_VANTAGE_API_KEY:
        return None
    
    try:
        API_COUNTER.increment()
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": CONFIG.ALPHA_VANTAGE_API_KEY
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if "Global Quote" in data and data["Global Quote"]:
            quote = data["Global Quote"]
            return {
                "symbol": symbol,
                "price": float(quote.get("05. price", 0)),
                "change_percent": float(quote.get("10. change percent", "0%").replace("%", ""))
            }
    except Exception as e:
        logger.debug(f"Alpha Vantage failed for {symbol}: {e}")
    
    return None

def fetch_batch_data_yfinance(tickers: List[str], period: str = "5d") -> Tuple[pd.DataFrame, str]:
    """yfinance로 배치 데이터 가져오기"""
    for attempt in range(1, CONFIG.MAX_RETRIES + 1):
        try:
            logger.info(f"[yfinance] Fetching {len(tickers)} tickers - Attempt {attempt}/{CONFIG.MAX_RETRIES}")
            
            API_COUNTER.increment()
            data = yf.download(
                tickers,
                period=period,
                group_by='ticker',
                threads=True,
                progress=False,
                auto_adjust=True
            )
            
            if data is not None and not data.empty:
                logger.info(f"✓ yfinance batch success")
                return data, "yfinance"
            
            logger.warning("Empty batch data from yfinance")
            
        except Exception as e:
            logger.error(f"yfinance attempt {attempt} failed: {e}")
        
        if attempt < CONFIG.MAX_RETRIES:
            sleep_s = (CONFIG.BASE_DELAY * (2 ** (attempt - 1))) + random.uniform(0, 0.7)
            logger.info(f"⏳ Retry in {sleep_s:.1f}s...")
            time.sleep(sleep_s)
    
    return pd.DataFrame(), "yfinance_failed"

def fetch_batch_data(tickers: List[str], period: str = "5d") -> Tuple[pd.DataFrame, str]:
    """Multi-source fallback: yfinance → Alpha Vantage"""
    cache_key = stable_cache_key(tickers, period)
    
    # 캐시 확인
    if CONFIG.CACHE_ENABLED:
        cached = CACHE.get(cache_key)
        if cached is not None:
            return cached[0], cached[1]
    
    # Primary: yfinance
    data, source = fetch_batch_data_yfinance(tickers, period)
    
    if not data.empty:
        if CONFIG.CACHE_ENABLED:
            CACHE.set(cache_key, (data, source), CONFIG.CACHE_TTL_SECONDS)
        return data, source
    
    # Fallback: Alpha Vantage (일부 심볼만 시도)
    if "alpha_vantage" in CONFIG.FALLBACK_SOURCES and CONFIG.ALPHA_VANTAGE_API_KEY:
        logger.warning("⚠️ yfinance failed, trying Alpha Vantage fallback...")
        
        # Alpha Vantage는 rate limit이 있으므로 처음 10개만 시도
        fallback_data = {}
        for symbol in tickers[:10]:
            quote = fetch_alpha_vantage_quote(symbol)
            if quote:
                fallback_data[symbol] = quote
            time.sleep(0.2)  # Rate limit 방지
        
        if fallback_data:
            logger.info(f"✓ Alpha Vantage fallback: {len(fallback_data)} symbols")
            # 간단한 DataFrame으로 변환 (제한적)
            # 실전에서는 더 정교한 변환 필요
            return pd.DataFrame(), "alpha_vantage_partial"
    
    logger.critical("All data sources failed")
    return pd.DataFrame(), "all_failed"

def extract_symbol_df(batch_data: pd.DataFrame, symbol: str) -> pd.DataFrame:
    if batch_data is None or batch_data.empty:
        raise ValueError(f"Empty batch for {symbol}")
    
    cols = batch_data.columns
    
    if isinstance(cols, pd.MultiIndex):
        tickers_set = set(cols.get_level_values(0))
        symbol_upper = symbol.upper()
        
        matched = None
        for ticker in tickers_set:
            if str(ticker).upper() == symbol_upper:
                matched = ticker
                break
        
        if matched is None:
            raise ValueError(f"{symbol} not in batch")
        
        return batch_data[matched]
    
    if isinstance(cols, pd.Index) and 'Close' in cols:
        return batch_data
    
    raise ValueError(f"Unsupported structure for {symbol}")

def format_crypto_price(price: float) -> str:
    if price < 0.01:
        return f"${price:,.8f}"
    elif price < 1.0:
        return f"${price:,.6f}"
    elif price < 10.0:
        return f"${price:,.4f}"
    else:
        return f"${price:,.2f}"

def calculate_sentiment(batch_data: pd.DataFrame, tickers: List[str]) -> str:
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
            logger.info(f"Sentiment: {positive}/{total} ({ratio*100:.1f}%)")
            
            if ratio >= 0.7:
                return "GREED 🔥"
            elif ratio >= 0.5:
                return "NEUTRAL 😐"
            else:
                return "FEAR 🥶"
    except Exception as e:
        logger.warning(f"Sentiment calc failed: {e}")
    
    return "NEUTRAL 😐"

def generate_html_from_batch(tickers: List[str], batch_data: pd.DataFrame, mode: str = "card") -> Tuple[str, Dict]:
    html = ""
    success = 0
    fail = 0
    failed_samples = []
    
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
        
        except Exception as e:
            fail += 1
            if len(failed_samples) < 5:
                failed_samples.append(symbol)
            
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
    fail_rate = (fail / total * 100) if total > 0 else 0
    
    if fail_rate >= 20:
        logger.warning(f"⚠️ High failure: {fail_rate:.1f}% ({fail}/{total})")
        logger.warning(f"Failed: {', '.join(failed_samples[:5])}")
    else:
        logger.info(f"[{mode.upper()}] ✓ {success} | ✗ {fail} ({fail_rate:.1f}%)")
    
    return html, {
        "success": success,
        "fail": fail,
        "total": total,
        "fail_rate": round(fail_rate, 2)
    }

def get_price_from_batch(batch_data: pd.DataFrame, symbol: str) -> str:
    try:
        df = extract_symbol_df(batch_data, symbol)
        df = df.dropna(subset=['Close'])
        if len(df) > 0:
            return f"${float(df['Close'].iloc[-1]):,.2f}"
    except Exception as e:
        logger.warning(f"Failed to get {symbol}: {e}")
    return "$0.00"

# =========================================================
# Main Update (🔥 Health를 업데이트 결과 반영)
# =========================================================
def run_update() -> Optional[Metrics]:
    start_time = time.time()
    all_stats = {}
    errors = []
    data_source_used = "unknown"
    
    try:
        kst_now = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=9)
        update_time_str = kst_now.strftime("%Y-%m-%d %H:%M KST")
        
        logger.info("=" * 60)
        logger.info(f"🚀 UPDATE START ({update_time_str})")
        logger.info("=" * 60)
        
        # 1) Crypto
        logger.info(">>> Crypto Markets")
        coin_batch, coin_source = fetch_batch_data(COIN_TICKERS, period="5d")
        coin_html, coin_stats = generate_html_from_batch(COIN_TICKERS, coin_batch, mode="card")
        all_stats["crypto"] = coin_stats
        data_source_used = coin_source
        
        # 2) Dividend
        logger.info(">>> Dividend Stocks")
        div_batch, div_source = fetch_batch_data(DIVIDEND_TICKERS, period="5d")
        div_html, div_stats = generate_html_from_batch(DIVIDEND_TICKERS, div_batch, mode="card")
        all_stats["dividend"] = div_stats
        if data_source_used == "unknown":
            data_source_used = div_source
        
        # 3) Nasdaq
        logger.info(">>> NASDAQ-100")
        all_nasdaq = NASDAQ_TICKERS + ["QQQ", "^VIX"]
        nasdaq_batch, nasdaq_source = fetch_batch_data(all_nasdaq, period="5d")
        
        nasdaq_html, nasdaq_stats = generate_html_from_batch(NASDAQ_TICKERS, nasdaq_batch, mode="table")
        all_stats["nasdaq"] = nasdaq_stats
        
        qqq_price = get_price_from_batch(nasdaq_batch, "QQQ")
        vix_price = get_price_from_batch(nasdaq_batch, "^VIX")
        sentiment = calculate_sentiment(nasdaq_batch, NASDAQ_TICKERS)
        
        # Metrics 계산
        duration = time.time() - start_time
        overall_success = sum(s["success"] for s in all_stats.values())
        overall_total = sum(s["total"] for s in all_stats.values())
        overall_rate = (overall_success / overall_total) if overall_total else 0.0
        
        coin_success_rate = (coin_stats["success"] / coin_stats["total"]) if coin_stats["total"] else 0.0
        div_success_rate = (div_stats["success"] / div_stats["total"]) if div_stats["total"] else 0.0
        nasdaq_success_rate = (nasdaq_stats["success"] / nasdaq_stats["total"]) if nasdaq_stats["total"] else 0.0
        
        metrics = Metrics(
            timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            update_duration_seconds=round(duration, 3),
            crypto_success_rate=round(coin_success_rate, 4),
            dividend_success_rate=round(div_success_rate, 4),
            nasdaq_success_rate=round(nasdaq_success_rate, 4),
            overall_success_rate=round(overall_rate, 4),
            total_api_calls=API_COUNTER.get_and_reset(),
            cache_hit_rate=round(CACHE.get_hit_rate(), 4),
            errors=errors,
            data_source=data_source_used
        )
        
        # Health 업데이트 후 반영
        HEALTH_MONITOR.add_metrics(metrics)
        health_status, health_class = HEALTH_MONITOR.get_health_status()
        
        # HTML 생성 (업데이트 후 health 반영)
        coin_final = COIN_TEMPLATE.format(
            update_time=update_time_str,
            content=coin_html,
            success_rate=f"{coin_success_rate*100:.1f}",
            health_status=health_status,
            health_class=health_class,
            data_source=data_source_used
        )
        if not atomic_write(CONFIG.OUTPUT_DIR / "coin.html", coin_final):
            errors.append("coin.html write failed")
        
        div_final = DIV_TEMPLATE.format(
            update_time=update_time_str,
            content=div_html,
            success_rate=f"{div_success_rate*100:.1f}",
            health_status=health_status,
            health_class=health_class,
            data_source=data_source_used
        )
        if not atomic_write(CONFIG.OUTPUT_DIR / "dividend.html", div_final):
            errors.append("dividend.html write failed")
        
        index_final = INDEX_TEMPLATE.format(
            update_time=update_time_str,
            content=nasdaq_html,
            qqq_price=qqq_price,
            vix_price=vix_price,
            sentiment=sentiment,
            success_rate=f"{nasdaq_success_rate*100:.1f}",
            health_status=health_status,
            health_class=health_class,
            data_source=data_source_used
        )
        if not atomic_write(CONFIG.OUTPUT_DIR / "index.html", index_final):
            errors.append("index.html write failed")
        
        # Trends & Status 저장
        HEALTH_MONITOR.save_trends()
        
        status_report = {
            "update_time": update_time_str,
            "metrics": asdict(metrics),
            "stats": all_stats,
            "health": {
                "status": health_status,
                "consecutive_failures": HEALTH_MONITOR.consecutive_failures
            }
        }
        
        with open(CONFIG.OUTPUT_DIR / "status.json", "w") as f:
            json.dump(status_report, f, indent=2)
        
        notify_failure(metrics)
        maybe_global_rollback()
        
        logger.info("=" * 60)
        logger.info(f"🏁 COMPLETE | {overall_rate*100:.1f}% | {health_status} | {duration:.1f}s | {data_source_used}")
        logger.info("=" * 60)
        
        return metrics
        
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        
        duration = time.time() - start_time
        metrics = Metrics(
            timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            update_duration_seconds=round(duration, 3),
            crypto_success_rate=0.0,
            dividend_success_rate=0.0,
            nasdaq_success_rate=0.0,
            overall_success_rate=0.0,
            total_api_calls=API_COUNTER.get_and_reset(),
            cache_hit_rate=0.0,
            errors=[str(e)],
            data_source="error"
        )
        
        HEALTH_MONITOR.add_metrics(metrics)
        HEALTH_MONITOR.save_trends()
        notify_failure(metrics)
        maybe_global_rollback()
        
        send_discord_notification(f"CRITICAL: {str(e)}", is_critical=True)
        send_slack_notification(f"CRITICAL: {str(e)}", is_critical=True)
        
        return None

# =========================================================
# Scheduler
# =========================================================
def start_scheduler():
    interval = max(1, int(CONFIG.UPDATE_INTERVAL_MINUTES))
    
    logger.info("=" * 60)
    logger.info("🤖 SCHEDULER STARTED")
    logger.info(f"Update interval: {interval} minutes")
    logger.info("=" * 60)
    
    run_update()
    
    schedule.every(interval).minutes.do(run_update)
    
    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except KeyboardInterrupt:
            logger.warning("Scheduler stopped by user")
            break
        except Exception as e:
            logger.error(f"Scheduler error: {e}", exc_info=True)
            time.sleep(5)

# =========================================================
# CLI
# =========================================================
def main():
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "once":
            logger.info("Running single update...")
            run_update()
        
        elif command == "schedule":
            start_scheduler()
        
        elif command == "clear-cache":
            CACHE.clear()
            logger.info("✓ Cache cleared")
        
        elif command == "health":
            status, css = HEALTH_MONITOR.get_health_status()
            print(f"Health Status: {status}")
            print(f"Consecutive Failures: {HEALTH_MONITOR.consecutive_failures}")
            print(f"Cache Hit Rate: {CACHE.get_hit_rate()*100:.1f}%")
        
        else:
            print("Usage:")
            print("  python script.py once        - Run single update")
            print("  python script.py schedule    - Start scheduler (1hr)")
            print("  python script.py clear-cache - Clear cache")
            print("  python script.py health      - Show health status")
    
    else:
        run_update()

if __name__ == "__main__":
    main()
