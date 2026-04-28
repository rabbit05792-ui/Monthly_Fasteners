from duckduckgo_search import DDGS
import time

CATEGORIES = {
    "汽車工業": {
        "sites": ["autonews.com", "reuters.com/business/autos-transportation", "electrek.co"],
        "keywords": '("L3" OR "L4" OR "智駕" OR "固態電池" OR "設廠")'
    },
    "重型機具": {
        "sites": ["engineering.com", "khl.com", "technologyreview.com"],
        "keywords": '("電氣化挖土機" OR "3D列印" OR "3D printing" OR "氫能" OR "hydrogen")'
    },
    "能源產業": {
        "sites": ["iea.org", "bnef.com", "energy-storage.news"],
        "keywords": '("小型模組化反應爐" OR "SMR" OR "虛擬電廠" OR "VPP" OR "離網")'
    },
    "航太與軍工": {
        "sites": ["defensenews.com", "aviationweek.com", "spacenews.com"],
        "keywords": '("無人機" OR "drone" OR "低軌衛星" OR "不對稱作戰" OR "預算")'
    },
    "投資與展望": {
        "sites": ["ft.com", "barrons.com", "clarivate.com"],
        "keywords": '("資本支出" OR "CAPEX" OR "併購" OR "M&A" OR "專利")'
    }
}

def search_industry_news(timelimit='w'):
    """
    使用 DuckDuckGo 搜尋每日工業新聞 (預設過去一週 'w'，因為有些冷門網站並非每天更新大新聞)
    回傳整理好的文字報告，供 LLM 分析
    """
    ddgs = DDGS()
    raw_data = []
    
    for category, info in CATEGORIES.items():
        sites_query = " OR ".join([f"site:{site}" for site in info['sites']])
        query = f"{info['keywords']} ({sites_query})"
        
        raw_data.append(f"=== {category} ===")
        print(f"🔍 正在搜尋 [{category}] ...")
        
        try:
            # 搜尋最多前 5 筆，確保來源權威性
            results = ddgs.text(query, timelimit=timelimit, max_results=5)
            if not results:
                raw_data.append("過去一週內無相關重大新聞。")
                continue
                
            for res in results:
                title = res.get('title', '')
                snippet = res.get('body', '')
                link = res.get('href', '')
                raw_data.append(f"- 標題: {title}\n  內容摘要: {snippet}\n  來源: {link}")
                
            # 加上短暫延遲避免被 DuckDuckGo 阻擋
            time.sleep(2)
            
        except Exception as e:
            raw_data.append(f"搜尋發生錯誤: {str(e)}")
            
        raw_data.append("\n")
        
    return "\n".join(raw_data)

if __name__ == "__main__":
    # 簡單測試用
    print(search_industry_news())
