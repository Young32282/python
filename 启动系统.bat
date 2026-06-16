@echo off
chcp 65001 >nul
title Smart Store 智慧门店系统

echo ═══════════════════════════════════════════
echo   Smart Store 智慧门店系统 - 一键部署
echo ═══════════════════════════════════════════
echo.

:: 获取当前脚本所在目录
set "ROOT_DIR=%~dp0"
set "BACKEND_DIR=%ROOT_DIR%backend"

:: ─── 第一步：检查 Python ───
echo [1/4] 检查 Python 环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到 Python，请先安装 Python 3.9+
    echo 下载地址: https://www.python.org/downloads/
    echo 安装时请勾选 "Add Python to PATH"
    pause
    exit /b 1
)
for /f "tokens=*" %%v in ('python --version 2^>^&1') do echo   ✓ %%v

:: ─── 第二步：安装依赖 ───
echo.
echo [2/4] 安装后端依赖...
cd /d "%BACKEND_DIR%"
pip install -r requirements.txt -q 2>nul
if %errorlevel% neq 0 (
    echo [警告] 部分依赖安装失败，尝试继续...
) else (
    echo   ✓ 依赖安装完成
)

:: ─── 第三步：初始化数据库 ───
echo.
echo [3/4] 初始化数据库...
if exist "%BACKEND_DIR%\smart_store.db" (
    echo   ✓ 数据库已存在，跳过初始化
) else (
    python seed_data.py
    if %errorlevel% neq 0 (
        echo [错误] 数据库初始化失败
        pause
        exit /b 1
    )
    echo   ✓ 数据库初始化完成
)

:: ─── 第四步：启动服务 ───
echo.
echo [4/4] 启动服务...
echo.
echo ═══════════════════════════════════════════
echo   系统启动中，请稍候...
echo   浏览器访问: http://localhost:8000
echo.
echo   测试账号:
echo     收银员: cashier1 / 123456
echo     店  长: manager1 / 123456
echo     区域经理: regional1 / 123456
echo.
echo   按 Ctrl+C 停止服务
echo ═══════════════════════════════════════════
echo.

:: 延迟 2 秒后打开浏览器
start "" /min cmd /c "timeout /t 2 /nobreak >nul && start http://localhost:8000"

:: 启动后端服务
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
