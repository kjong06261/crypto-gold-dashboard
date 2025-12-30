import yfinance as yf
import re

# ==========================================
# 1. 종목 리스트 설정
# ==========================================
nasdaq_tickers = ['NVDA', 'AAPL', 'MSFT', 'AMZN', 'TSLA', 'GOOGL', 'META', 'AMD', 'NFLX', 'INTC']
coin_tickers = ['BTC-USD', 'ETH-USD', 'SOL-USD', 'XRP-USD', 'DOGE-USD', 'ADA-USD']
dividend_tickers = ['O', 'SCHD', 'JEPI', 'JEPQ', 'VICI', 'MAIN', 'T', 'VZ']

# ==========================================
# 2. 데이터 생성 함수들 (HTML 구조에 맞춤)
# ==========================================

# [A] 코인/배당주용: 카드(Card) 디자인 생성
def make_card_html(symbol):
    try:
        t = yf.Ticker(symbol)
        data = t.history(period="2d")
        if len(data) < 2: return ""
        price = data['Close'].iloc[-1]
        prev = data['Close'].iloc[-2]
        change = ((price - prev) / prev) * 100
        
        cls = "up" if change >= 0 else "down"
        sign = "+" if change >= 0 else ""
        name = symbol.replace("-USD", "")
        
        # 대표님이 주신 HTML의 card, name, price, pct 클래스 사용
        return f"""
        <div class="card">
            <div class="card-header">
                <span class="symbol">{name}</span>
                <span class="pct {cls}">{sign}{change:.2f}%</span>
            </div>
            <div class="price">${price:,.2f}</div>
        </div>"""
    except: return ""

# [B] 나스닥용: 테이블 행(Table Row) 생성 (대표님 index.html은 표 형식임)
def make_table_row(symbol):
    try:
        t = yf.Ticker(symbol)
        data = t.history(period="2d")
        if len(data) < 2: return ""
        price = data['Close'].iloc[-1]
        prev = data['Close'].iloc[-2]
        change = ((price - prev) / prev) * 100
        
        cls = "up" if change >= 0 else "down"
        sign = "+" if change >= 0 else ""
        signal = "STRONG BUY" if change > 1 else ("SELL" if change < -1 else "HOLD")
        
        # 대표님 index.html의 table 구조 (tr, td) 사용
        return f"""
        <tr>
            <td>{symbol}</td>
            <td>{t.info.get('shortName', symbol)}</td>
            <td>${price:,.2f}</td>
            <td class="{cls}">{sign}{change:.2f}%</td>
            <td>{signal}</td>
        </tr>"""
    except: return ""

# [C] 단순 가격 가져오기 (QQQ, VIX용)
def get_simple_price(symbol):
    try:
        t = yf.Ticker(symbol)
        price = t.history(period="1d")['Close'].iloc[-1]
        return f"${price:,.2f}"
    except: return "Error"

# ==========================================
# 3. 파일 업데이트 엔진 (Regex로 핀셋 교체)
# ==========================================
def inject_html(filename, target_id, new_content):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            html = f.read()
        
        # id="타겟" 태그의 내부 내용만 교체하는 정규식
        # <태그 id="target"> (여기만바꿈) </태그>
        pattern = f'(id="{target_id}"[^>]*>)(.*?)(</)'
        
        import re
        if re.search(pattern, html, re.DOTALL):
            updated_html = re.sub(pattern, f'\\1{new_content}\\3', html, flags=re.DOTALL)
            with open(filename, "w", encoding="utf-8") as f:
                f.write(updated_html)
            print(f"✅ {filename} ({target_id}) 업데이트 성공")
        else:
            print(f"❌ {filename}에서 id='{target_id}'를 찾을 수 없음")
            
    except FileNotFoundError:
        print(f"⚠️ {filename} 파일 없음")

# ==========================================
# 4. 실행 (메인 로직)
# ==========================================
if __name__ == "__main__":
    
    # 1. 코인 업데이트 (coin.html -> id="coin-grid")
    coin_html = "".join([make_card_html(s) for s in coin_tickers])
    inject_html("coin.html", "coin-grid", coin_html)
    
    # 2. 배당주 업데이트 (dividend.html -> id="dividend-grid")
    div_html = "".join([make_card_html(s) for s in dividend_tickers])
    inject_html("dividend.html", "dividend-grid", div_html)
    
    # 3. 나스닥 테이블 업데이트 (index.html -> id="nasdaq-table")
    nasdaq_html = "".join([make_table_row(s) for s in nasdaq_tickers])
    inject_html("index.html", "nasdaq-table", nasdaq_html)
    
    # 4. 나스닥 상단 지표 업데이트 (index.html -> id="qqq-price", id="vix-index")
    inject_html("index.html", "qqq-price", get_simple_price("QQQ"))
    inject_html("index.html", "vix-index", get_simple_price("^VIX"))
    inject_html("index.html", "sentiment-score", "GREED (75)") # 센티먼트는 임시값
