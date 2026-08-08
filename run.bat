@echo off
chcp 65001 > nul
title Kamand - Running...

set VENV_PATH=C:\kamand-venv

REM ─── چک venv ───
if not exist "%VENV_PATH%\Scripts\activate.bat" (
    color 0C
    echo.
    echo  ❌ venv یافت نشد در %VENV_PATH%
    echo.
    echo  ابتدا اجرا کنید:  setup.bat
    echo.
    pause
    exit /b 1
)

REM ─── فعال‌سازی و اجرا ───
call "%VENV_PATH%\Scripts\activate.bat"
python main.py