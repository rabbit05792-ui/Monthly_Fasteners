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
            
    except Exception as e:
        print(f"❌ 寫入 Google 試算表時發生錯誤: {e}")

def log_daily_text_to_sheets(markdown_content, prefix="每日工業預警"):
    """將每日文字報告以新增一列的方式寫入 Google 試算表"""
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
        date_str = today.strftime('%Y-%m-%d %H:%M')
        
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
            worksheet = spreadsheet.add_worksheet(title=worksheet_name, rows="100", cols="3")
            # 寫入標題列
            worksheet.append_row(["日期", "每日情報內容"])
            worksheet.format('A1:B1', {'textFormat': {'bold': True}, 'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9}})
            
        # 每天新增一列
        worksheet.append_row([date_str, markdown_content])
        print("✅ 成功將今日情報寫入 Google 試算表！")
            
    except Exception as e:
        print(f"❌ 寫入每日 Google 試算表時發生錯誤: {e}")
