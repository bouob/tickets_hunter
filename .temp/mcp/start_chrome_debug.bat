@echo off
chcp 65001 >nul 2>&1

:: ============================================================
:: Chrome Debug Mode Launcher for MCP Integration
:: ============================================================

set PORT=9222

:: Get the project root directory
pushd "%~dp0..\.."
set "PROJECT_ROOT=%CD%"
popd

set "PROFILE_DIR=%PROJECT_ROOT%\.temp\chrome-debug-profile"

:: Check if Chrome is already running on the specified port
netstat -ano | findstr ":%PORT% " | findstr "LISTENING" >nul 2>&1
if %errorlevel%==0 goto :already_running

:: Find Chrome executable
set "CHROME_PATH="
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" set "CHROME_PATH=C:\Program Files\Google\Chrome\Application\chrome.exe"
if "%CHROME_PATH%"=="" if exist "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" set "CHROME_PATH=C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
if "%CHROME_PATH%"=="" if exist "%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe" set "CHROME_PATH=%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"

if "%CHROME_PATH%"=="" goto :no_chrome

:: Create profile directory if it doesn't exist
if not exist "%PROFILE_DIR%" mkdir "%PROFILE_DIR%"

:: Launch Chrome with remote debugging
echo [INFO] Starting Chrome with remote debugging on port %PORT%...
echo [INFO] Profile dir: %PROFILE_DIR%

start "" "%CHROME_PATH%" --remote-debugging-port=%PORT% --user-data-dir="%PROFILE_DIR%" --no-first-run --no-default-browser-check --disable-background-networking --disable-default-apps --disable-sync --remote-allow-origins=* about:blank

:: Wait a moment for Chrome to start
timeout /t 2 /nobreak >nul

:: Verify Chrome started successfully
netstat -ano | findstr ":%PORT% " | findstr "LISTENING" >nul 2>&1
if %errorlevel%==0 goto :success
goto :failed

:already_running
echo [INFO] Chrome is already running on port %PORT%
echo [INFO] You can now connect with: --mcp_connect %PORT%
goto :end

:no_chrome
echo [ERROR] Chrome executable not found!
goto :end

:success
echo.
echo [SUCCESS] Chrome started successfully on port %PORT%
echo.
echo Next steps:
echo   1. Run NoDriver with: python src/nodriver_tixcraft.py --input src/settings.json --mcp_connect %PORT%
echo   2. MCP tools should connect automatically via .mcp.json
echo.
goto :end

:failed
echo [WARNING] Chrome may not have started correctly.
echo [WARNING] Please check if port %PORT% is available.
goto :end

:end
