@echo off
chcp 65001 > nul
title Kamand - CMD

set VENV_PATH=C:\kamand-venv

if not exist "%VENV_PATH%\Scripts\activate.bat" (
    color 0C
    echo.
    echo  ❌ venv یافت نشد. ابتدا setup.bat را اجرا کنید
    echo.
    pause
    exit /b 1
)

call "%VENV_PATH%\Scripts\activate.bat"
color 0A
echo.
echo  ═══════════════════════════════════════════════════════════
echo   🏭 KAMAND — Interactive CMD (venv active)
echo  ═══════════════════════════════════════════════════════════
echo.
echo  📦 دستورات مفید:
echo.
echo    ─── Alembic (Migration) ───
echo    alembic upgrade head              اجرای migration ها
echo    alembic revision -m "..."         migration جدید
echo    alembic history                   تاریخچه migration
echo    alembic current                   migration فعلی
echo.
echo    ─── Seed ───
echo    python -m app.database.seeds.lookup_seeds
echo.
echo    ─── اجرا ───
echo    python main.py                    اجرای برنامه
echo.
echo    ─── Git ───
echo    git status
echo    git pull
echo    git add . ^&^& git commit -m "..." ^&^& git push
echo.
echo  برای خروج: exit
echo  ═══════════════════════════════════════════════════════════
echo.

cmd /k