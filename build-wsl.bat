@echo off
REM ==========================================================
REM        RIDA OS - 1-Click Windows ISO Builder (WSL2)
REM ==========================================================

echo Checking WSL status...
wsl --status >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [!] Error: WSL2 is not enabled or installed on this system.
    echo     Run 'wsl --install' in PowerShell, or use Docker via build.bat.
    pause
    exit /b 1
)

echo Launching RIDA OS build inside WSL...
wsl -u root bash -c "cd $(wslpath '%cd%') && chmod +x builder/build-wsl.sh && ./builder/build-wsl.sh"

pause
