import yfinance as yf
import pandas as pd
import datetime, pytz, os, re, time, html, json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# =========================================================
# 0) 경로 및 환경 설정 (Atomic & API 지원)
# =========================================================
OUTPUT_DIR = Path("./docs")
ASSETS_DIR = OUTPUT_DIR / "assets"
AI_DIR = OUTPUT_DIR / "ai"
BLOG_DIR = OUTPUT_DIR / "blog"
CACHE_DIR = OUTPUT_DIR / ".cache"
API_DIR = OUTPUT_DIR / "api" # API Export용
for d in [OUTPUT_DIR, ASSETS_DIR, AI_DIR, BLOG_DIR, CACHE_DIR, API_DIR]: 
    d.mkdir(parents=True, exist_ok=True)

SITE_NAME = "US Dividend Pro"
BASE_URL = os.getenv("BASE_URL", "").rstrip("/")
SITE_URL = os.getenv("SITE_URL", "").rstrip("/")
CACHE_MINUTES = 5
MAX_WORKERS = int(os.getenv("MAX_WORKERS", "6"))

def u(path: str) -> str:
    if not path.startswith("/"): path = "/" + path
    return f"{BASE_URL}{path}"

def abs_url(path: str) -> str:
    path_clean = u(path)
    return (SITE_URL + path_clean) if SITE_URL else path_clean

def safe_slug(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9_-]+", "_", s).lower()

def atomic_write(path: Path, text: str):
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)

# =========================================================
# 1) 티커 및 디자인 설정
# =========================================================
TICKERS = {
    "crypto": ["BTC-USD","ETH-USD","SOL-USD","XRP-USD"],
    "tech": ["AAPL","MSFT","NVDA","AMZN","META","GOOGL","TSLA"],
    "dividend": ["O","SCHD","JEPI","VICI","MAIN","STAG","ADC"],
}
ALL_TICKERS = sorted(set(sum(TICKERS.values(), [])))
AI_TOOLS = [f"AI-Strategy-Tool-{i}" for i in range(1, 51)]

def get_category(ticker: str) -> str:
    for cat, tickers in TICKERS.items():
        if ticker in tickers: return cat
    return "other"

BASE_CSS = """
:root{--bg:#05070a;--panel:#11141b;--border:#1e222d;--text:#d1d4dc;--muted:#8b949e;--link:#58a6ff;--success:#00d084;--danger:#ff3366;}
body{margin:0;background:var(--bg);color:var(--text);font-family:system-ui,sans-serif;line-height:1.6;}
.container{max-width:1200px;margin:0 auto;padding:20px;}
.nav{display:flex;gap:12px;padding:15px 5%;background:#0b0e14;border-bottom:1px solid var(--border);position:sticky;top:0;z-index:100;align-items:center;}
.nav strong{color:#fff;margin-right:auto;}
.nav a{color:var(--link);text-decoration:none;font-weight:700;padding:8px 14px;background:#1e222d;border-radius:8px;font-size:0.9rem;}
.hero{text-align:center;padding:50px 20px;background:rgba(88,166,255,0.03);border-radius:16px;margin:20px 0;}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:15px;margin:20px 0;}
.stat-card{background:var(--panel);padding:20px;border-radius:12px;border:1px solid var(--border);text-align:center;}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:18px;}
.card{background:var(--panel);border:1px solid var(--border);padding:20px;border-radius:14px;text-decoration:none;color:inherit;transition:0.2s;display:flex;flex-direction:column;gap:8px;}
.card:hover{border-color:var(--link);transform:translateY(-3px);}
.filter-btns{display:flex;gap:10px;margin:20px 0;flex-wrap:wrap;}
.filter-btns button{padding:10px 18px;background:var(--panel);border:1px solid var(--border);color:var(--text);border-radius:8px;cursor:pointer;font-weight:600;}
.filter-btns button.active{background:var(--link);color:#000;}
footer{text-align:center;padding:40px;margin-top:60px;color:var(--muted);font-size:0.8rem;border-top:1px solid var(--border);}
"""

FILTER_JS = """
<script>
function filterCat(cat, el){
    document.querySelectorAll('.filter-btns button').forEach(b=>b.classList.remove('active'));
    if(el) el.classList.add('active');
    document.querySelectorAll('.grid .card[data-cat]').forEach(c=>{
        c.style.display=(cat==='all'||c.dataset.cat===cat)?'flex':'none';
    });
}
</script>
"""

def wrap_page(title, body, last_et, desc="Professional market analytics.", include_js=False):
    site, t_h, d_h = html.escape(SITE_NAME), html.escape(title), html.escape(desc)
    js = FILTER_JS if include_js else ""
    nav = f"<div class='nav'><strong>{site}</strong><a href='{u('/index.html')}'>Home</a><a href='{u('/finance.html')}'>Terminal</a><a href='{u('/ai_tools.html')}'>AI Tools</a></div>"
    return f"<!DOCTYPE html><html lang='en'><head><meta charset='UTF-8'><meta name='viewport' content='width=device-width,initial-scale=1.0'><meta name='description' content='{d_h}'><title>{t_h} | {site}</title><style>{BASE_CSS}</style>{js}</head><body>{nav}<div class='container'>{body}</div><footer>© 2025 {site} | Sync: {html.escape(last_et)}</footer></body></html>"

# =========================================================
# 2) 수집 및 데이터 처리 (Validation)
# =========================================================
REQ_KEYS = {"t","p","c","v","slug","cat","ts"}
def fetch_data(t):
    cache_file = CACHE_DIR / f"{safe_slug(t)}.json"
    if cache_file.exists():
        try:
            d = json.loads(cache_file.read_text(encoding="utf-8"))
            if REQ_KEYS.issubset(d.keys()) and time.time() - d['ts'] < CACHE_MINUTES * 60: return d
        except: pass

    try:
        s = yf.Ticker(t)
        h = s.history(period="2d", auto_adjust=False)
        if h.empty or len(h) < 2: return None
        p, prev = float(h['Close'].iloc[-1]), float(h['Close'].iloc[-2])
        res = {"t": t, "p": p, "c": ((p-prev)/prev)*100, "v": int(h['Volume'].iloc[-1]), "slug": safe_slug(t), "cat": get_category(t), "ts": time.time()}
        atomic_write(cache_file, json.dumps(res, ensure_ascii=False))
        return res
    except: return None

# =========================================================
# 3) 빌드 엔진
# =========================================================
def main():
    start_time = time.time()
    now_et = datetime.datetime.now(pytz.timezone("US/Eastern")).strftime("%Y-%m-%d %H:%M %Z")
    
    results = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futures = [ex.submit(fetch_data, t) for t in ALL_TICKERS]
        for f in as_completed(futures):
            r = f.result()
            if r: results.append(r)
    results.sort(key=lambda x: x['t'])

    # [D] API Export
    atomic_write(API_DIR / "assets.json", json.dumps(results, ensure_ascii=False, indent=2))

    # Assets Individual Pages (1번 수정 반영)
    for a in results:
        color = "var(--success)" if a['c'] >= 0 else "var(--danger)"
        body = f"<div class='hero'><h1>{html.escape(a['t'])}</h1><div style='font-size:2.5rem;font-weight:800;color:{color}'>${a['p']:,.2f} ({a['c']:+.2f}%)</div><p>Volume: {a['v']:,}</p></div>"
        (ASSETS_DIR / f"{a['slug']}.html").write_text(wrap_page(f"{a['t']} Analysis", body, now_et), encoding="utf-8")

    # Finance Terminal (3번 수정 반영)
    avg_c = (sum(x['c'] for x in results)/len(results)) if results else 0.0
    stats_h = f"<div class='stats'><div class='stat-card'><strong>Assets</strong><br>{len(results)}</div><div class='stat-card'><strong>Avg Change</strong><br>{avg_c:+.2f}%</div></div>"
    btns = f"<div class='filter-btns'><button class='active' onclick='filterCat(\"all\", this)'>All</button>" + "".join([f"<button onclick='filterCat(\"{c}\", this)'>{c.upper()}</button>" for c in TICKERS.keys()]) + "</div>"
    
    grid = "<div class='grid'>"
    for a in results:
        color = "var(--success)" if a['c'] >= 0 else "var(--danger)"
        grid += f"<a href='{u('/assets/'+a['slug']+'.html')}' class='card' data-cat='{a['cat']}'><strong>{html.escape(a['t'])}</strong><span style='font-size:1.2rem;font-weight:700;'>${a['p']:,.2f}</span><span style='color:{color};font-weight:800;'>{a['c']:+.2f}%</span></a>"
    grid += "</div>"
    (OUTPUT_DIR / "finance.html").write_text(wrap_page("Terminal", stats_h + btns + grid, now_et, include_js=True), encoding="utf-8")

    # AI Tools (4번 수정 반영)
    ai_idx = "<h1>AI Tools</h1><div class='grid'>" + "".join([f"<a href='{u('/ai/'+safe_slug(t)+'.html')}' class='card'><strong>{html.escape(t)}</strong></a>" for t in AI_TOOLS]) + "</div>"
    (OUTPUT_DIR / "ai_tools.html").write_text(wrap_page("AI Directory", ai_idx, now_et), encoding="utf-8")
    for t in AI_TOOLS:
        (AI_DIR / f"{safe_slug(t)}.html").write_text(wrap_page(t, f"<h1>{html.escape(t)}</h1><p>AI-driven analysis tool content here.</p>", now_et), encoding="utf-8")

    # SEO & Index
    (OUTPUT_DIR / "index.html").write_text(wrap_page("Home", "<div class='hero'><h1>US Dividend Pro</h1><p>Institutional Grade Market Terminal</p></div>", now_et), encoding="utf-8")
    (OUTPUT_DIR / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {abs_url('/sitemap.xml')}\n", encoding="utf-8")
    
    urls = [abs_url("/index.html"), abs_url("/finance.html"), abs_url("/ai_tools.html"), abs_url("/about.html"), abs_url("/disclaimer.html"), abs_url("/privacy.html")]
    urls += [abs_url(f"/assets/{a['slug']}.html") for a in results]
    urls += [abs_url(f"/ai/{safe_slug(t)}.html") for t in AI_TOOLS]
    
    sitemap = ["<?xml version='1.0' encoding='UTF-8'?>", "<urlset xmlns='http://www.sitemaps.org/schemas/sitemap/0.9'>"]
    for url in urls: sitemap.append(f"  <url><loc>{html.escape(url)}</loc></url>")
    sitemap.append("</urlset>")
    (OUTPUT_DIR / "sitemap.xml").write_text("\n".join(sitemap), encoding="utf-8")

    print(f"✅ Build Completed: {len(results)} assets | {time.time()-start_time:.1f}s")

if __name__ == "__main__":
    main()
