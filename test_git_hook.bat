@echo off
chcp 65001 >nul
echo ========================================
echo 🧪 测试Git Hook自动检查
echo ========================================
echo.
echo 📝 创建测试文件...
echo test > test_file.txt
echo.

echo 📦 添加到Git...
git add test_file.txt
echo.

echo 🚀 尝试提交（会触发自动检查）...
git commit -m "test: 测试Git Hook自动检查"
echo.

echo 🧹 清理测试文件...
git reset HEAD test_file.txt
del test_file.txt
echo.

echo ========================================
echo ✅ 测试完成
echo ========================================
pause
