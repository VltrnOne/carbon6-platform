@echo off
REM ============================================================================
REM Carbon6 OiS - Windows Single-Click Installer (Personal)
REM
REM Double-click this file to install Carbon6 in your user directory
REM for personal development use.
REM
REM Installation Location: C:\Users\YourName\Carbon6
REM Access: localhost only (this PC only)
REM ============================================================================

color 0B
cls
echo.
echo ========================================================================
echo.
echo      CARBON6 OiS - PERSONAL INSTALLER
echo.
echo      Single User ^| Development ^| Fast Setup
echo.
echo ========================================================================
echo.
echo This installer will:
echo   * Install Carbon6 to %USERPROFILE%\Carbon6
echo   * Install Chocolatey, Bun, PostgreSQL, Memurai (Redis)
echo   * Configure for localhost access only
echo.
echo Installation time: 15-20 minutes
echo.
pause

echo.
echo [1/1] Downloading and running installer...
echo.

REM Run PowerShell installer
powershell -NoProfile -ExecutionPolicy Bypass -Command "iex ((New-Object System.Net.WebClient).DownloadString('https://raw.githubusercontent.com/VltrnOne/carbon6-platform/main/install-carbon6-windows.ps1'))"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================================================
    echo.
    echo      INSTALLATION COMPLETE!
    echo.
    echo ========================================================================
    echo.
    echo Quick Start:
    echo.
    echo   1. Start server:
    echo      cd %USERPROFILE%\Carbon6
    echo      .\start.bat
    echo.
    echo   2. Access:
    echo      http://localhost:3006
    echo.
) else (
    echo.
    echo ========================================================================
    echo.
    echo      INSTALLATION FAILED
    echo.
    echo ========================================================================
    echo.
    echo Check the error messages above for details.
    echo.
)

echo.
pause
