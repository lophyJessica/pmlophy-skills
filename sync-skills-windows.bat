@echo off
setlocal EnableExtensions

rem Windows skill sync script
rem Run from the pmlophy-skills repository root after pulling it.

set "REPO=%~dp0skills"
set "USER_SKILLS=%USERPROFILE%\.agents\skills"
set "CURSOR_SKILLS=%USERPROFILE%\.cursor\skills"
set "CODEX_SKILLS=%USERPROFILE%\.codex\skills"
set "GEMINI_SKILLS=%USERPROFILE%\.gemini\config\skills"
set "WORKBUDDY_SKILLS=%USERPROFILE%\.workbuddy\skills"

if not exist "%REPO%" (
  echo [ERROR] Cannot find repository skills directory: %REPO%
  exit /b 1
)

for %%D in ("%USER_SKILLS%" "%CURSOR_SKILLS%" "%CODEX_SKILLS%" "%GEMINI_SKILLS%" "%WORKBUDDY_SKILLS%") do (
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
echo [OK] Cursor skills:
echo      %CURSOR_SKILLS%
endlocal
