# (앞부분 설정 생략 - 동일함)

def main():
    now_et = datetime.datetime.now(pytz.timezone("US/Eastern")).strftime("%Y-%m-%d %H:%M %Z")
    
    home_body = f"""
    <div class="card" style="border:2px solid var(--link); background: rgba(88,166,255,0.05);">
        <h2 style="color:var(--link);margin-top:0;">📊 Real-time Investment Analyzer</h2>
        <p style="color:var(--muted); font-size:0.9rem;">실시간 시장 지표를 기반으로 기대 수익률 및 자산 가치를 분석합니다.</p>
        <input type="number" id="p" placeholder="Entry Price ($)">
        <input type="number" id="q" placeholder="Quantity">
        <button class="tab-btn" style="background:var(--link);color:white;width:auto;" onclick="alert('Analyzed Asset Value: $'+(document.getElementById('p').value*document.getElementById('q').value).toLocaleString())">Analyze Now</button>
    </div>

    <div class="tab-menu">
        <button class="tab-btn active" onclick="openTab('ai')">AI & Tech Equity</button>
        <button class="tab-btn" onclick="openTab('nasdaq')">NASDAQ Index</button>
        <button class="tab-btn" onclick="openTab('coin')">Digital Assets</button>
        <button class="tab-btn" onclick="openTab('divi')">High-Yield Dividend</button>
        <button class="tab-btn" onclick="openTab('all')">Full Market Index ({len(ALL_TICKERS)})</button>
    </div>

    <div id="ai" class="tab-content active"><div class="ticker-grid">{make_links('AI')}</div></div>
    <div id="nasdaq" class="tab-content"><div class="ticker-grid">{make_links('NASDAQ')}</div></div>
    <div id="coin" class="tab-content"><div class="ticker-grid">{make_links('COIN')}</div></div>
    <div id="divi" class="tab-content"><div class="ticker-grid">{make_links('DIVIDEND')}</div></div>
    <div id="all" class="tab-content">
        <p style="text-align:center; color:var(--muted); font-size:0.8rem; margin-bottom:15px;">전 세계 500여 개 핵심 금융 자산에 대한 실시간 인덱스를 제공합니다.</p>
        <div class="ticker-grid">{"".join([f'<a href="{u("/assets/index.html")}?t={t}" class="ticker-link">{t}</a>' for t in ALL_TICKERS])}</div>
    </div>
    """
    # (이하 생략)
