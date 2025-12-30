import os
import re
from datetime import datetime

# 1. 각 섹터별 데이터 (대표님이 관리하시는 종목들)
crypto_data = """
    <div class="card"><span class="name">BTC</span><span class="price">$96,432</span><span class="pct up">+2.5%</span></div>
    <div class="card"><span class="name">ETH</span><span class="price">$3,542</span><span class="pct down">-1.2%</span></div>
    <div class="card"><span class="name">SOL</span><span class="price">$192</span><span class="pct up">+5.8%</span></div>
"""

nasdaq_data = """
    <tr><td>NVDA</td><td>NVIDIA</td><td>$495.22</td><td style="color:#39d353">+4.8%</td><td>STRONG BUY</td></tr>
    <tr><td>TSLA</td><td>Tesla</td><td>$248.48</td><td style="color:#39d353">+2.5%</td><td>HOLD</td></tr>
"""

dividend_data = """
    <tr><td>O</td><td>Realty Income</td><td>$54.20</td><td>5.8%</td><td>Monthly</td></tr>
    <tr><td>SCHD</td><td>Schwab Dividend</td><td>$78.15</td><td>3.4%</td><td>Quarterly</td></tr>
"""

def inject_data(filename, target_id, new_html):
    if not os.path.exists(filename): return
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()
    
    # id="이름" 뒤에 오는 내용을 교체하는 정규식
    pattern = f'(id="{target_id}">)(.*?)(?=</tbody>|</div>)'
    updated = re.sub(pattern, f'\\1{new_html}', content, flags=re.DOTALL)
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(updated)

# 실행: 3개 파일 동시 업데이트
try:
    inject_data("coin.html", "coin-grid", crypto_data)
    inject_data("nasdaq.html", "nasdaq-table", nasdaq_data)
    inject_data("dividend.html", "dividend-table", dividend_data)
    print(f"{datetime.now()} - 모든 데이터 주입 완료")
except Exception as e:
    print(f"오류 발생: {e}")
