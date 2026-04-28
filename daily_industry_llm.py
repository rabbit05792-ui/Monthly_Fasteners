import os
from google import genai
from google.genai import types

def generate_daily_report(raw_news_data):
    """
    將爬蟲抓到的原始資料丟給 Gemini 分析，
    並嚴格依照使用者的 Prompt 轉化為每日情報簡報。
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("請設定 GEMINI_API_KEY 環境變數")
        
    client = genai.Client(api_key=api_key)
    
    prompt = f"""
[角色任務]：
你是一位專精於全球重工業與前沿科技的**「產業情報分析官」**，核心目標是為決策者提供具備投資價值的每日動態簡報。

[背景資訊]：
目前時值 2026 年，全球正處於能源轉型臨界點。你需要追蹤汽車、重機具、能源、航太與軍工等核心產業的變革。

[內部事實查核基準 (Internal Fact Check)]：
為了防範假新聞與 AI 幻覺，請在評估新聞時與以下 2026 年的現實趨勢進行交叉比對：
- **汽車業**：2026 年是全球電動車補貼退坡與 L3 級自動駕駛商業化的關鍵年。
- **能源業**：2026 年初發生全球能源斷鏈事故，導致市場轉向「分布式自主能源」，歐洲與美國資料中心開始繞過電網直接興建 SMR。
- **軍工業**：台灣 2026 年國防預算已達 9,495 億台幣，佔 GDP 3.32%，重點在於無人機與防禦系統。

[約束條件]：
1. 請使用繁體中文。
2. 語氣保持專業中立，嚴禁包含未經證實的八卦。
3. 每個產業列出 2-3 則最關鍵的消息。如果該產業沒有重大新聞，請填寫「今日無重大變革預警」。
4. 對於每則新聞，請給予「事實查核與信心水準評估」。若內容空泛、與基準相左，請標記 [🚨 高風險/疑似假訊息]；若為單一發明查無細節，標記 [⚠️ 信心水準低於90%]。
5. 必須使用以下結構化整理格式輸出 Markdown：

### [產業名稱]
- **[標題]** ([附上新聞網址連結])
  - **核心事實摘要**: (請用一句話總結核心事件)
  - **投資/變革影響力評估**: (請以分析官的角度，評估這件事對資本支出、未來趨勢或市場的影響)
  - **🛡️ 事實查核**: (例如：[信賴度 95%] 符合 2026 年 L3 智駕商業化趨勢，具備權威來源。)

---
[多源檢索資料]：
以下是系統剛剛從各大權威來源抓取到的最新新聞摘要：

{raw_news_data}

請依照上述要求，將這些原始資料轉化為高價值且具備防偽機制的動態簡報！
    """
    
    print("🧠 正在請求 Gemini 進行情報分析官優化...")
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.3, # 降低隨機性，確保格式穩定
        )
    )
    
    return response.text
