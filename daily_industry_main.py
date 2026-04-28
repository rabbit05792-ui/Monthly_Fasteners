import os
from datetime import datetime
from daily_industry_scraper import search_industry_news
from daily_industry_llm import generate_daily_report
from mailer import send_email
from sheets_logger import log_daily_text_to_sheets
from dotenv import load_dotenv

def main():
    load_dotenv()
    
    print("====== 開始執行 每日工業新聞彙整與變革預警系統 ======")
    
    # 1. 抓取過去一週內的權威網站新聞
    print("\n[1/3] 執行多源檢索 (鎖定權威網域)...")
    raw_data = search_industry_news(timelimit='w')
    
    # 2. 透過 Gemini 產生專家級簡報
    print("\n[2/3] 執行專家優化分析...")
    try:
        markdown_report = generate_daily_report(raw_data)
        print("✅ 報告生成完畢！")
        
        # 將本次報告存檔以便除錯
        with open("latest_daily_industry_report.md", "w", encoding="utf-8") as f:
            f.write(markdown_report)
            
    except Exception as e:
        print(f"❌ 產生報告時發生錯誤: {e}")
        return
        
    # 3. 寄出 Email
    print("\n[3/3] 準備發送預警簡報...")
    # 自訂信件標題
    subject = "⚠️ 每日工業新聞彙整與變革預警系統"
    title = "⚠️ 每日工業新聞彙整與變革預警系統"
    
    send_email(markdown_report, subject=subject, title=title)
    
    # 4. 寫入 Google 試算表備份
    print("\n[4/4] 準備寫入每日 Google 試算表...")
    log_daily_text_to_sheets(markdown_report, prefix="每日工業預警")
    
    print("====== 系統執行完畢 ======")

if __name__ == "__main__":
    main()
