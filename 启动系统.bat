@echo off
chcp 65001 >nul
echo 正在启动系统...

start "Smart-Store Backend" cmd /k "cd /d %~dp0backend && uvicorn app.main:app --reload --port 8000"
start "Smart-Store Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

timeout /t 5 /nobreak >nul

start http://localhost:5173

echo 系统已启动！
