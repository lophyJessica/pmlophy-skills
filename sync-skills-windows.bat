@echo off
setlocal EnableExtensions

rem Windows skill sync script
rem Run from the pmlophy-skills repository root after pulling it.

set "REPO=%~dp0.agents\skills"
if not exist "%REPO%" set "REPO=%~dp0skills"
set "PROJECT_ROOT=%~1"
if "%PROJECT_ROOT%"=="" set "PROJECT_ROOT=%CD%"
set "PROJECT_SKILLS=%PROJECT_ROOT%\.agents\skills"
set "USER_SKILLS=%USERPROFILE%\.agents\skills"
set "CURSOR_SKILLS=%USERPROFILE%\.cursor\skills"
set "CODEX_SKILLS=%USERPROFILE%\.codex\skills"
set "GEMINI_SKILLS=%USERPROFILE%\.gemini\config\skills"
set "WORKBUDDY_SKILLS=%USERPROFILE%\.workbuddy\skills"

if not exist "%REPO%" (
  echo [ERROR] Cannot find repository skills directory: %REPO%
  exit /b 1
)

for %%D in ("%PROJECT_SKILLS%" "%USER_SKILLS%" "%CURSOR_SKILLS%" "%CODEX_SKILLS%" "%GEMINI_SKILLS%" "%WORKBUDDY_SKILLS%") do (
  if not exist "%%~D" mkdir "%%~D"
  echo Syncing to %%~D
  robocopy "%REPO%" "%%~D" /E /XD .git /NFL /NDL /NJH /NJS /NP
  if errorlevel 8 (
    echo [ERROR] Sync failed: %%~D
    exit /b 1
  )
)

echo.
echo [OK] Skills synced from:
echo      %REPO%
echo [OK] Project skills:
echo      %PROJECT_SKILLS%
echo [OK] Cursor skills:
echo      %CURSOR_SKILLS%
endlocal
