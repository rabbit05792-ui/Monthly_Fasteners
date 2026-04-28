import smtplib
import os
import markdown
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def send_email(markdown_content):
    """將 Markdown 內容轉為 HTML 並透過 Gmail SMTP 寄送"""
    sender_email = os.getenv("SMTP_EMAIL")
    sender_password = os.getenv("SMTP_PASSWORD")
    target_emails_str = os.getenv("TARGET_EMAILS", "")
    
    if not sender_email or not sender_password or not target_emails_str:
        print("寄件失敗：缺少 .env 設定 (SMTP_EMAIL, SMTP_PASSWORD 或 TARGET_EMAILS)")
        return

    target_emails = [e.strip() for e in target_emails_str.split(",") if e.strip()]

    # 將 Markdown 轉為 HTML
    html_table = markdown.markdown(markdown_content, extensions=['tables'])
    
    # 加上簡單的 CSS 美化表格
    html_content = f"""
    <html>
    <head>
    <style>
      body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #333; }}
      table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
      th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
      th {{ background-color: #f4f6f8; font-weight: bold; }}
      tr:nth-child(even) {{ background-color: #fbfbfb; }}
      tr:hover {{ background-color: #f1f1f1; }}
      .footer {{ margin-top: 30px; font-size: 12px; color: #888; border-top: 1px solid #eee; padding-top: 10px; }}
    </style>
    </head>
    <body>
      <h2>📊 每月競爭對手新聞情報</h2>
      <p>日期：{datetime.now().strftime('%Y-%m-%d')}</p>
      <p>以下為最新的企業動態監控報告：</p>
      
      {html_table}
      
      <div class="footer">
        此報表由 AI 系統自動從公開新聞源蒐集並產生。<br>
        發送帳號：{sender_email}
      </div>
    </body>
    </html>
    """

    # 設定信件標題與收件人
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f"📊 每月競爭對手新聞情報 - {datetime.now().strftime('%Y-%m-%d')}"
    msg['From'] = sender_email
    msg['To'] = ", ".join(target_emails)

    part = MIMEText(html_content, 'html')
    msg.attach(part)

    try:
        print(f"正在透過 smtp.gmail.com 寄送給 {target_emails_str} ...")
        # Google Workspace 使用 smtp.gmail.com 搭配 SSL/465
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, target_emails, msg.as_string())
        server.quit()
        print("Email 寄送成功！")
    except Exception as e:
        print(f"寄送 Email 時發生錯誤: {e}")
