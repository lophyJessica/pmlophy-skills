@echo off
setlocal EnableExtensions

rem Windows skill junction setup
rem Source of truth: pmlophy-skills\.agents\skills

set "REPO=%~dp0.agents\skills"
if not exist "%REPO%" set "REPO=%~dp0skills"
set "USER_SKILLS=%USERPROFILE%\.agents\skills"
set "CURSOR_SKILLS=%USERPROFILE%\.cursor\skills"
set "CODEX_SKILLS=%USERPROFILE%\.codex\skills"
set "GEMINI_SKILLS=%USERPROFILE%\.gemini\config\skills"
set "WORKBUDDY_SKILLS=%USERPROFILE%\.workbuddy\skills"

if not exist "%REPO%" (
  echo [ERROR] Cannot find skill source: %REPO%
  exit /b 1
)

call :ensure_junction "%USER_SKILLS%" "%REPO%"
call :ensure_junction "%CURSOR_SKILLS%" "%USER_SKILLS%"
call :ensure_junction "%CODEX_SKILLS%" "%USER_SKILLS%"
call :ensure_junction "%GEMINI_SKILLS%" "%USER_SKILLS%"
call :ensure_junction "%WORKBUDDY_SKILLS%" "%USER_SKILLS%"

echo.
echo [OK] Skill source: %REPO%
echo [OK] User skill junction: %USER_SKILLS%
echo [OK] Cursor skill junction: %CURSOR_SKILLS%
exit /b 0

:ensure_junction
set "LINK=%~1"
set "TARGET=%~2"
if exist "%LINK%" (
  echo [KEEP] Existing path: %LINK%
  echo        If it is not a junction to the target, fix it manually after checking.
  exit /b 0
)
for %%P in ("%LINK%") do if not exist "%%~dpP" mkdir "%%~dpP"
mklink /J "%LINK%" "%TARGET%"
if errorlevel 1 (
  echo [ERROR] Failed to create junction: %LINK%
  exit /b 1
)
echo [LINK] %LINK% ^> %TARGET%
exit /b 0
