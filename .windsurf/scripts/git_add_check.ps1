# Git Add 预检查脚本
# 用途：在 git add 前检查将要添加的文件，避免误提交

param(
    [switch]$DryRun = $false  # 预览模式
)

Write-Host "=== Git Add 预检查 ===" -ForegroundColor Cyan

# 1. 检查工作区状态
Write-Host "`n📋 工作区状态：" -ForegroundColor Yellow
$status = git status --short

if (-not $status) {
    Write-Host "  ✅ 工作区干净，无文件需要添加" -ForegroundColor Green
    exit 0
}

Write-Host $status

# 2. 分析文件类型
Write-Host "`n🔍 文件分析：" -ForegroundColor Yellow

$newFiles = @()
$modifiedFiles = @()
$deletedFiles = @()
$suspiciousFiles = @()

foreach ($line in $status) {
    $statusCode = $line.Substring(0, 2).Trim()
    $file = $line.Substring(3)
    
    switch ($statusCode) {
        "??" { $newFiles += $file }
        "M" { $modifiedFiles += $file }
        "D" { $deletedFiles += $file }
    }
    
    # 检查可疑文件
    if ($file -match "(temp|test|_old|backup|\.tmp|项目记录|windsurfrules)") {
        $suspiciousFiles += $file
    }
}

Write-Host "  📄 新文件: $($newFiles.Count)个" -ForegroundColor Gray
Write-Host "  ✏️ 修改文件: $($modifiedFiles.Count)个" -ForegroundColor Gray
Write-Host "  🗑️ 删除文件: $($deletedFiles.Count)个" -ForegroundColor Gray

# 3. 警告可疑文件
if ($suspiciousFiles.Count -gt 0) {
    Write-Host "`n⚠️ 发现可疑文件：" -ForegroundColor Red
    foreach ($file in $suspiciousFiles) {
        Write-Host "  ❌ $file" -ForegroundColor Red
    }
    Write-Host "`n这些文件可能不应该提交！" -ForegroundColor Yellow
}

# 4. 检查是否有空文件
Write-Host "`n📊 空文件检查：" -ForegroundColor Yellow
$emptyFiles = @()
foreach ($file in $newFiles) {
    if (Test-Path $file) {
        $size = (Get-Item $file).Length
        if ($size -eq 0) {
            $emptyFiles += $file
            Write-Host "  ⚠️ $file (0字节)" -ForegroundColor Yellow
        }
    }
}

if ($emptyFiles.Count -eq 0) {
    Write-Host "  ✅ 无空文件" -ForegroundColor Green
}

# 5. 按目录分组显示
Write-Host "`n📁 按目录分组：" -ForegroundColor Yellow

$allFiles = $newFiles + $modifiedFiles + $deletedFiles
$grouped = $allFiles | Group-Object { Split-Path $_ -Parent }

foreach ($group in $grouped) {
    $dir = if ($group.Name) { $group.Name } else { "根目录" }
    Write-Host "`n  📂 $dir ($($group.Count)个文件):" -ForegroundColor Cyan
    foreach ($file in $group.Group) {
        $basename = Split-Path $file -Leaf
        Write-Host "     - $basename" -ForegroundColor Gray
    }
}

# 6. 给出建议
Write-Host "`n💡 建议操作：" -ForegroundColor Cyan

if ($suspiciousFiles.Count -gt 0 -or $emptyFiles.Count -gt 0) {
    Write-Host "  ⚠️ 发现问题文件，建议：" -ForegroundColor Yellow
    Write-Host "     1. 检查并删除临时文件/空文件" -ForegroundColor Gray
    Write-Host "     2. 更新 .gitignore" -ForegroundColor Gray
    Write-Host "     3. 使用选择性添加：git add <文件路径>" -ForegroundColor Gray
} else {
    Write-Host "  ✅ 未发现明显问题" -ForegroundColor Green
    Write-Host "  📝 可以使用以下命令：" -ForegroundColor Gray
    Write-Host "     - 添加所有：git add -A" -ForegroundColor Gray
    Write-Host "     - 选择性添加：git add <文件路径>" -ForegroundColor Gray
}

# 7. 交互式选择（可选）
if (-not $DryRun) {
    Write-Host "`n❓ 是否继续查看详细信息？(Y/N)" -ForegroundColor Yellow
    $response = Read-Host
    
    if ($response -eq "Y" -or $response -eq "y") {
        Write-Host "`n📄 详细文件列表：" -ForegroundColor Cyan
        git status
    }
}

Write-Host "`n✅ 检查完成" -ForegroundColor Green
Write-Host "请谨慎使用 git add 命令！" -ForegroundColor Yellow
