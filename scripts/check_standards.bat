@echo off
chcp 65001 > nul
echo ========================================
echo 项目记录目录规范检查
echo ========================================
echo.

python scripts\check_directory_standards.py

echo.
echo 按任意键退出...
pause > nul
