import yfinance as yf
import pandas as pd
import datetime
import time
import os
import pytz
from pathlib import Path

# [설정]
OUTPUT_DIR = Path("./docs")
ASSETS_DIR = OUTPUT_DIR / "assets"
AI_DIR = OUTPUT_DIR / "ai"
for d in [ASSETS_DIR, AI_DIR]: d.mkdir(parents=True, exist_ok=True)

CUSTOM_DOMAIN = "us-dividend-pro.com"
BASE_URL = f"https://{CUSTOM_DOMAIN}"
SITE_NAME = "US Market Terminals"

# [수익화 코드]
ADSENSE_HEAD = """<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3030006828946894" crossorigin="anonymous"></script>"""
ADS_TXT = "google.com, pub-3030006828946894, DIRECT, f08c47fec0942fa0"

# [데이터: AI 툴 30개]
AI_TOOLS = [
    {"id":"perplexity-pro","name":"Perplexity Pro","cat":"Research","str":"Real-time search with citations"},
    {"id":"claude-3-5-sonnet","name":"Claude 3.5 Sonnet","cat":"Analysis","str":"Deep financial reasoning"},
    {"id":"deepseek-v3","name":"DeepSeek V3","cat":"Data","str":"Extreme cost-efficiency for quant"},
    {"id":"gpt-4o","name":"GPT-4o","cat":"Multi-modal","str":"Market report & chart vision"},
    {"id":"gemini-pro","name":"Gemini Pro","cat":"Verification","str":"Google Sheets sync tool"}
] + [{"id":f"tool-{i}","name":f"FinTech AI {i}","cat":"Investing","str":f"Advanced Analysis {i}"} for i in range(6,31)]

FINANCE_TICKERS = ['AAPL','MSFT','GOOGL','AMZN','NVDA','TSLA','META','O','SCHD','JEPI','SPY','QQQ'] # 핵심 위주

# [디자인 복구: 프리미엄 다크 모드]
BASE_CSS = """
:root{--bg:#05070a;--panel:#11141b;--border:#1e222d;--text:#d1d4dc;--accent:#fbbf24;--link:#58a6ff;}
body{margin:0;padding:20px;background:var(--bg);color:var(--text);font-family:sans-serif;}
.container{max-width:1100px;margin:0 auto}
.nav{display:flex;gap:15px;padding:15px;background:#0b0e14;border-radius:12px;border:1px solid var(--border);margin-bottom:20px;}
.nav a{color:var(--text);text-decoration:none;font-weight:600;}
.nav a:hover{color:var(--accent);}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:15px;}
.card{background:var(--panel);border:1px solid var(--border);padding:20px;border-radius:12px;}
.btn{display:inline-block;margin-top:10px;color:var(--accent);text-decoration:none;font-weight:bold;}
footer{text-align:center;margin-top:50px;color:var(--muted);font-size:0.8rem;border-top:1px solid var(--border);padding-top:20px;}
"""

def wrap(title, body):
    nav = f'<div class="nav"><b>{SITE_NAME}</b> <a href="/index.html">Home</a> <a href="/finance.html">Finance</a> <a href="/ai_tools.html">AI Tools</a> <a href="/about.html">About</a></div>'
    return f"<html><head>{ADSENSE_HEAD}<title>{title}</title><style>{BASE_CSS}</style></head><body><div class='container'>{nav}{body}<footer>© 2025 {SITE_NAME} | <a href='/privacy.html'>Privacy</a> | <a href='/terms.html'>Terms</a></footer></div></body></html>"

def main():
    print("🚀 제미나이 엔진으로 사이트 복구 시작...")
    
    # 1. Home
    (OUTPUT_DIR / "index.html").write_text(wrap("Home", "<h1>Investor AI & Market Terminal</h1><div class='grid'><div class='card'><h2>Market Data</h2><p>Real-time asset analysis</p><a href='/finance.html' class='btn'>Enter →</a></div><div class='card'><h2>AI Tools</h2><p>30+ AI for Investors</p><a href='/ai_tools.html' class='btn'>Explore →</a></div></div>"), encoding="utf-8")

    # 2. AI Tools Hub & Pages
    ai_html = "<h1>Investor AI Toolkit</h1><div class='grid'>"
    for t in AI_TOOLS:
        ai_html += f"<div class='card'><h3>{t['name']}</h3><p>{t['cat']}</p><a href='/ai/{t['id']}.html' class='btn'>Learn More</a></div>"
        (AI_DIR / f"{t['id']}.html").write_text(wrap(t['name'], f"<h1>{t['name']}</h1><div class='card'><p>{t['str']}</p><p>This AI tool enhances your investment workflow by providing data-driven insights.</p></div>"), encoding="utf-8")
    (OUTPUT_DIR / "ai_tools.html").write_text(wrap("AI Tools", ai_html + "</div>"), encoding="utf-8")

    # 3. Finance Hub
    fin_html = "<h1>Market Terminal</h1><div class='grid'>"
    for ticker in FINANCE_TICKERS:
        try:
            print(f"📡 수집: {ticker}")
            stock = yf.Ticker(ticker)
            price = stock.info.get('currentPrice', 0)
            fin_html += f"<div class='card'><h3>{ticker}</h3><p style='font-size:1.5rem;color:var(--accent)'>${price}</p><a href='/assets/{ticker}.html' class='btn'>Deep Analysis</a></div>"
            (ASSETS_DIR / f"{ticker}.html").write_text(wrap(ticker, f"<h1>{ticker} Analysis</h1><div class='card'>Current Price: ${price}</div>"), encoding="utf-8")
            time.sleep(0.1)
        except: continue
    (OUTPUT_DIR / "finance.html").write_text(wrap("Finance", fin_html + "</div>"), encoding="utf-8")

    # 4. 필수 법적 페이지 (복구 핵심)
    (OUTPUT_DIR / "about.html").write_text(wrap("About", "<h1>About Us</h1><p>Professional terminal for AI-driven investing.</p>"), encoding="utf-8")
    (OUTPUT_DIR / "privacy.html").write_text(wrap("Privacy", "<h1>Privacy Policy</h1><p>We use cookies for AdSense. No personal data collected.</p>"), encoding="utf-8")
    (OUTPUT_DIR / "terms.html").write_text(wrap("Terms", "<h1>Terms of Service</h1><p>Informational purposes only. Not financial advice.</p>"), encoding="utf-8")

    # 5. SEO & Adsense
    (OUTPUT_DIR / "ads.txt").write_text(ADS_TXT, encoding="utf-8")
    (OUTPUT_DIR / "CNAME").write_text(CUSTOM_DOMAIN, encoding="utf-8")
    
    # 6. Sitemap (모든 AI 페이지 포함)
    sitemap = f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>{BASE_URL}/index.html</loc></url>'
    for t in AI_TOOLS: sitemap += f"<url><loc>{BASE_URL}/ai/{t['id']}.html</loc></url>"
    sitemap += "</urlset>"
    (OUTPUT_DIR / "sitemap.xml").write_text(sitemap, encoding="utf-8")
    print("✅ 복구 완료!")

if __name__ == "__main__": main()
