import yfinance as yf
import pandas as pd
import datetime
import time
import os
import pytz
from pathlib import Path

OUTPUT_DIR = Path("./docs")
ASSETS_DIR = OUTPUT_DIR / "assets"
AI_DIR = OUTPUT_DIR / "ai"

for d in [ASSETS_DIR, AI_DIR]: 
    d.mkdir(parents=True, exist_ok=True)

CUSTOM_DOMAIN = "us-dividend-pro.com"
ADSENSE_HEAD = '<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3030006828946894" crossorigin="anonymous"></script>'

FINANCE_TICKERS = ['AAPL','MSFT','GOOGL','AMZN','NVDA','TSLA','META','AVGO','ORCL','ADBE']

AI_TOOLS_30 = [
    {"id":"perplexity-pro","name":"Perplexity Pro","cat":"Research","price":"$20/mo","str":"Real-time news & citations","use":"Market trend investigation"},
    {"id":"claude-sonnet","name":"Claude 3.5 Sonnet","cat":"Analysis","price":"$20/mo","str":"Deep reasoning & risk assessment","use":"Financial statement analysis"},
    {"id":"deepseek-v3","name":"DeepSeek V3","cat":"Code/Data","price":"$0.01/task","str":"Ultra low-cost processing","use":"Quant strategy development"},
    {"id":"gpt-4o","name":"GPT-4o","cat":"Multi-modal","price":"$20/mo","str":"Creative reports & vision","use":"Investment report writing"},
    {"id":"gemini-pro","name":"Gemini Pro","cat":"Verification","price":"Free tier","str":"Google ecosystem integration","use":"Cross-verification of analysis"}
]

for i in range(6, 31):
    AI_TOOLS_30.append({
        "id": f"fintool-{i}",
        "name": f"Investment AI Tool {i}",
        "cat": "Investment Analysis",
        "price": "$10-50/mo",
        "str": f"Advanced financial analysis feature set {i}",
        "use": f"Portfolio optimization and risk management"
    })

BASE_CSS = ":root{--bg:#05070a;--text:#d1d4dc;--accent:#fbbf24;}body{margin:0;padding:20px;background:var(--bg);color:var(--text);font-family:system-ui;}.container{max-width:1200px;margin:0 auto}.card{background:#11141b;padding:20px;margin:10px 0;border-radius:12px;border:1px solid #1e222d;}"

NAV = '<div style="margin-bottom:30px;"><a href="/index.html" style="color:#58a6ff;margin-right:20px;">Home</a><a href="/finance.html" style="color:#58a6ff;margin-right:20px;">Finance</a><a href="/ai_tools.html" style="color:#58a6ff;">Investor AI</a></div>'

def wrap(title, body):
    return f"<!DOCTYPE html><html><head><meta charset='UTF-8'>{ADSENSE_HEAD}<title>{title}</title><style>{BASE_CSS}</style></head><body><div class='container'>{NAV}<h1 style='color:var(--accent);'>{title}</h1>{body}<footer style='margin-top:50px;padding-top:20px;border-top:1px solid #1e222d;text-align:center;color:#8b949e;'>© 2025 US Market Terminals</footer></div></body></html>"

def main():
    print("🚀 Starting build...")
    
    # Home
    home = wrap("US Market Terminals", "<div class='card'><h2>Financial Terminal</h2><p><a href='/finance.html' style='color:var(--accent);'>View Markets →</a></p></div><div class='card'><h2>AI Investment Tools</h2><p><a href='/ai_tools.html' style='color:var(--accent);'>Explore AI →</a></p></div>")
    (OUTPUT_DIR / "index.html").write_text(home, encoding="utf-8")
    
    # Finance
    finance_html = ""
    for ticker in FINANCE_TICKERS:
        try:
            print(f"📡 {ticker}")
            stock = yf.Ticker(ticker)
            price = stock.info.get('currentPrice', 0)
            if price > 0:
                finance_html += f"<div class='card'><h3>{ticker}</h3><p style='font-size:1.5em;color:var(--accent);'>${price:.2f}</p><a href='/assets/{ticker}.html' style='color:#58a6ff;'>Analysis →</a></div>"
                asset_page = wrap(f"{ticker} Analysis", f"<div class='card'><h2>Current Price</h2><p style='font-size:2em;color:var(--accent);'>${price:.2f}</p><p>Real-time market data for {ticker}. Use AI tools like Perplexity Pro for deeper analysis.</p></div>")
                (ASSETS_DIR / f"{ticker}.html").write_text(asset_page, encoding="utf-8")
            time.sleep(0.2)
        except:
            pass
    
    (OUTPUT_DIR / "finance.html").write_text(wrap("Finance Terminal", finance_html), encoding="utf-8")
    
    # AI Tools List
    ai_list = "".join([f"<div class='card'><h3>{t['name']}</h3><p style='color:#8b949e;'>{t['cat']}</p><p>{t['str']}</p><a href='/ai/{t['id']}.html' style='color:var(--accent);'>Details →</a></div>" for t in AI_TOOLS_30])
    (OUTPUT_DIR / "ai_tools.html").write_text(wrap("Investor AI Toolkit", ai_list), encoding="utf-8")
    
    # AI Individual Pages
    for tool in AI_TOOLS_30:
        print(f"🤖 {tool['name']}")
        ai_page = wrap(tool['name'], f"""
        <div class='card'>
            <h2>Overview</h2>
            <p><strong>Category:</strong> {tool['cat']}</p>
            <p><strong>Pricing:</strong> {tool['price']}</p>
            <p><strong>Core Strength:</strong> {tool['str']}</p>
            <p><strong>Investment Use Case:</strong> {tool['use']}</p>
        </div>
        <div class='card'>
            <h3>💡 Integration Tip</h3>
            <p>Use {tool['name']} alongside our <a href='/finance.html' style='color:var(--accent);'>Finance Terminal</a> for enhanced market analysis.</p>
        </div>
        """)
        (AI_DIR / f"{tool['id']}.html").write_text(ai_page, encoding="utf-8")
    
    # SEO Files
    (OUTPUT_DIR / "CNAME").write_text(CUSTOM_DOMAIN, encoding="utf-8")
    (OUTPUT_DIR / "ads.txt").write_text("google.com, pub-3030006828946894, DIRECT, f08c47fec0942fa0", encoding="utf-8")
    
    print("✅ Build complete!")

if __name__ == "__main__":
    main()
