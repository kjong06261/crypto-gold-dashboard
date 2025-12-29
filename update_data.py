import yfinance as yf
from datetime import datetime

try:
    tickers = {'IBIT': '비트코인 ETF', 'GLD': '금 현물', 'QQQ': '나스닥 100'}
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    html = f"<html><body style='background:#121212;color:white;text-align:center;'><h1>💰 실시간 전광판</h1><p>{now}</p><div style='display:flex;justify-content:center;gap:20px;'>"
    
    for s, n in tickers.items():
        p = yf.Ticker(s).history(period='1d')['Close'].iloc[-1]
        html += f"<div style='border:1px solid #333;padding:20px;'><h3>{n}</h3><p>${round(p, 2)}</p></div>"
    
    html += "</div></body></html>"
    
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)
except Exception as e:
    print(f"Error: {e}")
