import yfinance as yf
from datetime import datetime

# 종목 리스트 (에러 방지를 위해 간단하게 구성)
tickers = {
    'IBIT': '비트코인 ETF',
    'ETHE': '이더리움 ETF',
    'GLD': '금 현물',
    'SLV': '은 현물',
    'QQQ': '나스닥 100',
    'SOXX': '반도체'
}

def get_data():
    results = []
    for symbol, name in tickers.items():
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period='2d') # 2일치를 가져와야 어제/오늘 비교 가능
            if len(data) >= 2:
                price = round(data['Close'].iloc[-1], 2)
                prev_price = data['Close'].iloc[-2]
                change = round(((price - prev_price) / prev_price) * 100, 2)
                results.append({'name': name, 'price': price, 'change': change})
        except:
            continue
    return results

data_list = get_data()
now = datetime.now().strftime('%Y-%m-%d %H:%M')

html_content = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>투자 대시보드</title>
    <style>
        body {{ background-color: #121212; color: white; font-family: sans-serif; text-align: center; padding: 20px; }}
        .header {{ color: #00ff88; font-size: 1.5rem; }}
        .container {{ display: flex; flex-wrap: wrap; justify-content: center; gap: 10px; margin-top: 20px; }}
        .card {{ background: #1e1e1e; border-radius: 10px; padding: 15px; width: 130px; border: 1px solid #333; }}
        .up {{ color: #ff4d4d; }} .down {{ color: #4d94ff; }}
    </style>
</head>
<body>
    <div class="header">💰 실시간 투자 대시보드</div>
    <div style="color:#888;">{now} 업데이트</div>
    <div class="container">
"""

for item in data_list:
    color = "up" if item['change'] >= 0 else "down"
    plus = "+" if item['change'] >= 0 else ""
    html_content += f"""
        <div class="card">
            <div style="font-size:0.8rem; color:#bbb;">{item['name']}</div>
            <div style="font-size:1.1rem; font-weight:bold;">${item['price']}</div>
            <div class="{color}">{plus}{item['change']}%</div>
        </div>
    """

html_content += "</div></body></html>"

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html_content)
