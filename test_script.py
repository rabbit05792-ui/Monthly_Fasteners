import os
import time
from scraper import get_recent_news
from llm_processor import generate_report

companies = ["Fastenal", "ITW Fasteners", "Norm Fasteners Turkey"]
news_data = []

print("開始獲取新聞...")
for c in companies:
    print(f"搜尋 {c}...")
    news = get_recent_news(c)
    news_data.append(f"### {c}\n{news}\n")
    time.sleep(5) # 增加延遲避免被擋

compiled_news = "\n".join(news_data)
print("--- 搜尋結果原始資料 ---")
print(compiled_news)
print("------------------------\n")

print("呼叫 LLM 產生報告...")
try:
    report = generate_report(compiled_news)
    print("--- 最終 Markdown 報告 ---")
    print(report)
except Exception as e:
    print(f"LLM 發生錯誤: {e}")
