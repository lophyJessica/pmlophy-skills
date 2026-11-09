@echo off
chcp 65001 >nul
setlocal

REM pmlophy-skills Windows 同步入口
REM 实际逻辑在 sync-skills-windows.ps1（Junction 重建、备份、清理僵尸链接）
REM 用法：
REM   sync-skills-windows.bat            直接同步
REM   sync-skills-windows.bat -DryRun    先演练，只看会动哪些，不实际改

set "PS1=%~dp0sync-skills-windows.ps1"
if not exist "%PS1%" (
    echo [FAIL] 找不到 %PS1%
    pause
    exit /b 1
)

echo.
echo === pmlophy-skills Windows 同步 ===
powershell -NoProfile -ExecutionPolicy Bypass -File "%PS1%" %*
set "RC=%ERRORLEVEL%"

echo.
if not "%RC%"=="0" (
    echo [FAIL] 同步失败，退出码 %RC%
) else (
    echo [OK] 同步完成
)
echo 提示：目录是否变成 Junction 用  dir /al  查看。
pause
exit /b %RC%
