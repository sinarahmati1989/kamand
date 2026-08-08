@echo off
chcp 65001 > nul
color 0A
title Kamand - Environment Setup

echo.
echo  ═══════════════════════════════════════════════════════════
echo   🏭 KAMAND — Environment Setup
echo  ═══════════════════════════════════════════════════════════
echo.

REM ─── تنظیمات ───
set VENV_PATH=C:\kamand-venv
set PYTHON_VERSION=3.12

REM ─── [1/7] چک وجود Python 3.12 ───
echo  [1/7] بررسی Python %PYTHON_VERSION%...
py -%PYTHON_VERSION% --version > nul 2>&1
if errorlevel 1 (
    color 0C
    echo  ❌ Python %PYTHON_VERSION% یافت نشد!
    echo.
    echo     لطفاً از این لینک نصب کنید:
    echo     https://www.python.org/downloads/release/python-3123/
    echo.
    pause
    exit /b 1
)
for /f "tokens=*" %%v in ('py -%PYTHON_VERSION% --version') do set PY_VER=%%v
echo  ✅ %PY_VER% موجود است
echo.

REM ─── [2/7] ساخت venv اگر نبود ───
if not exist "%VENV_PATH%\Scripts\activate.bat" (
    echo  [2/7] ساخت venv در %VENV_PATH% ...
    py -%PYTHON_VERSION% -m venv "%VENV_PATH%"
    if errorlevel 1 (
        color 0C
        echo  ❌ خطا در ساخت venv
        pause
        exit /b 1
    )
    echo  ✅ venv ساخته شد
) else (
    echo  [2/7] venv قبلاً موجود است ✅
)
echo.

REM ─── [3/7] فعال‌سازی venv ───
echo  [3/7] فعال‌سازی venv...
call "%VENV_PATH%\Scripts\activate.bat"
if errorlevel 1 (
    color 0C
    echo  ❌ خطا در فعال‌سازی venv
    pause
    exit /b 1
)
echo  ✅ venv فعال شد
echo.

REM ─── [4/7] بروزرسانی pip ───
echo  [4/7] بروزرسانی pip...
python -m pip install --upgrade pip > nul 2>&1
echo  ✅ pip بروزرسانی شد
echo.

REM ─── [5/7] نصب پکیج‌ها ───
echo  [5/7] نصب پکیج‌ها از requirements.txt...
pip install -r requirements.txt
if errorlevel 1 (
    color 0C
    echo  ❌ خطا در نصب پکیج‌ها
    pause
    exit /b 1
)
echo  ✅ پکیج‌ها نصب شدند
echo.

REM ─── [6/7] چک .env ───
echo  [6/7] بررسی .env...
if not exist ".env" (
    if exist ".env.example" (
        copy .env.example .env > nul
        color 0E
        echo  ⚠️  فایل .env از .env.example ساخته شد
        echo.
        echo     🔴 مهم: قبل از ادامه، DB_PASSWORD را ویرایش کنید!
        echo.
        echo     دستور:  notepad .env
        echo.
        pause
        color 0A
    ) else (
        color 0C
        echo  ❌ .env.example هم موجود نیست!
        pause
        exit /b 1
    )
) else (
    echo  ✅ .env موجود است
)
echo.

REM ─── [7/7] Migration + Seed ───
echo  [7/7] اجرای Migration و Seed...
echo.
echo  ─── اجرای alembic upgrade head ───
alembic upgrade head
if errorlevel 1 (
    color 0C
    echo.
    echo  ❌ خطا در اجرای migration!
    echo.
    echo  احتمالاً:
    echo    - PostgreSQL روشن نیست (services.msc)
    echo    - DB_PASSWORD در .env اشتباه است
    echo.
    pause
    exit /b 1
)
echo  ✅ Migration ها اجرا شدند
echo.

echo  ─── اجرای Seed داده‌های پایه ───
python -m app.database.seeds.lookup_seeds
if errorlevel 1 (
    color 0E
    echo  ⚠️  خطا در seed (احتمالاً قبلاً seed شده)
    echo     ادامه می‌دهیم...
) else (
    echo  ✅ داده‌های پایه seed شدند
)
echo.

echo  ═══════════════════════════════════════════════════════════
color 0A
echo   ✅ همه چیز آماده است!
echo  ═══════════════════════════════════════════════════════════
echo.
echo  🚀 برای اجرای برنامه:  run.bat
echo  🛠️  برای CMD تعاملی:    cmd.bat
echo.
echo  👤 اطلاعات ورود:
echo     Username: admin
echo     Password: admin123
echo.
pause