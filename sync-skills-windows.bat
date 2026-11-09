@echo off
chcp 65001 >nul
setlocal

REM pmlophy-skills Windows sync entry
REM Logic lives in sync-skills-windows.ps1
REM Usage:
REM   sync-skills-windows.bat             run sync
REM   sync-skills-windows.bat -DryRun     dry run only

set "PS1=%~dp0sync-skills-windows.ps1"
if not exist "%PS1%" (
    echo [FAIL] sync-skills-windows.ps1 not found
    pause
    exit /b 1
)

echo.
echo === pmlophy-skills Windows sync ===
powershell -NoProfile -ExecutionPolicy Bypass -File "%PS1%" %*
set "RC=%ERRORLEVEL%"

echo.
if not "%RC%"=="0" (
    echo [FAIL] exit code %RC%
) else (
    echo [OK] done
)
echo Tip: check junctions with  dir /al
pause
exit /b %RC%
