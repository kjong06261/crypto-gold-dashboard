import yfinance as yf
import pandas as pd
import datetime
import time
import os
import pytz
from typing import List, Dict
from pathlib import Path

# =========================================================
# 1. 시스템 설정 (완벽 배포용)
# =========================================================
OUTPUT_DIR = Path("./docs")
ASSETS_DIR = OUTPUT_DIR / "assets"
AI_DIR = OUTPUT_DIR / "ai"
BLOG_DIR = OUTPUT_DIR / "blog"
for d in [ASSETS_DIR, AI_DIR, BLOG_DIR]: d.mkdir(parents=True, exist_ok=True)

CUSTOM_DOMAIN = "us-dividend-pro.com"
BASE_URL = f"https://{CUSTOM_DOMAIN}"
SITE_NAME = "US Market Terminals"

# [애드센스 & SEO]
ADSENSE_HEAD = """<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3030006828946894" crossorigin="anonymous"></script>"""
ADS_TXT_LINE = "google.com, pub-3030006828946894, DIRECT, f08c47fec0942fa0"

# =========================================================
# 2. 디자인 시스템 (패치 완료: analysis, small-muted 클래스 추가)
# =========================================================
BASE_CSS = """
:root{--bg:#05070a;--panel:#11141b;--border:#1e222d;--text:#d1d4dc;--muted:#8b949e;--link:#58a6ff;--accent:#fbbf24;--success:#00d084;}
body{margin:0;padding:18px;background:var(--bg);color:var(--text);font-family:system-ui,sans-serif;line-height:1.6;}
.container{max-width:1200px;margin:0 auto}
.nav{display:flex;flex-wrap:wrap;gap:10px;padding:12px;background:#0b0e14;margin-bottom:16px;border-radius:12px;border:1px solid var(--border)}
.nav a{color:var(--link);text-decoration:none;padding:8px 14px;background:rgba(255,255,255,0.03);border-radius:8px;font-weight:600;}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:20px;margin-bottom:30px}
.card{background:var(--panel);border:1px solid var(--border);padding:20px;border-radius:14px;transition:0.3s;}
.card:hover{border-color:var(--accent);transform:translateY(-3px);}
.analysis{background:var(--panel);padding:20px;border-radius:12px;margin:20px 0;border:1px solid var(--border);}
.small-muted{font-size:0.85em;color:var(--muted);margin-top:5px;}
.calc-card{background:var(--panel);border:2px solid var(--accent);padding:25px;border-radius:15px;margin:20px 0}
.calc-input{width:100%;padding:12px;margin:8px 0;background:#0b0e14;border:1px solid var(--border);color:#fff;border-radius:8px;outline:none}
.calc-btn{width:100%;padding:15px;background:var(--accent);color:#000;font-weight:800;border:none;border-radius:8px;cursor:pointer}
footer{text-align:center;padding:40px 0;color:var(--muted);font-size:0.9rem;border-top:1px solid var(--border)}
"""

# [경로 패치] 모든 링크를 절대경로(/)로 통일하여 SEO 및 크롤링 최적화
NAV_HTML = f"""<div class="nav"><strong style="color:var(--accent)">{SITE_NAME}</strong><a href="/index.html">Home</a><a href="/finance.html">Finance</a><a href="/ai_tools.html">Investor AI</a><a href="/blog/index.html">Insights</a></div>"""

def wrap_page(title, body, desc="Pro AI-Financial Analysis Terminal"):
    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">{ADSENSE_HEAD}<meta name="viewport" content="width=device-width,initial-scale=1.0"><meta name="description" content="{desc}"><title>{title} | {SITE_NAME}</title><style>{BASE_CSS}</style></head><body><div class="container">{NAV_HTML}{body}<footer>© 2025 {SITE_NAME} - Updated Hourly.</footer></div></body></html>"""

# [계산기 패치] r=0 방어 및 NaN 처리 완료
SCRIPTS = """<script>
function calcInvestment(){
    let p=parseFloat(document.getElementById('p').value)||0;
    let m=parseFloat(document.getElementById('m').value)||0;
    let r_val=parseFloat(document.getElementById('r').value);
    let y_raw=parseInt(document.getElementById('y').value);
    let y = (isFinite(y_raw) ? y_raw : 0) * 12;
    let total=0;
    if(!isFinite(r_val) || r_val === 0){
        total = p + (m * y);
    } else {
        let r = r_val/100/12;
        total = p * Math.pow(1+r, y) + m*((Math.pow(1+r, y)-1)/r);
    }
    document.getElementById('res').innerHTML="<div style='margin-top:15px; font-size:1.5em; color:var(--accent)'>Est. Value: $"+total.toLocaleString(undefined,{maximumFractionDigits:0})+"</div>";
}
function compareAI(){
    document.getElementById('ai_res').innerHTML="<div style='background:#0b0e14; padding:15px; border-radius:10px; margin-top:15px; color:var(--success)'>DeepSeek: Low Cost ($0.01) | Claude: High Intelligence ($0.50)<br><b>💡 Pro Tip: Use DeepSeek for bulk data analysis!</b></div>";
}
</script>"""

# =========================================================
# 3. 데이터 및 빌드 엔진 (Finance 200 + AI 30)
# =========================================================
# (중략: FINANCE_TICKERS, AI_TOOLS_30 리스트 및 yfinance 연동 루프)
# 패치: created_assets 기반 sitemap 자동 생성 로직 적용
