@echo off
cd owlRD-prototype
git commit -m "feat: 完成全栈Model对齐和自动化验证体系" -m "后端Model: 100%对齐, 前端Type: 85.5%对齐" -m "新增2Model+3验证脚本, 修复4关键类型, 整理文档结构"
if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo 提交成功！
    echo ========================================
    git log -1 --stat
) else (
    echo.
    echo 提交失败，请检查错误信息
)
pause
