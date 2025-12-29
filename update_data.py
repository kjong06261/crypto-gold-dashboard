import yfinance as yf
from datetime import datetime

# 종목 설정 (비트코인 ETF, 금, 나스닥)
tickers = {'IBIT': '비트코인 ETF', 'GLD': '금 현물', 'QQQ': '나스닥 100'}

now = datetime.now().strftime('%Y-%m-%d %H:%M')
html_content = f"""
<!DOCTYPE html>
<html lang="ko">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>실시간 대시보드</title>
<style>
    body {{ background: #121212; color: white; text-align: center; font-family: sans-serif; }}
    .card-container {{ display: flex; justify-content: center; gap: 20px; margin-top: 30px; }}
    .card {{ background: #1e1e1e; padding: 20px; border-radius: 10px; border: 1px solid #333; width: 150px; }}
    .price {{ font-size: 1.5rem; font-weight: bold; color: #00ff88; }}
</style></head>
<body>
    <h1>💰 투자 실시간 전광판</h1>
    <p style="color: #888;">{now} 업데이트 (매시간 자동)</p>
    <div class="card-container">
"""

for symbol, name in tickers.items():
    try:
        data = yf.Ticker(symbol).history(period='1d')
        price = round(data['Close'].iloc[-1], 2)
        html_content += f"<div class='card'><div>{name}</div><div class='price'>${price}</div></div>"
    except Exception as e:
        print(f"Error {symbol}: {e}")

html_content += "</div></body></html>"

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html_content)
