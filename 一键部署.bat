@echo off
chcp 65001 >nul
title 优尚服饰系统 - 一键部署

echo ============================================
echo   优尚服饰门店运营管理系统 - 一键部署
echo ============================================
echo.

:: 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.9+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo [1/5] Python 已安装

:: 检查 Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Node.js，请先安装 Node.js 16+
    echo 下载地址: https://nodejs.org/
    pause
    exit /b 1
)
echo [2/5] Node.js 已安装

:: 安装后端依赖
echo [3/5] 安装后端依赖...
cd /d %~dp0backend
pip install -r requirements.txt -q
echo   ✓ 后端依赖完成

:: 初始化数据库
echo [4/5] 初始化数据库...
python seed_data.py
echo   ✓ 数据库初始化完成

:: 安装前端依赖
echo [5/5] 安装前端依赖...
cd /d %~dp0frontend
npm install --silent
echo   ✓ 前端依赖完成

echo.
echo ============================================
echo   部署完成，正在启动服务...
echo ============================================
echo.

:: 启动后端
start "Smart-Store Backend" cmd /k "cd /d %~dp0backend && uvicorn app.main:app --reload --port 8000"

:: 等待后端启动
timeout /t 3 /nobreak >nul

:: 启动前端
start "Smart-Store Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

:: 等待前端启动
timeout /t 5 /nobreak >nul

:: 打开浏览器
start http://localhost:5173

echo ============================================
echo   系统已启动！
echo ============================================
echo.
echo   前端地址: http://localhost:5173
echo   后端地址: http://localhost:8000
echo.
echo   测试账号:
echo   收银员: cashier1 / 123456
echo   店长:   manager1 / 123456
echo   区域经理: regional1 / 123456
echo.
pause
