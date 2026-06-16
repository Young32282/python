@echo off
chcp 65001 >nul
echo ============================================
echo   优尚服饰门店运营管理系统 - 停止服务
echo ============================================
echo.

echo 正在停止后端服务...
taskkill /FI "WINDOWTITLE eq Smart-Store Backend*" /F >nul 2>&1
if errorlevel 1 (
    echo   后端服务未运行或已停止
) else (
    echo   ✓ 后端服务已停止
)

echo 正在停止前端服务...
taskkill /FI "WINDOWTITLE eq Smart-Store Frontend*" /F >nul 2>&1
if errorlevel 1 (
    echo   前端服务未运行或已停止
) else (
    echo   ✓ 前端服务已停止
)

echo.
echo ============================================
echo   所有服务已停止
echo ============================================
pause
