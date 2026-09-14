@echo off
setlocal enabledelayedexpansion
title Student Performance Prediction System
cd /d "%~dp0"

echo ======================================================================
echo    Student Performance Prediction System (BCA Academic Project)
echo ======================================================================
echo.

:: 1. Detect Python
set "PY_CMD="

:: Check standard py launcher for 3.12, 3.11, 3.13, 3.10
for %%V in (-3.12 -3.11 -3.13 -3.10 -3) do (
    if not defined PY_CMD (
        py %%V -c "import sys" >nul 2>&1
        if !errorlevel! equ 0 (
            set "PY_CMD=py %%V"
        )
    )
)

:: Check python command in PATH
if not defined PY_CMD (
    python -c "import sys" >nul 2>&1
    if !errorlevel! equ 0 (
        set "PY_CMD=python"
    )
)

:: Check common AppData Python installs
if not defined PY_CMD (
    if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
        set "PY_CMD=\"%LOCALAPPDATA%\Programs\Python\Python312\python.exe\""
    ) else if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
        set "PY_CMD=\"%LOCALAPPDATA%\Programs\Python\Python311\python.exe\""
    ) else if exist "%LOCALAPPDATA%\Programs\Python\Python310\python.exe" (
        set "PY_CMD=\"%LOCALAPPDATA%\Programs\Python\Python310\python.exe\""
    )
)

if not defined PY_CMD (
    echo [ERROR] Python was not detected on this system.
    echo Please install Python 3.10, 3.11, or 3.12 from https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

echo [INFO] Detected Python: !PY_CMD!
echo.

:: 2. Run master launcher run.py
!PY_CMD! run.py

pause
