@echo off
chcp 65001 > nul
echo ========================================
echo owlRD 系统全自动测试
echo ========================================
echo.
echo 注意：请确保后端服务已启动
echo   启动方式: cd owlRD-prototype/backend && python start_with_check.py
echo.
pause
echo.

python tests\full_system_test.py

echo.
echo 按任意键退出...
pause > nul
