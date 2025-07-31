# build.ps1
Write-Host "=== AetherOnePy Build Script ===" -ForegroundColor Green

# Check if running as administrator
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "ERROR: This script must be run as Administrator" -ForegroundColor Red
    Write-Host "Right-click on PowerShell and select 'Run as administrator'"
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Running as Administrator - Good!" -ForegroundColor Green

# Set location to script directory
Set-Location $PSScriptRoot
Write-Host "Current directory: $(Get-Location)"

# Check required files
if (-not (Test-Path "desktop_launcher.py")) {
    Write-Host "ERROR: desktop_launcher.py not found" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

if (-not (Test-Path "py")) {
    Write-Host "ERROR: py folder not found" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Cleanup
Write-Host "Cleaning old build files..." -ForegroundColor Yellow
if (Test-Path "dist") {
    Remove-Item "dist" -Recurse -Force -ErrorAction SilentlyContinue
}
if (Test-Path "build") {
    Remove-Item "build" -Recurse -Force -ErrorAction SilentlyContinue
}

# Activate virtual environment
$venvPaths = @("py\.venv\Scripts\Activate.ps1", ".venv\Scripts\Activate.ps1", "venv\Scripts\Activate.ps1")
$venvFound = $false

foreach ($venvPath in $venvPaths) {
    if (Test-Path $venvPath) {
        Write-Host "Found virtual environment at: $venvPath" -ForegroundColor Green
        & $venvPath
        $venvFound = $true
        break
    }
}

if (-not $venvFound) {
    Write-Host "Warning: No virtual environment found" -ForegroundColor Yellow
}

# Build
Write-Host "Building executable..." -ForegroundColor Yellow
Write-Host "This may take several minutes, please wait..." -ForegroundColor Cyan

if (Test-Path "AetherOnePy.spec") {
    pyinstaller AetherOnePy.spec --noconfirm
} else {
    pyinstaller --name "AetherOnePy" --add-data "py;py" --console --noupx desktop_launcher.py
}

# Check result
if (Test-Path "dist\AetherOnePy\AetherOnePy.exe") {
    Write-Host "`n=== BUILD SUCCESSFUL ===" -ForegroundColor Green
    $exePath = Resolve-Path "dist\AetherOnePy\AetherOnePy.exe"
    Write-Host "Executable created at: $exePath"
    
    $choice = Read-Host "Do you want to test the executable now? (Y/N)"
    if ($choice -eq "Y" -or $choice -eq "y") {
        Start-Process -FilePath $exePath
    }
} else {
    Write-Host "`n=== BUILD FAILED ===" -ForegroundColor Red
}

Read-Host "Press Enter to exit"