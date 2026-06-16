@echo off
chcp 65001 >nul
echo ============================================
echo   优尚服饰门店运营管理系统 - 一键部署
echo ============================================
echo.

:: 检查 Python
echo [检查环境] 验证 Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.9+
    pause
    exit /b 1
)
echo   ✓ Python 已安装

:: 检查 Node.js
echo [检查环境] 验证 Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Node.js，请先安装 Node.js 16+
    pause
    exit /b 1
)
echo   ✓ Node.js 已安装
echo.

:: 安装后端依赖
echo [1/4] 安装后端依赖...
cd /d %~dp0backend
pip install -r requirements.txt -q
if errorlevel 1 (
    echo [错误] 后端依赖安装失败
    pause
    exit /b 1
)
echo   ✓ 后端依赖安装完成
echo.

:: 初始化数据库
echo [2/4] 初始化数据库...
python seed_data.py
if errorlevel 1 (
    echo [错误] 数据库初始化失败
    pause
    exit /b 1
)
echo   ✓ 数据库初始化完成
echo.

:: 安装前端依赖
echo [3/4] 安装前端依赖...
cd /d %~dp0frontend
if not exist "node_modules" (
    npm install
    if errorlevel 1 (
        echo [错误] 前端依赖安装失败
        pause
        exit /b 1
    )
    echo   ✓ 前端依赖安装完成
) else (
    echo   ✓ 前端依赖已存在，跳过安装
)
echo.

:: 启动服务
echo [4/4] 启动服务...
echo.
echo ============================================
echo   启动后端服务（端口 8000）...
echo ============================================
start "Smart-Store Backend" cmd /k "cd /d %~dp0backend && uvicorn app.main:app --reload --port 8000"

:: 等待后端启动
timeout /t 3 /nobreak >nul

echo ============================================
echo   启动前端服务（端口 5173）...
echo ============================================
start "Smart-Store Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

:: 等待前端启动
timeout /t 5 /nobreak >nul

echo.
echo ============================================
echo   系统部署完成！
echo ============================================
echo.
echo   前端地址: http://localhost:5173
echo   后端地址: http://localhost:8000
echo.
echo   测试账号：
echo   收银员: cashier1 / 123456
echo   店长:   manager1 / 123456
echo   区域经理: regional1 / 123456
echo.
echo   按任意键打开浏览器访问系统...
pause >nul

:: 打开浏览器
start http://localhost:5173

echo.
echo 系统正在运行中...
echo 关闭此窗口不会影响系统运行。
echo 如需停止系统，请关闭后端和前端的命令行窗口。
pause
