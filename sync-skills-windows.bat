@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM pmlophy-skills Windows 软链安装脚本
REM 真源：脚本所在仓库的 .agents\skills
REM 作用：逐个 skill 建立 Junction 到用户级 Agent 目录

set "SRC=%~dp0.agents\skills"
if not exist "%SRC%" set "SRC=%~dp0skills"
set "HUB=%USERPROFILE%\.agents\skills"

if not exist "%SRC%" (
    echo [FAIL] 找不到 skill 真源: %SRC%
    pause
    exit /b 1
)
if not exist "%HUB%" mkdir "%HUB%"

echo.
echo === pmlophy-skills Windows 软链安装 ===
echo 真源: %SRC%
echo 中枢: %HUB%
echo.

REM 逐个 skill 建立中枢 Junction
for /d %%D in ("%SRC%\*") do (
    set "NAME=%%~nD"
    set "TARGET=%HUB%\!NAME!"
    if exist "!TARGET!" (
        set "BACKUP=!TARGET!.backup-%RANDOM%"
        move "!TARGET!" "!BACKUP!" >nul 2>nul
        echo [BACKUP] !TARGET! ^> !BACKUP!
    )
    mklink /J "!TARGET!" "%%D" 2>nul
    if exist "!TARGET!" (echo [OK] 中枢 !NAME!) else (echo [FAIL] 中枢 !NAME!)
)

call :mirror "Cursor" "%USERPROFILE%\.cursor\skills"
call :mirror "Codex" "%USERPROFILE%\.codex\skills"
call :mirror "Antigravity" "%USERPROFILE%\.antigravity\skills"

:done
echo.
echo === 全部完成 ===
echo 真源: %SRC%
echo 中枢: %HUB%
echo 不涉及 cms-project，不会在项目目录写入 skill。
pause
exit /b 0

:mirror
set "LABEL=%~1"
set "DEST=%~2"
if not exist "%DEST%" (
    echo [SKIP] %LABEL% 目录不存在: %DEST%
    exit /b 0
)
echo 镜像到 %LABEL%...
for /d %%D in ("%SRC%\*") do (
    set "NAME=%%~nD"
    set "TARGET=%DEST%\!NAME!"
    if exist "!TARGET!" (
        set "BACKUP=!TARGET!.backup-%RANDOM%"
        move "!TARGET!" "!BACKUP!" >nul 2>nul
        echo [BACKUP] !TARGET! ^> !BACKUP!
    )
    mklink /J "!TARGET!" "%%D" 2>nul
    if exist "!TARGET!" (echo [OK] !LABEL! !NAME!) else (echo [FAIL] !LABEL! !NAME!)
)
exit /b 0
