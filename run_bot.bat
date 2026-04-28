@echo off
chcp 65001 > nul
echo 準備執行情報收集機器人...
cd /d "%~dp0"
python main.py
echo.
pause
