@echo off
chcp 65001 >nul
echo ========================================
echo 👁️ 项目结构自动监控
echo ========================================
echo.
echo 📋 说明:
echo   - 自动监控项目目录变化
echo   - 创建/删除/移动目录时自动检查
echo   - 按 Ctrl+C 可停止监控
echo.
echo ⚠️ 需要安装 watchdog 库
echo    pip install watchdog
echo.
echo ========================================
echo.

python .windsurfrules\scripts\watch_and_check.py

pause
