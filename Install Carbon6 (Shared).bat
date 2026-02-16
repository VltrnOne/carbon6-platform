@echo off
REM ============================================================================
REM Carbon6 OiS - Windows Single-Click Installer (Shared/Network)
REM
REM Double-click this file to install Carbon6 for all users on your PC
REM with network accessibility.
REM
REM Installation Location: C:\Carbon6
REM Data Location: C:\ProgramData\Carbon6
REM Network Access: http://YOUR-PC-NAME:3006
REM
REM REQUIRES: Administrator privileges
REM ============================================================================

REM Check for admin privileges
net session >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo.
    echo ========================================================================
    echo.
    echo      ERROR: Administrator privileges required
    echo.
    echo ========================================================================
    echo.
    echo This installer must be run as Administrator.
    echo.
    echo Right-click this file and select "Run as administrator"
    echo.
    pause
    exit /b 1
)

color 0B
cls
echo.
echo ========================================================================
echo.
echo      CARBON6 OiS - SHARED INSTALLER
echo.
echo      Multi-User ^| Network-Ready ^| Centralized
echo.
echo ========================================================================
echo.
echo This installer will:
echo   * Install Carbon6 to C:\Carbon6 (all users can access)
echo   * Configure for network access from other computers
echo   * Install Chocolatey, Bun, PostgreSQL, Memurai (Redis)
echo   * Create desktop shortcut for all users
echo.
echo Installation time: 15-20 minutes
echo.
pause

echo.
echo [1/1] Downloading and running installer...
echo.

REM Run PowerShell installer as admin
powershell -NoProfile -ExecutionPolicy Bypass -Command "iex ((New-Object System.Net.WebClient).DownloadString('https://raw.githubusercontent.com/VltrnOne/carbon6-platform/main/install-carbon6-windows-shared.ps1'))"

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
    echo      Double-click "Carbon6 OiS" on desktop
    echo      OR
    echo      C:\Carbon6\start.bat
    echo.
    echo   2. Access from this PC:
    echo      http://localhost:3006
    echo.
    echo   3. Access from other computers:
    echo      http://%COMPUTERNAME%:3006
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
