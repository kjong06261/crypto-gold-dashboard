import os
import re

# 1. 삽입할 데이터 정의
nasdaq_html_data = """
    <tr><td style="color:#ffa657; font-weight:bold;">NVDA</td><td>NVIDIA Corp.</td><td style="color:#ffffff;">$495.22</td><td style="color:#39d353;">+4.8%</td><td style="color:#00ff88;">STRONG BUY</td></tr>
    <tr><td style="color:#ffa657; font-weight:bold;">TSLA</td><td>Tesla, Inc.</td><td style="color:#ffffff;">$248.48</td><td style="color:#39d353;">+2.5%</td><td style="color:#58a6ff;">HOLD</td></tr>
    <tr><td style="color:#ffa657; font-weight:bold;">AAPL</td><td>Apple Inc.</td><td style="color:#ffffff;">$192.53</td><td style="color:#39d353;">+1.2%</td><td style="color:#00ff88;">BUY</td></tr>
"""

coin_html_data = """
    <p>> BTC DOMINANCE: <span style="color:#39d353;">52.4%</span></p>
    <p>> MARKET SENTIMENT: <span style="color:#58a6ff;">GREED (68)</span></p>
    <p>> SYSTEM STATUS: <span style="color:#39d353;">BULLISH</span></p>
"""

def update_file(filename, target_id, new_data):
    if not os.path.exists(filename):
        return
    
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 정규표현식을 사용하여 id가 지정된 태그 내부를 교체합니다.
    pattern = f'id="{target_id}">(.*?)</tbody>' if "table" in target_id else f'id="{target_id}">(.*?)</div>'
    replacement = f'id="{target_id}">{new_data}{"</tbody>" if "table" in target_id else "</div>"}'
    
    updated_content = re.sub(f'id="{target_id}">.*?(?=<\/tbody>|<\/div>)', f'id="{target_id}">{new_data}', content, flags=re.DOTALL)
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(updated_content)

# 2. 각 파일에 데이터 주입
try:
    update_file("nasdaq.html", "nasdaq-table", nasdaq_html_data)
    update_file("coin.html", "terminal", coin_html_data)
    print("데이터 업데이트 완료")
except Exception as e:
    print(f"오류 발생: {e}")
