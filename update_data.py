import yfinance as yf
import datetime, pytz, os, re, time, html, json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# =========================================================
# 0) 경로 및 환경 설정
# =========================================================
OUTPUT_DIR = Path("./docs")
ASSETS_DIR = OUTPUT_DIR / "assets"
API_DIR = OUTPUT_DIR / "api"
CACHE_DIR = OUTPUT_DIR / ".cache"
for d in [OUTPUT_DIR, ASSETS_DIR, API_DIR, CACHE_DIR]:
    d.mkdir(parents=True, exist_ok=True)

SITE_NAME = "US Dividend Pro"
BASE_URL = os.getenv("BASE_URL", "").strip().rstrip("/")
if BASE_URL and not BASE_URL.startswith("/"):
    BASE_URL = "/" + BASE_URL

SITE_URL = os.getenv("SITE_URL", "").rstrip("/")

def u(path: str) -> str:
    if not path.startswith("/"): path = "/" + path
    return f"{BASE_URL}{path}"

def abs_url(path: str) -> str:
    path_clean = u(path)
    return (SITE_URL + path_clean) if SITE_URL else path_clean

def safe_slug(s: str) -> str:
    return re.sub(r"[^a-z0-9_-]+", "_", s).lower()

def atomic_write(path: Path, text: str):
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)

def write_if_changed(path: Path, text: str):
    if path.exists():
        try:
            if path.read_text(encoding="utf-8") == text: return
        except: pass
    atomic_write(path, text)

# =========================================================
# 1) 티커 데이터 (나스닥, AI, 코인, 배당주 리스트)
# =========================================================
TICKERS = {
    "crypto": [
        "BTC-USD", "ETH-USD", "SOL-USD", "XRP-USD", "DOGE-USD", "ADA-USD", "DOT-USD", "LINK-USD", "AVAX-USD", "SHIB-USD"
    ],
    "ai_semiconductor": [
        "NVDA", "AMD", "AVGO", "ARM", "TSM", "ASML", "AMAT", "LRCX", "KLAC", "MRVL", 
        "MU", "INTC", "SMCI", "SNPS", "CDNS", "ANSS", "MCHP", "TXN", "ADI", "NXPI"
    ],
    "big_tech": [
        "AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "NFLX", "ADBE", "ORCL", "CRM"
    ],
    "dividend_pro": [
        "O", "SCHD", "JEPI", "JEPQ", "VICI", "MAIN", "STAG", "ADC", "MO", "T", "VZ", "JNJ", "PG", "KO", "PEP"
    ],
    "nasdaq_100_extra": [
        "AMGN", "SBUX", "MDLZ", "ISRG", "GILD", "BKNG", "VRTX", "REGN", "ADP", "PANW"
    ]
}
ALL_TICKERS = sorted(set(sum(TICKERS.values(), [])))

def get_category(ticker: str) -> str:
    for cat, arr in TICKERS.items():
        if ticker in arr: return cat
    return "other"

# =========================================================
# 2) UI & 무적 JS (중괄호 탈출 완벽 처리)
# =========================================================
BASE_CSS = """
:root{--bg:#05070a;--panel:#11141b;--border:#1e222d;--text:#d1d4dc;--muted:#8b949e;--link:#58a6ff;--success:#00d084;--danger:#ff3366;}
body{margin:0;background:var(--bg);color:var(--text);font-family:system-ui,sans-serif;line-height:1.6;}
.container{max-width:1200px;margin:0 auto;padding:20px;}
.nav{display:flex;gap:12px;padding:15px 5%;background:#0b0e14;border-bottom:1px solid var(--border);position:sticky;top:0;z-index:100;align-items:center;flex-wrap:wrap;}
.nav strong{color:#fff;margin-right:auto;font-size:1.1rem}
.nav a{color:var(--link);text-decoration:none;font-weight:700;padding:8px 14px;background:#1e222d;border-radius:8px;font-size:0.9rem;}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:15px;margin-top:20px;}
.card{background:var(--panel);border:1px solid var(--border);padding:20px;border-radius:14px;text-decoration:none;color:inherit;display:block;transition:0.2s;}
.card:hover{border-color:var(--link);transform:translateY(-3px);box-shadow:0 10px 20px rgba(88,166,255,0.1);}
.hero{text-align:center;padding:60px 20px;background:rgba(88,166,255,0.03);border-radius:16px;margin:20px 0;}
footer{text-align:center;padding:40px;margin-top:60px;font-size:0.8rem;color:var(--muted);border-top:1px solid var(--border);}
"""

site_js = json.dumps(SITE_NAME)
base_js = json.dumps(BASE_URL)

DYNAMIC_JS = f"""
<script>
(function() {{
  const RAW_BASE = {base_js};
  const BASE = (!RAW_BASE || RAW_BASE === "/") ? "" : RAW_BASE.replace(/\\/+$/g, "");
  const SITE_NAME = {site_js};

  const ABS = (p) => window.location.origin + BASE + (p.startsWith("/") ? p : ("/" + p));
  const URLS = [ ABS("/api/assets.json"), ABS("api/assets.json"), "./api/assets.json", "../api/assets.json" ];

  async function fetchFirstOk(urls) {{
    for (const url of urls) {{
      try {{
        const res = await fetch(url, {{ cache: "no-store" }});
        if (res.ok) return res;
      }} catch(e) {{}}
    }}
    throw new Error("Load Failed");
  }}

  async function init() {{
    try {{
      const res = await fetchFirstOk(URLS);
      const data = await res.json();
      
      const params = new URLSearchParams(window.location.search);
      const ticker = params.get("t");

      if (ticker) {{
        renderDetail(data, ticker.trim().toUpperCase());
      }} else if (document.getElementById("grid")) {{
        renderGrid(data);
      }}
    }} catch (e) {{
      console.error(e);
      const c = document.getElementById("content");
      if (c) {{ c.innerHTML = "<h1>Data Load Failed</h1>"; }}
    }}
  }}

  function renderGrid(data) {{
    const grid = document.getElementById("grid");
    grid.innerHTML = data.map(a => {{
      const t = (a.t || "UNKNOWN").toString();
      const href = ABS("/assets/index.html") + "?t=" + encodeURIComponent(t);
      return `<a class="card" href="${{href}}">
          <strong>${{t}}</strong>
          <div style="font-size:1.5rem;font-weight:800;margin:5px 0;">$${{Number(a.p||0).toLocaleString()}}</div>
          <div style="color:${{(a.c||0)>=0?"var(--success)":"var(--danger)"}};font-weight:700;">
            ${{(a.c||0)>=0?"+":""}}${{Number(a.c||0).toFixed(2)}}%
          </div>
        </a>`;
    }}).join("");
  }}

  function renderDetail(data, ticker) {{
    const asset = data.find(x => String(x.t).toUpperCase() === ticker);
    const content = document.getElementById("content");
    if (!asset) {{ 
        content.innerHTML = "<h1>Asset (" + ticker + ") Not Found</h1>"; 
        return; 
    }}

    document.title = asset.t + " | " + SITE_NAME;
    const color = (asset.c||0) >= 0 ? "var(--success)" : "var(--danger)";

    content.innerHTML = `<div class="hero">
        <h1>${{asset.t}}</h1>
        <div style="font-size:4rem;font-weight:900;color:${{color}}">
          $${{Number(asset.p || 0).toLocaleString()}}
        </div>
        <div style="font-size:1.5rem;font-weight:700;color:${{color}}">${{(asset.c||0)>=0?"+":""}}${{Number(asset.c||0).toFixed(2)}}%</div>
        <p style="margin-top:20px;color:var(--muted);">Vol: ${{Number(asset.v || 0).toLocaleString()}} | Cat: ${{String(asset.cat || "").toUpperCase()}}</p>
        <a href="${{ABS("/finance.html")}}" style="color:var(--link);text-decoration:none;font-weight:800;">← Back to Terminal</a>
      </div>`;
  }}
  window.addEventListener("load", init);
}})();
</script>
"""

def wrap_page(title, body, last_et, use_js=False):
    site = html.escape(SITE_NAME)
    js = DYNAMIC_JS if use_js else ""
    nav = f"<div class='nav'><strong>{site}</strong><a href='{u('/index.html')}'>Home</a><a href='{u('/finance.html')}'>Terminal</a></div>"
    return f"<!DOCTYPE html><html lang='en'><head><meta charset='UTF-8'><meta name='viewport' content='width=device-width,initial-scale=1.0'><title>{title} | {site}</title><style>{BASE_CSS}</style>{js}</head><body>{nav}<div class='container' id='content'>{body}</div><footer>© 2025 {site} | Updated: {last_et}</footer></body></html>"

# =========================================================
# 3) 데이터 엔진
# =========================================================
def fetch_data(t):
    cache_file = CACHE_DIR / f"{safe_slug(t)}.json"
    if cache_file.exists() and time.time() - cache_file.stat().st_mtime < 10 * 60:
        try: return json.loads(cache_file.read_text(encoding="utf-8"))
        except: pass

    try:
        s = yf.Ticker(t)
        h = s.history(period="2d", auto_adjust=False)
        if h.empty or len(h) < 2: return None
        p, prev = float(h['Close'].iloc[-1]), float(h['Close'].iloc[-2])
        if prev == 0: return None
        res = {"t": t, "p": round(p, 2), "c": round(((p-prev)/prev)*100, 2), "v": int(h['Volume'].iloc[-1]), "cat": get_category(t), "ts": time.time()}
        atomic_write(cache_file, json.dumps(res, ensure_ascii=False))
        return res
    except: return None

def main():
    start_time = time.time()
    now_et = datetime.datetime.now(pytz.timezone("US/Eastern")).strftime("%Y-%m-%d %H:%M %Z")
    
    results = []
    with ThreadPoolExecutor(max_workers=5) as ex:
        futures = [ex.submit(fetch_data, t) for t in ALL_TICKERS]
        for f in as_completed(futures):
            r = f.result()
            if r: results.append(r)
    
    if len(results) < 5: return

    results.sort(key=lambda x: x['t'])
    write_if_changed(API_DIR / "assets.json", json.dumps(results, ensure_ascii=False, indent=2))
    write_if_changed(OUTPUT_DIR / "index.html", wrap_page("Home", "<div class='hero'><h1>US Dividend Pro</h1><p>Static & JSON Based Terminal</p></div>", now_et))
    write_if_changed(OUTPUT_DIR / "finance.html", wrap_page("Terminal", "<h1>Market Terminal</h1><div id='grid' class='grid'>Loading...</div>", now_et, use_js=True))
    write_if_changed(ASSETS_DIR / "index.html", wrap_page("Analysis", "Syncing data...", now_et, use_js=True))

    write_if_changed(OUTPUT_DIR / "robots.txt", f"User-agent: *\nAllow: /\nSitemap: {abs_url('/sitemap.xml')}\n")
    sitemap = ["<?xml version='1.0' encoding='UTF-8'?>", "<urlset xmlns='http://www.sitemaps.org/schemas/sitemap/0.9'>"]
    for url in [u("/index.html"), u("/finance.html"), u("/assets/index.html")]:
        sitemap.append(f"  <url><loc>{html.escape(abs_url(url))}</loc></url>")
    sitemap.append("</urlset>")
    write_if_changed(OUTPUT_DIR / "sitemap.xml", "\n".join(sitemap))

    print(f"✅ Success: {len(results)} assets")

if __name__ == "__main__":
    main()
