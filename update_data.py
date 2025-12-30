import yfinance as yf
import pandas as pd
import datetime
import time
import os
import pytz
from typing import List, Dict
from pathlib import Path

# =========================================================
# 1. 시스템 설정
# =========================================================
OUTPUT_DIR = Path("./docs")
ASSETS_DIR = OUTPUT_DIR / "assets"
AI_DIR = OUTPUT_DIR / "ai"
BLOG_DIR = OUTPUT_DIR / "blog"

for d in [ASSETS_DIR, AI_DIR, BLOG_DIR]: 
    d.mkdir(parents=True, exist_ok=True)

CUSTOM_DOMAIN = "us-dividend-pro.com"
BASE_URL = f"https://{CUSTOM_DOMAIN}"
SITE_NAME = "US Market Terminals"

ADSENSE_HEAD = """<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3030006828946894" crossorigin="anonymous"></script>"""
ADS_TXT_LINE = "google.com, pub-3030006828946894, DIRECT, f08c47fec0942fa0"

# =========================================================
# 2. 데이터베이스 (Finance 200 + AI Tools 30)
# =========================================================
FINANCE_TICKERS = [
    'AAPL','MSFT','GOOGL','AMZN','NVDA','TSLA','META','AVGO','ORCL','ADBE','CRM','AMD','QCOM','TXN','INTC','MU',
    'O','SCHD','JEPI','VICI','MAIN','STAG','ADC','MO','T','VZ','PFE','JNJ','PG','KO','PEP','MMM','ABBV','XOM',
    'SPY','QQQ','DIA','VTI','VOO','IVV','IWM','VGT','XLK','XLY','XLP','XLV','XLF','XLB','XLE','XLU','XLRE'
]

AI_TOOLS_30 = [
    {"id":"perplexity-pro","name":"Perplexity Pro","cat":"Research","price":"$20/mo","str":"Real-time news & citations","use":"Market investigation"},
    {"id":"claude-3-5-sonnet","name":"Claude 3.5 Sonnet","cat":"Analysis","price":"$20/mo","str":"Logical reasoning & risk","use":"Financial analysis"},
    {"id":"deepseek-v3","name":"DeepSeek V3","cat":"Code/Data","price":"$0.01/task","str":"Unmatched cost-efficiency","use":"Quant development"},
    {"id":"gpt-4o","name":"GPT-4o","cat":"Multi-modal","price":"$20/mo","str":"Creative reports & vision","use":"Report writing"},
    {"id":"gemini-pro","name":"Gemini Pro","cat":"Verification","price":"Free/Paid","str":"Google ecosystem sync","use":"Result validation"}
] + [{"id":f"tool-{i}","name":f"FinTech Tool {i}","cat":"Investment AI","price":"$10/mo","str":f"Smart Feature {i}","use":f"Financial use {i}"} for i in range(6,31)]

# =========================================================
# 3. 디자인 시스템
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
.calc-card{background:var(--panel);border:2px solid var(--accent);padding:25px;border-radius:15px;margin:20px 0}
.calc-input{width:100%;padding:12px;margin:8px 0;background:#0b0e14;border:1px solid var(--border);color:#fff;border-radius:8px;outline:none}
.calc-btn{width:100%;padding:15px;background:var(--accent);color:#000;font-weight:800;border:none;border-radius:8px;cursor:pointer}
footer{text-align:center;padding:40px 0;color:var(--muted);font-size:0.9rem;border-top:1px solid var(--border)}
"""

NAV_HTML = f"""<div class="nav"><strong style="color:var(--accent)">{SITE_NAME}</strong><a href="/index.html">Home</a><a href="/finance.html">Finance</a><a href="/ai_tools.html">Investor AI</a><a href="/blog/index.html">Blog</a></div>"""

def wrap_page(title, body, desc="Pro AI-Financial Analysis Terminal"):
    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">{ADSENSE_HEAD}<meta name="viewport" content="width=device-width,initial-scale=1.0"><meta name="description" content="{desc}"><title>{title} | {SITE_NAME}</title><style>{BASE_CSS}</style></head><body><div class="container">{NAV_HTML}{body}<footer>© 2025 {SITE_NAME}</footer></div></body></html>"""

SCRIPTS = """<script>
function calcInvestment(){
    let p=parseFloat(document.getElementById('p').value)||0;
    let m=parseFloat(document.getElementById('m').value)||0;
    let r_val=parseFloat(document.getElementById('r').value);
    let y=parseInt(document.getElementById('y').value)*12;
    let total=0;
    if(!isFinite(r_val) || r_val === 0){ total = p + (m * y); }
    else { let r = r_val/100/12; total = p * Math.pow(1+r, y) + m*((Math.pow(1+r, y)-1)/r); }
    document.getElementById('res').innerHTML="<div style='margin-top:15px; font-size:1.5em; color:var(--accent)'>Est. Value: $"+total.toLocaleString(undefined,{maximumFractionDigits:0})+"</div>";
}
function compareAI(){
    document.getElementById('ai_res').innerHTML="<div style='background:#0b0e14; padding:15px; border-radius:10px; margin-top:15px; color:var(--success)'>DeepSeek: Low Cost ($0.01) | Claude: High Intelligence ($0.50)</div>";
}
</script>"""

def main():
    print("🚀 빌드를 시작합니다...")
    tz = pytz.timezone('US/Eastern')
    created_assets = []

    # [1] Index
    home_body = f"<h1>🚀 Financial Terminal</h1><div class='grid'><div class='card'><h2>Finance</h2><a href='/finance.html'>Enter</a></div><div class='card'><h2>AI Tools</h2><a href='/ai_tools.html'>Explore</a></div></div>"
    (OUTPUT_DIR / "index.html").write_text(wrap_page("Home", home_body), encoding="utf-8")

    # [2] Finance & Assets
    finance_cards = ""
    for ticker in FINANCE_TICKERS:
        try:
            print(f"📡 수집 중: {ticker}")
            stock = yf.Ticker(ticker)
            info = stock.info
            price = info.get('currentPrice', info.get('regularMarketPrice', 0))
            if price == 0: continue
            finance_cards += f"<div class='card'><h3>{ticker}</h3><div style='font-size:1.5em;color:var(--accent)'>${price:.2f}</div><a href='/assets/{ticker}.html'>Analysis</a></div>"
            (ASSETS_DIR / f"{ticker}.html").write_text(wrap_page(f"{ticker} Analysis", f"<h1>{ticker}</h1><div class='analysis'>Price: ${price:.2f}</div>"), encoding="utf-8")
            created_assets.append(ticker)
            time.sleep(0.1)
        except: continue

    (OUTPUT_DIR / "finance.html").write_text(wrap_page("Finance", f"<div class='grid'>{finance_cards}</div>"), encoding="utf-8")

    # [3] AI Tools
    ai_cards = "".join([f"<div class='card'><h3>{t['name']}</h3><a href='/ai/{t['id']}.html'>Details</a></div>" for t in AI_TOOLS_30])
    (OUTPUT_DIR / "ai_tools.html").write_text(wrap_page("AI Tools", f"<div class='grid'>{ai_cards}</div>"), encoding="utf-8")
    for tool in AI_TOOLS_30:
        (AI_DIR / f"{tool['id']}.html").write_text(wrap_page(tool['name'], f"<h1>{tool['name']}</h1><div class='analysis'>{tool['str']}</div>"), encoding="utf-8")

    # [4] SEO
    (OUTPUT_DIR / "CNAME").write_text(CUSTOM_DOMAIN, encoding="utf-8")
    (OUTPUT_DIR / "ads.txt").write_text(ADS_TXT_LINE, encoding="utf-8")
    (OUTPUT_DIR / "robots.txt").write_text(f"User-agent: *\nSitemap: {BASE_URL}/sitemap.xml", encoding="utf-8")
    
    sitemap_xml = '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    for u in ["/index.html", "/finance.html", "/ai_tools.html"]: sitemap_xml += f"<url><loc>{BASE_URL}{u}</loc></url>"
    for t in created_assets: sitemap_xml += f"<url><loc>{BASE_URL}/assets/{t}.html</loc></url>"
    sitemap_xml += "</urlset>"
    (OUTPUT_DIR / "sitemap.xml").write_text(sitemap_xml, encoding="utf-8")
    print("✅ 빌드 완료!")

if __name__ == "__main__":
    main()
