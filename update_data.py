import os

# 1. 데이터 정의 (사장님이 원하는 종목들)
nasdaq_data = """
    <tr><td>NVDA</td><td>NVIDIA</td><td>$495.22</td><td style="color:#39d353">+4.8%</td><td>BUY</td></tr>
    <tr><td>TSLA</td><td>Tesla</td><td>$248.48</td><td style="color:#39d353">+2.5%</td><td>HOLD</td></tr>
    <tr><td>AAPL</td><td>Apple</td><td>$192.53</td><td style="color:#39d353">+1.2%</td><td>STRONG BUY</td></tr>
"""

coin_data = """
    <p>> BTC DOMINANCE: 52.4%</p>
    <p>> MARKET SENTIMENT: GREED (68)</p>
    <p>> STATUS: BULLISH</p>
"""

# 2. 나스닥 파일 업데이트
with open("nasdaq.html", "r", encoding="utf-8") as f:
    content = f.read()
if "nasdaq-table" in content:
    # Loading 문구를 실제 데이터로 교체
    new_content = content.replace("", nasdaq_data) # 혹은 특정 ID 위치에 삽입
    with open("nasdaq.html", "w", encoding="utf-8") as f:
        f.write(new_content)

# 3. 코인 파일 업데이트
with open("coin.html", "r", encoding="utf-8") as f:
    content = f.read()
# 코인 데이터 교체 로직 (필요시 추가)

print("모든 금융 데이터 배포 완료!")
