# PintaAI dev restart script
$ErrorActionPreference = "SilentlyContinue"

Write-Host "Killing all processes on ports 8000, 8001, 5173, 5174, 5175..." -ForegroundColor Yellow

foreach ($port in @(8000, 8001, 5173, 5174, 5175)) {
    Get-NetTCPConnection -LocalPort $port |
        Select-Object -ExpandProperty OwningProcess |
        Sort-Object -Unique |
        ForEach-Object { Stop-Process -Id $_ -Force }
}

Start-Sleep -Seconds 2

Write-Host "Clearing Vite cache..." -ForegroundColor Yellow
$viteCache = "$PSScriptRoot\frontend\node_modules\.vite"
if (Test-Path $viteCache) { Remove-Item -Recurse -Force $viteCache }

Write-Host "Starting backend on port 8001..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\backend'; uvicorn main:app --reload --port 8001"

Start-Sleep -Seconds 2

Write-Host "Starting frontend..." -ForegroundColor Green
Set-Location "$PSScriptRoot\frontend"
npm run dev -- --force
