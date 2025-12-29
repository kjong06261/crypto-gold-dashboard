import yfinance as yf
import pandas as pd
from datetime import datetime

# MZ 타겟 종목 리스트
tickers = {
    '비트코인 ETF (IBIT)': 'IBIT',
    '이더리움 ETF (ETHE)': 'ETHE',
    '금 현물 (GLD)': 'GLD',
    '은 현물 (SLV)': 'SLV',
    '나스닥 100 (QQQ)': 'QQQ',
    '반도체 대장 (SOXX)': 'SOXX'
}

def get_data():
    results = []
    for name, symbol in tickers.items():
        ticker = yf.Ticker(symbol)
        data = ticker.history(period='1d')
        if not data.empty:
            price = round(data['Close'].iloc[-1], 2)
            change = round(((data['Close'].iloc[-1] - data['Open'].iloc[-1]) / data['Open'].iloc[-1]) * 100, 2)
            results.append({'name': name, 'price': price, 'change': change})
    return results

data_list = get_data()
now = datetime.now().strftime('%Y-%m-%d %H:%M')

# 깔끔한 다크모드 대시보드
html_content = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>코인/금 실시간 대시보드</title>
    <style>
        body {{ background-color: #121212; color: white; font-family: sans-serif; text-align: center; margin: 0; padding: 20px; }}
        .header {{ color: #00ff88; font-size: 1.5rem; margin-bottom: 10px; }}
        .time {{ color: #888; font-size: 0.9rem; margin-bottom: 30px; }}
        .container {{ display: flex; flex-wrap: wrap; justify-content: center; gap: 15px; }}
        .card {{ background: #1e1e1e; border-radius: 12px; padding: 20px; width: 140px; border: 1px solid #333; }}
        .name {{ font-size: 0.9rem; margin-bottom: 10px; color: #bbb; }}
        .price {{ font-size: 1.2rem; font-weight: bold; margin-bottom: 5px; }}
        .up {{ color: #ff4d4d; }} .down {{ color: #4d94ff; }}
    </style>
</head>
<body>
    <div class="header">💰 투자 실시간 대시보드</div>
    <div class="time">마지막 업데이트: {now} (KST)</div>
    <div class="container">
"""

for item in data_list:
    color_class = "up" if item['change'] >= 0 else "down"
    plus_sign = "+" if item['change'] >= 0 else ""
    html_content += f"""
        <div class="card">
            <div class="name">{item['name']}</div>
            <div class="price">${item['price']}</div>
            <div class="change {color_class}">{plus_sign}{item['change']}%</div>
        </div>
    """

html_content += """
    </div>
    <div style="margin-top:50px; color:#555; font-size:0.8rem;">매시간 자동 업데이트 중</div>
</body>
</html>
"""

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html_content)
