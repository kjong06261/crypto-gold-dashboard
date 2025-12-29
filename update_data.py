# (중략... 위에는 기존 시세 데이터 코드)

if __name__ == "__main__":
    # 1. 인덱스 파일 생성
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(get_data())

    # 2. 지도 파일 생성 (이게 꼭 있어야 합니다!)
    sitemap_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://coin.us-dividend-pro.com/</loc>
        <lastmod>{datetime.now().strftime('%Y-%m-%d')}</lastmod>
        <changefreq>hourly</changefreq>
        <priority>1.0</priority>
    </url>
</urlset>"""
    with open('sitemap.xml', 'w', encoding='utf-8') as f:
        f.write(sitemap_content)
