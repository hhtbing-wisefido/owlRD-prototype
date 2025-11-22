@echo off
chcp 65001 >nul
echo.
echo ================================================================================
echo                      运行 Playwright E2E 测试
echo ================================================================================
echo.

cd /d "%~dp0"
python tests\full_system_test.py --playwright

echo.
echo 按任意键退出...
pause >nul
