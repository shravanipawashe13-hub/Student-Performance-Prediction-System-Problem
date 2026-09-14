# Universal PowerShell Runner for Any Windows PC
Set-Location -Path $PSScriptRoot

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "   Student Performance Prediction System (BCA Academic Project)" -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Cyan

# 1. Dynamically locate Python
$pyCmd = $null

if (Get-Command py -ErrorAction SilentlyContinue) {
    foreach ($ver in @("-3.12", "-3.11", "-3.13", "-3.10", "-3")) {
        try {
            $test = & py $ver -c "import sys; print(sys.executable)" 2>$null
            if ($test -and (Test-Path $test)) {
                $pyCmd = "py $ver"
                break
            }
        } catch {}
    }
}

if (-not $pyCmd -and (Get-Command python -ErrorAction SilentlyContinue)) {
    $pyCmd = "python"
}

if (-not $pyCmd) {
    $localPy = "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
    if (Test-Path $localPy) { $pyCmd = "& `"$localPy`"" }
}

if (-not $pyCmd) {
    Write-Host "[ERROR] Python 3 was not found. Please install Python 3.10+ from python.org" -ForegroundColor Red
    Pause
    Exit 1
}

Write-Host "[INFO] Detected Python: $pyCmd" -ForegroundColor Yellow

# 2. Run master launcher run.py
Invoke-Expression "$pyCmd run.py"
