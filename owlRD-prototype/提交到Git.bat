@echo off
chcp 65001 >nul
echo.
echo ================================================================================
echo                         提交项目到Git
echo ================================================================================
echo.

cd /d "%~dp0"

echo [1/4] 查看当前状态...
git status
echo.

echo [2/4] 添加所有更改...
git add .
echo.

echo [3/4] 提交更改...
git commit -m "feat: 集成Vitest和Playwright测试框架

- 添加Vitest单元测试配置和示例（7/7通过）
- 添加Playwright E2E测试配置
- 整合测试文档到tests/README.md
- 更新full_system_test.py支持--vitest和--playwright
- 配置淘宝npm镜像加速
- 解决React重复实例问题
- 根据实际UserForm组件编写测试
- 保存聊天记录和迁移指南
"
echo.

echo [4/4] 推送到远程仓库...
echo 提示：如果还没关联远程仓库，请先运行：
echo git remote add origin https://github.com/你的用户名/owlRD-prototype.git
echo.
git push
echo.

echo ================================================================================
echo ✅ 提交完成！
echo.
echo 在新电脑上恢复项目：
echo 1. git clone https://github.com/你的用户名/owlRD-prototype.git
echo 2. 查看迁移指南: 项目记录\项目迁移指南.md
echo 3. 查看聊天记录: 项目记录\聊天记录\2025-11-22_Vitest和Playwright测试框架集成.md
echo ================================================================================
echo.

pause
