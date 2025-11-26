@echo off
chcp 65001 >nul
echo ========================================
echo ⏰ 创建Windows定时任务
echo ========================================
echo.
echo 📋 将创建以下定时任务:
echo   - 任务名称: 项目结构检查
echo   - 执行频率: 每天上午9:00
echo   - 执行脚本: check_project_structure.py
echo.
echo ⚠️ 需要管理员权限
echo.
pause

REM 获取当前目录
set "PROJECT_DIR=%~dp0.."
set "PYTHON_PATH=python"
set "SCRIPT_PATH=%PROJECT_DIR%\scripts\check_project_structure.py"

echo.
echo 🔧 创建定时任务...

schtasks /create /tn "项目结构检查" /tr "%PYTHON_PATH% \"%SCRIPT_PATH%\"" /sc daily /st 09:00 /f

if errorlevel 1 (
    echo.
    echo ❌ 创建失败！请以管理员身份运行此脚本
    pause
    exit /b 1
)

echo.
echo ========================================
echo ✅ 定时任务创建成功！
echo ========================================
echo.
echo 📋 任务信息:
schtasks /query /tn "项目结构检查" /fo list /v
echo.
echo 💡 管理任务:
echo   - 查看: schtasks /query /tn "项目结构检查"
echo   - 运行: schtasks /run /tn "项目结构检查"
echo   - 删除: schtasks /delete /tn "项目结构检查" /f
echo.
pause
