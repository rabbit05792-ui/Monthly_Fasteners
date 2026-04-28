import os
import json
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# 定義要使用的 Google API 權限範圍
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

def parse_markdown_table(markdown_content):
    """將 Markdown 表格字串轉換為 2D 陣列 (List of Lists)"""
    lines = markdown_content.strip().split('\n')
    table_data = []
    
    # 尋找表格的起始與結束
    in_table = False
    for line in lines:
        line = line.strip()
        if line.startswith('|'):
            in_table = True
            # 略過分隔線 (例如 | :--- | :--- |)
            if '---' in line:
                continue
                
            # 去除頭尾的 '|' 並依 '|' 分割
            row = [cell.strip() for cell in line.strip('|').split('|')]
            table_data.append(row)
        else:
            # 如果已經離開表格區塊，就結束解析
            if in_table:
                break
                
    return table_data

def log_to_sheets(markdown_content):
    """將解析後的表格寫入對應年份與月份的 Google 試算表"""
    creds_json_str = os.getenv("GCP_SERVICE_ACCOUNT_JSON")
    folder_id = os.getenv("GDRIVE_FOLDER_ID") # 可選，用來指定新建檔案要放在哪個資料夾
    
    if not creds_json_str:
        print("未設定 GCP_SERVICE_ACCOUNT_JSON，跳過 Google 試算表寫入。")
        return
        
    try:
        # 從環境變數讀取 JSON 金鑰
        creds_dict = json.loads(creds_json_str)
        credentials = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        client = gspread.authorize(credentials)
        
        # 決定當前要寫入的年份與月份（這裡是寫入「上個月」的新聞，所以用執行時間上個月的月份來命名）
        today = datetime.today()
        first_day_current = today.replace(day=1)
        import datetime as dt_module
        last_day_prev = first_day_current - dt_module.timedelta(days=1)
        target_year = last_day_prev.year
        target_month = last_day_prev.month
        
        spreadsheet_name = f"{target_year}競爭對手新聞"
        worksheet_name = f"{target_month}月"
        
        print(f"準備寫入試算表: {spreadsheet_name} -> {worksheet_name}")
        
        spreadsheet = None
        try:
            # 嘗試尋找是否已經有該年份的試算表
            spreadsheet = client.open(spreadsheet_name)
        except gspread.exceptions.SpreadsheetNotFound:
            print(f"找不到試算表 '{spreadsheet_name}'，準備自動建立...")
            if folder_id:
                spreadsheet = client.create(spreadsheet_name, folder_id=folder_id)
            else:
                spreadsheet = client.create(spreadsheet_name)
            
            # 若有設定擁有者信箱，轉移擁有權或分享
            owner_email = os.getenv("SPREADSHEET_OWNER_EMAIL")
            if owner_email:
                spreadsheet.share(owner_email, perm_type='user', role='writer')
        
        # 尋找或建立月份分頁
        worksheet = None
        try:
            worksheet = spreadsheet.worksheet(worksheet_name)
            # 若存在，先清空舊資料
            worksheet.clear()
        except gspread.exceptions.WorksheetNotFound:
            print(f"建立新分頁 '{worksheet_name}'...")
            worksheet = spreadsheet.add_worksheet(title=worksheet_name, rows="100", cols="10")
            
        # 解析並寫入資料
        table_data = parse_markdown_table(markdown_content)
        if table_data:
            worksheet.update(values=table_data, range_name='A1')
            
            # 簡單調整欄位寬度與格式 (Optional)
            worksheet.format('A1:E1', {'textFormat': {'bold': True}, 'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9}})
            print("✅ 成功寫入 Google 試算表！")
        else:
            print("無法從內容中解析出表格資料。")
            
import re

def parse_daily_markdown_to_rows(markdown_content, date_str):
    """將 Markdown 內容解析為結構化列資料: [日期, 產業, 標題, 摘要, 影響, 查核, 連結]"""
    rows = []
    current_industry = ""
    lines = markdown_content.strip().split('\n')
    
    current_title = ""
    current_link = ""
    current_summary = ""
    current_impact = ""
    current_factcheck = ""
    
    def save_current_item():
        if current_title:
            rows.append([date_str, current_industry, current_title, current_summary, current_impact, current_factcheck, current_link])
    
    for line in lines:
        line = line.strip()
        if line.startswith('### '):
            save_current_item()
            current_industry = line[4:].strip()
            current_title, current_link, current_summary, current_impact, current_factcheck = "", "", "", "", ""
        elif line.startswith('- **') and '([閱讀原文]' in line:
            save_current_item()
            current_title, current_link, current_summary, current_impact, current_factcheck = "", "", "", "", ""
            match = re.search(r'-\s*\*\*\[(.*?)\]\*\*\s*\(\[閱讀原文\]\((.*?)\)\)', line)
            if match:
                current_title = match.group(1)
                current_link = match.group(2)
        elif '今日無重大變革預警' in line:
             pass
        elif '- **核心事實摘要**:' in line:
            current_summary = line.split(':', 1)[1].strip()
        elif '- **投資/變革影響力評估**:' in line or '- **變革影響力評估**:' in line:
            current_impact = line.split(':', 1)[1].strip()
        elif '- **🛡️ 事實查核**:' in line:
            current_factcheck = line.split(':', 1)[1].strip()

    save_current_item()
    return rows

def log_daily_text_to_sheets(markdown_content, prefix="每日工業預警"):
    """將每日文字報告解析後寫入 Google 試算表"""
    creds_json_str = os.getenv("GCP_SERVICE_ACCOUNT_JSON")
    folder_id = os.getenv("GDRIVE_FOLDER_ID")
    
    if not creds_json_str:
        print("未設定 GCP_SERVICE_ACCOUNT_JSON，跳過 Google 試算表寫入。")
        return
        
    try:
        creds_dict = json.loads(creds_json_str)
        credentials = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        client = gspread.authorize(credentials)
        
        today = datetime.today()
        target_year = today.year
        target_month = today.month
        date_str = today.strftime('%Y-%m-%d')
        
        spreadsheet_name = f"{target_year}{prefix}"
        worksheet_name = f"{target_month}月"
        
        print(f"準備寫入每日預警試算表: {spreadsheet_name} -> {worksheet_name}")
        
        spreadsheet = None
        try:
            spreadsheet = client.open(spreadsheet_name)
        except gspread.exceptions.SpreadsheetNotFound:
            print(f"找不到試算表 '{spreadsheet_name}'，準備自動建立...")
            if folder_id:
                spreadsheet = client.create(spreadsheet_name, folder_id=folder_id)
            else:
                spreadsheet = client.create(spreadsheet_name)
            
            owner_email = os.getenv("SPREADSHEET_OWNER_EMAIL")
            if owner_email:
                spreadsheet.share(owner_email, perm_type='user', role='writer')
        
        worksheet = None
        try:
            worksheet = spreadsheet.worksheet(worksheet_name)
        except gspread.exceptions.WorksheetNotFound:
            print(f"建立新分頁 '{worksheet_name}'...")
            worksheet = spreadsheet.add_worksheet(title=worksheet_name, rows="1000", cols="7")
            worksheet.append_row(["日期", "產業類別", "新聞標題", "核心事實摘要", "變革影響力評估", "事實查核與信心水準", "新聞連結"])
            worksheet.format('A1:G1', {'textFormat': {'bold': True}, 'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9}})
            
        rows_to_append = parse_daily_markdown_to_rows(markdown_content, date_str)
        if rows_to_append:
            worksheet.append_rows(rows_to_append)
            print(f"✅ 成功將 {len(rows_to_append)} 筆今日情報寫入 Google 試算表！")
        else:
            print("⚠️ 查無有效新聞可寫入試算表。")
            
    except Exception as e:
        print(f"❌ 寫入每日 Google 試算表時發生錯誤: {e}")
