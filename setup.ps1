# NΞXUS 一键部署 — Windows
# 右键 → 使用 PowerShell 运行，或: powershell -ExecutionPolicy Bypass -File setup.ps1

Write-Host "╔═══════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   NΞXUS AI 部署 — Windows        ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════╝" -ForegroundColor Cyan

# 检查 Python
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host "❌ 需要 Python 3.10+，正在通过 winget 安装..."
    winget install Python.Python.3.12 --silent
    $env:Path += ";$env:LOCALAPPDATA\Programs\Python\Python312"
}

# 检查 Git
$git = Get-Command git -ErrorAction SilentlyContinue
if (-not $git) {
    Write-Host "❌ 需要 Git，正在通过 winget 安装..."
    winget install Git.Git --silent
}

Write-Host "✅ 环境就绪，运行部署脚本..." -ForegroundColor Green

# 下载并运行 Python 部署脚本
$setupPy = "$env:TEMP\nexus-setup.py"
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/qingyiwss/hermes-knowledge-flywheel/main/setup.py" -OutFile $setupPy
python $setupPy

Write-Host ""
Write-Host "✅ 部署完成！AI 启动: cd ~/nexus-knowledge; python context-loader.py" -ForegroundColor Green
pause
