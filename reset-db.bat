@echo off
chcp 65001 >nul
echo ============================================
echo   优尚服饰门店运营管理系统 - 重置数据库
echo ============================================
echo.

echo [警告] 此操作将清空所有数据并重新初始化！
echo.
set /p confirm="确定要重置数据库吗？(Y/N): "
if /i not "%confirm%"=="Y" (
    echo 操作已取消
    pause
    exit /b 0
)

echo.
echo 正在重置数据库...
cd /d %~dp0backend

:: 删除旧数据库
if exist "smart_store.db" (
    del "smart_store.db"
    echo   ✓ 已删除旧数据库
)

:: 重新初始化
python seed_data.py
if errorlevel 1 (
    echo [错误] 数据库重置失败
    pause
    exit /b 1
)

echo.
echo ============================================
echo   数据库重置完成！
echo ============================================
pause
