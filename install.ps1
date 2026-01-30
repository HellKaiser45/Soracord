# Clear screen for a clean start
Clear-Host
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "   🚀 SoraCord One-Click Setup (Windows)   " -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

# 1. Check for Docker (Requirement)
if (!(Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "`n❌ Docker not found!" -ForegroundColor Red
    Write-Host "Please download and install Docker Desktop first:" -ForegroundColor White
    Write-Host "👉 https://www.docker.com/products/docker-desktop/" -ForegroundColor Cyan
    Write-Host "`nAfter installing and starting Docker, run this script again."
    Write-Host "Press any key to exit..."
    $null = [Console]::ReadKey($true)
    exit
}

# 2. Check for Git
if (!(Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "`n📦 Git not found. Trying to install via winget..." -ForegroundColor Yellow
    winget install --id Git.Git -e --source winget
    Write-Host "⚠️  You may need to restart this terminal for Git to be recognized."
}

# 3. Clone Repository
$RepoUrl = "https://github.com/HellKaiser45/Soracord.git"
$DirName = "Soracord"

if (Test-Path $DirName) {
    Write-Host "`n📂 Repository exists. Updating code..." -ForegroundColor Gray
    Set-Location $DirName
    git pull
} else {
    Write-Host "`n📂 Cloning SoraCord repository..." -ForegroundColor Gray
    git clone $RepoUrl
    Set-Location $DirName
}

# 4. Configuration (.env)
if (!(Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
}

Write-Host "`n--- Setup your Credentials ---" -ForegroundColor Yellow
$Token = Read-Host "Enter Discord Bot Token"
$ChanID = Read-Host "Enter Discord Channel ID (Default: 1348673358782703685)"
if ([string]::IsNullOrWhiteSpace($ChanID)) { $ChanID = "1348673358782703685" }
$SrvName = Read-Host "Enter a name for this VPS/Server"

# Update .env file content
$EnvContent = Get-Content .env
$EnvContent = $EnvContent -replace 'BOT_TOKEN=.*', "BOT_TOKEN=`"$Token`""
$EnvContent = $EnvContent -replace 'CHANNEL_ID=.*', "CHANNEL_ID=$ChanID"
$EnvContent = $EnvContent -replace 'SERVER_NAME=.*', "SERVER_NAME=`"$SrvName`""
$EnvContent | Set-Content .env

# 5. Final Launch
Write-Host "`n🏗️  Starting Docker containers..." -ForegroundColor Yellow
docker compose up -d --build

Write-Host "`n✅ SUCCESS! SoraCord is now running on $SrvName." -ForegroundColor Green
Write-Host "You can close this window now."
