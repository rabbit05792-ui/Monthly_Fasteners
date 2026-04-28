@echo off
chcp 65001 > nul
echo 正在為您設定「每月1號早上8點」自動執行的排程...
cd /d "%~dp0"
set SCRIPT_PATH=%~dp0run_bot.bat
schtasks /create /tn "FastenerMarketBot" /tr "\"%SCRIPT_PATH%\"" /sc monthly /d 1 /st 08:00 /f
echo.
echo 設定完成！以後每個月 1 號早上 8:00 電腦只要開著，就會自動發送情報 Email。
pause
