@echo off
echo ========================================
echo 项目状态自动更新工具
echo ========================================
echo.

cd /d "%~dp0"
python update_project_status.py

echo.
echo ========================================
pause
