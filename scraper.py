import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

def get_recent_news(company_name):
    """使用 Google News RSS 搜尋企業近期新聞 (限定上個月)"""
    try:
        # 計算上個月的起訖日期
        today = datetime.today()
        first_day_current = today.replace(day=1)
        last_day_prev = first_day_current - timedelta(days=1)
        first_day_prev = last_day_prev.replace(day=1)
        
        target_year = first_day_prev.year
        target_month = first_day_prev.month
        
        after_str = first_day_prev.strftime("%Y-%m-%d")
        before_str = first_day_current.strftime("%Y-%m-%d")
        
        # 使用 Google News RSS 搜尋，加入製造業關鍵字以及日期限制
        query = f'"{company_name}" (fasteners OR manufacturing) after:{after_str} before:{before_str}'
        url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        root = ET.fromstring(response.text)
        items = root.findall('.//item')
        
        results = []
        for item in items:
            # 如果已經取滿 3 則，就停止
            if len(results) >= 3:
                break
                
            title = item.find('title').text if item.find('title') is not None else ''
            pub_date = item.find('pubDate').text if item.find('pubDate') is not None else '近期'
            source = item.find('source').text if item.find('source') is not None else 'Google News'
            
            # 解析時間並嚴格過濾「非上個月」的新聞
            try:
                # Format: Tue, 15 Mar 2026 12:00:00 GMT
                dt = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %Z")
                if dt.year != target_year or dt.month != target_month:
                    continue  # 不屬於上個月，跳過
                pub_date = dt.strftime("%Y-%m-%d")
            except:
                # 若無法解析時間，為了確保時間準確性，選擇跳過
                continue
                
            results.append(f"- [{pub_date}] {title} (來源: {source})")
            
        return "\n".join(results) if results else "無近期重大新聞。"
        
    except Exception as e:
        print(f"[{company_name}] 搜尋發生錯誤: {e}")
        return "搜尋失敗。"
