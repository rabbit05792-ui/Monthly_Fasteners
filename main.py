import time
from scraper import get_recent_news
from llm_processor import generate_report
from mailer import send_email
from sheets_logger import log_to_sheets

# 使用者定義的名單 (前段部分，此處包含所有 60 家企業)
COMPANIES = [
    "Fastenal", "ITW Fasteners", "Stanley Engineered Fastening", "Acument Global Technologies",
    "MNP Corporation", "Agrati NA", "KAMAX NA", "ARaymond North America", "Bulten North America",
    "EJOT North America", "Slidematic cold headed", "Semblex", "RB&W pierce clinch",
    "Ramco large diameter fasteners", "MacLean-Fogg", "Optimas Solutions", "EFC International",
    "Norm Fasteners Turkey", "Çetin Civata", "Obel Civata Turkey", "LISI Aerospace",
    "Birmingham Fastener", "Howmet Aerospace", "PCC fasteners", "PEM fasteners",
    "Bossard NA", "Infasco", "Elgin Fastener Group", "Decker Manufacturing", "SFS intec US",
    "Valley Forge Bolt", "Shannon Fasteners", "Tornillos Monterrey", "Böllhoff NA",
    "Berdan Civata Turkey", "Ezel Civata", "Berat Civata", "Grainger", "Würth Industry NA",
    "Meidoh fastener", "KPF Korea", "Aoyama Seisakusho", "Taeyang Metal", "Saga Tekkosho",
    "Jin-Hap fastener", "Nitto Seiko", "Meira Corporation", "Sannohashi", "Topura",
    "Young Shin Metal", "Nagoya Screw", "Daehwa Industrial", "Owari Precise", "Yamashina",
    "Iwata Bolt", "Unytite", "Shin-Heung Precision", "Nishihata Seisakusho", "Mitsuchi"
]

# 為了避免測試階段耗時過長，你可以先將上方陣列縮減為前 5 家來測試
# COMPANIES = COMPANIES[:5]

def main():
    print("====== 啟動每日扣件產業市場情報系統 ======")
    
    all_news = []
    
    print(f"開始收集 {len(COMPANIES)} 家公司的新聞 (預計耗時數分鐘)...")
    for idx, company in enumerate(COMPANIES):
        print(f"[{idx+1}/{len(COMPANIES)}] 正在搜尋: {company} ...")
        news = get_recent_news(company)
        all_news.append(f"### {company}\n{news}\n")
        
        # 避免觸發搜尋引擎 Rate Limit，每次搜尋後暫停 2 秒
        time.sleep(2)
        
    compiled_news_text = "\n".join(all_news)
    
    print("\n新聞收集完畢！交由 AI 撰寫報告中...")
    try:
        markdown_report = generate_report(compiled_news_text)
        print("報告產生完成！")
        
        # 將最終結果備份至本機 (選用)
        with open("latest_report.md", "w", encoding="utf-8") as f:
            f.write(markdown_report)
            
    except Exception as e:
        print(f"產生報告時發生錯誤: {e}")
        return
    
    print("\n準備發送 Email...")
    send_email(markdown_report)
    
    print("\n準備寫入 Google 試算表...")
    log_to_sheets(markdown_report)
    
    print("====== 系統執行完畢 ======")

if __name__ == "__main__":
    main()
