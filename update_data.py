name: Update Asset Data

on:
  schedule:
    - cron: '0 * * * *'
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    # 권한 설정이 확실하게 먹히도록 코드 레벨에서도 한 번 더 박아줍니다
    permissions:
      contents: write
      
    steps:
      - name: Checkout code
        uses: actions/checkout@v4 # 최신 버전 v4로 교체

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'

      - name: Install dependencies
        run: pip install yfinance

      - name: Run update script
        run: python update_data.py

      - name: Commit and Push changes
        run: |
          git config --global user.name "github-actions[bot]"
          git config --global user.email "github-actions[bot]@users.noreply.github.com"
          git add -A
          git commit -m "Automated update: index.html & sitemap.xml" || echo "Nothing changed"
          git push
