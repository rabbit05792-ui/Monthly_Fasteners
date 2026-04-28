import requests
import xml.etree.ElementTree as ET
from datetime import datetime

def get_recent_news(company_name):
    """使用 Google News RSS 搜尋企業近期新聞"""
    try:
        # 使用 Google News RSS 搜尋，加入製造業關鍵字
        query = f'"{company_name}" (fasteners OR manufacturing)'
        url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        root = ET.fromstring(response.text)
        items = root.findall('.//item')
        
        results = []
        # 只取前 3 則新聞
        for item in items[:3]:
            title = item.find('title').text if item.find('title') is not None else ''
            pub_date = item.find('pubDate').text if item.find('pubDate') is not None else '近期'
            source = item.find('source').text if item.find('source') is not None else 'Google News'
            
            # 將 pub_date 簡化
            try:
                # Format: Tue, 15 Mar 2026 12:00:00 GMT
                dt = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %Z")
                pub_date = dt.strftime("%Y-%m-%d")
            except:
                pass
                
            results.append(f"- [{pub_date}] {title} (來源: {source})")
            
        return "\n".join(results) if results else "無近期重大新聞。"
        
    except Exception as e:
        print(f"[{company_name}] 搜尋發生錯誤: {e}")
        return "搜尋失敗。"
