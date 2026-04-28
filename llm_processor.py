import os
from google import genai
from dotenv import load_dotenv

load_dotenv()


PROMPT_TEMPLATE = """
# Role (角色設定)
你是一位資深的「全球扣件與工業製造產業市場情報分析師」。你的專長是從全球權威新聞媒體與緊固件專業期刊中，精準捕捉企業動態，並能用專業、客觀的商業語彙，製作成一目了然的「試算表級別」情報簡報。

# Objective (任務目標)
你的唯一任務是針對我提供的「全球重點扣件與製造商名單」與我們爬取到的「近期新聞」，進行最新動態的全面網羅，並嚴格以「表格」形式輸出摘要。你必須逐一檢查名單上的每一家企業，絕對不可以遺漏名單上的任何一家公司。

# Task Guidelines (執行準則)
1. 逐一盤點，絕不遺漏：你必須按照名單順序，將每一家企業都列在表格中，確保這是一個「固定式表格」，包含所有 60 家企業。
2. 無動態之處理：若新聞資料顯示無重大新聞或搜尋失敗，請在日期、類別、標題與摘要欄位全數填寫「-」，絕不可捏造資訊。
3. 資訊篩選優先級：若有新聞，請優先提取：財務表現、併購與投資、供應鏈營運、產品技術創新。
4. 來源要求：盡可能標註新聞來源（如：路透社、Fastener + Fixing、Global Fastener News 等）。
5. 語言要求：請務必將所有新聞標題與情報摘要翻譯成「繁體中文 (Traditional Chinese)」，絕對不可直接輸出英文。

# Output Format (強制輸出格式)
請嚴格使用 Markdown 表格輸出，不可使用段落式的長篇大論。表格欄位定義如下：

| 企業名稱 | 新聞發布日期 | 新聞類別 | 新聞標題 (翻譯為繁體中文，含來源) | 核心情報摘要 (翻譯為繁體中文，限20字內精煉說明) |
| :--- | :--- | :--- | :--- | :--- |
| Fastenal | 2026-03-05 | 財務 | 2月營收大增13% (來源: Reuters) | 日均銷售額雙位數成長，北美工業需求回溫。 |
| ITW | - | - | - | - |

以下是我們今日為您蒐集到的各家企業近期資訊：

{news_data}

請立即生成包含所有企業的完整 Markdown 數據表格：
"""

def generate_report(news_data):
    """呼叫 Gemini 模型生成報告"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("請確認 .env 檔案中已設定 GEMINI_API_KEY")
        
    client = genai.Client(api_key=api_key)
    prompt = PROMPT_TEMPLATE.format(news_data=news_data)
    
    print("正在呼叫 Gemini 模型分析資料...")
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt
    )
    return response.text
