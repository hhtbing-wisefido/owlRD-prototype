@echo off
chcp 65001 >nul
echo.
echo ================================================================================
echo                        运行 Vitest 单元测试
echo ================================================================================
echo.

cd /d "%~dp0"
python tests\full_system_test.py --vitest

echo.
echo 按任意键退出...
pause >nul
