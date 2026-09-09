@echo off
REM ==========================================================
REM        RIDA OS - 1-Click Windows ISO Builder (Docker)
REM ==========================================================

echo [1/3] Checking Docker Desktop status...
docker info >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [!] Error: Docker is not running or not installed.
    echo     Please ensure Docker Desktop is started.
    echo     Alternatively, run build-wsl.bat to build via Windows Subsystem for Linux.
    pause
    exit /b 1
)

echo [2/3] Building RIDA OS Build Container Image...
docker build -t rida-os-builder -f builder\Dockerfile.builder .
if %ERRORLEVEL% NEQ 0 (
    echo [!] Failed to create builder container image.
    pause
    exit /b 1
)

echo [3/3] Running RIDA OS ISO Compilation...
echo     (Privileged mode is required for debootstrap, loop mounts, and xorriso)
mkdir output 2>nul
docker run --rm --privileged -v "%cd%:/workspace" rida-os-builder

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ==========================================================
    echo [OK] Build Complete! Your ISO is ready in the output\ folder:
    dir output\*.iso
    echo ==========================================================
) else (
    echo [!] Build encountered errors. Please inspect output\build.log
)

pause
