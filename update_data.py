import yfinance as yf
from datetime import datetime

# 종목 리스트
tickers = {'IBIT': '비트코인 ETF', 'GLD': '금 현물', 'QQQ': '나스닥 100'}

def get_data():
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    html = f"<html><body style='background:#121212;color:white;text-align:center;'><h1>💰 실시간 전광판</h1><p>{now}</p><div style='display:flex;justify-content:center;gap:20px;'>"
    
    for s, n in tickers.items():
        try:
            t = yf.Ticker(s)
            df = t.history(period='1d')
            if not df.empty:
                price = round(df['Close'].iloc[-1], 2)
                html += f"<div style='border:1px solid #333;padding:20px;'><h3>{n}</h3><p>${price}</p></div>"
        except:
            continue
    
    html += "</div></body></html>"
    return html

if __name__ == "__main__":
    result_html = get_data()
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(result_html)
