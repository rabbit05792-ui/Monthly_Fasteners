import requests
import xml.etree.ElementTree as ET
import time

CATEGORIES = {
    "汽車工業": {
        "sites": ["autonews.com", "reuters.com", "electrek.co"],
        "keywords": '("L3" OR "L4" OR "autonomous driving" OR "solid-state battery" OR "new plant" OR "factory")'
    },
    "重型機具": {
        "sites": ["engineering.com", "khl.com", "technologyreview.com"],
        "keywords": '("electric excavator" OR "3D printing" OR "hydrogen" OR "heavy machinery")'
    },
    "能源產業": {
        "sites": ["iea.org", "bnef.com", "energy-storage.news"],
        "keywords": '("SMR" OR "small modular reactor" OR "VPP" OR "virtual power plant" OR "off-grid")'
    },
    "航太與軍工": {
        "sites": ["defensenews.com", "aviationweek.com", "spacenews.com"],
        "keywords": '("drone swarm" OR "UAV" OR "LEO" OR "low earth orbit" OR "asymmetric warfare" OR "defense budget")'
    },
    "投資與展望": {
        "sites": ["ft.com", "barrons.com", "clarivate.com"],
        "keywords": '("CAPEX" OR "capital expenditure" OR "M&A" OR "merger" OR "patent" OR "innovation")'
    }
}

def search_industry_news(timelimit='7d'):
    """
    使用 Google News RSS 搜尋每日工業新聞 (過去 7 天)
    回傳整理好的文字報告，供 LLM 分析
    """
    raw_data = []
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    for category, info in CATEGORIES.items():
        sites_query = " OR ".join([f"site:{site}" for site in info['sites']])
        # Google News RSS query 格式: "keyword" (site:A OR site:B) when:7d
        query = f'{info["keywords"]} ({sites_query}) when:{timelimit}'
        
        raw_data.append(f"=== {category} ===")
        print(f"正在搜尋 [{category}] ...")
        
        url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            root = ET.fromstring(response.text)
            items = root.findall('.//item')
            
            if not items:
                raw_data.append("過去一週內無相關重大新聞。")
                continue
                
            # 取前 5 篇即可
            for item in items[:5]:
                title = item.find('title').text if item.find('title') is not None else ''
                pub_date = item.find('pubDate').text if item.find('pubDate') is not None else ''
                source = item.find('source').text if item.find('source') is not None else ''
                link = item.find('link').text if item.find('link') is not None else ''
                
                raw_data.append(f"- 標題: {title}\n  發布時間: {pub_date}\n  來源: {source} ({link})")
                
            time.sleep(1)
            
        except Exception as e:
            raw_data.append(f"搜尋發生錯誤: {str(e)}")
            
        raw_data.append("\n")
        
    return "\n".join(raw_data)

if __name__ == "__main__":
    # 簡單測試用
    print(search_industry_news())
