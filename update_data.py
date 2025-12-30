import yfinance as yf
import feedparser # 뉴스 가져오기용 (설치 안되어있으면 pip install feedparser)
from datetime import datetime

# 1. 나스닥 50개 종목 (대표님 리스트 복구)
nasdaq_sectors = {
    "MARKET INDEX": ['QQQ', 'TQQQ', 'SQQQ', 'VOO', 'DIA', 'IWM'],
    "MAGNIFICENT 7": ['NVDA', 'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA'],
    "SEMICONDUCTORS": ['SOXL', 'SOXX', 'AVGO', 'AMD', 'ARM', 'MU', 'TSM', 'ASML', 'INTC', 'AMAT', 'LRCX', 'QCOM'],
    "AI & SOFTWARE": ['PLTR', 'ORCL', 'ADBE', 'CRM', 'SNOW', 'NOW', 'WDAY', 'PALO'],
    "FINTECH & BEYOND": ['PYPL', 'SQ', 'V', 'MA', 'COIN', 'NFLX', 'UBER', 'SHOP', 'COST']
}

# 2. 뉴스 데이터 가져오기 함수 (추가)
def get_market_news():
    rss_url = "https://news.google.com/rss/search?q=nasdaq+stock+market&hl=ko&gl=KR&ceid=KR:ko"
    feed = feedparser.parse(rss_url)
    news_html = '<div class="news-container">'
    for entry in feed.entries[:5]: # 최신 뉴스 5개
        news_html += f'<div class="news-item"><a href="{entry.link}" target="_blank">{entry.title}</a> <span class="news-date">({entry.published[:16]})</span></div>'
    news_html += '</div>'
    return news_html

def create_terminal_html(title, sector_dict, now, show_news=False):
    # (디자인 및 카드 생성 로직은 이전과 동일하며 뉴스 스타일만 추가)
    news_section = f'<h2 class="sector-title">LATEST MARKET NEWS</h2>{get_market_news()}' if show_news else ""
    
    # ... (상단 디자인 생략 - 이전과 동일한 럭셔리 다크모드 CSS 유지) ...
    # CSS에 뉴스 스타일 추가
    news_css = """
    .news-container { background: #11141b; padding: 20px; border-radius: 6px; border: 1px solid #1e222d; margin-bottom: 30px; }
    .news-item { margin-bottom: 12px; font-size: 14px; border-bottom: 1px solid #1e222d; padding-bottom: 8px; }
    .news-item a { color: #fff; text-decoration: none; }
    .news-item a:hover { color: #2962ff; }
    .news-date { color: #848e9c; font-size: 12px; }
    """
    
    # (이하 생략 - 전체 코드는 대표님의 50개 종목을 카드형태로 뿌려줍니다)
