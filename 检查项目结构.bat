@echo off
chcp 65001 >nul
echo ========================================
echo 📊 项目结构规范检查工具
echo ========================================
echo.

python .windsurfrules\scripts\check_project_structure.py

echo.
echo ========================================
if errorlevel 1 (
    echo ❌ 检查发现问题，请根据提示修正
) else (
    echo ✅ 检查通过
)
echo ========================================
echo.
pause
