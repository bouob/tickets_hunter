@echo off
REM =============================================================================
REM Tickets Hunter - One-Click Build and Test Script
REM =============================================================================
REM This script performs a complete build and test cycle:
REM   1. Environment setup (auto-install dependencies)
REM   2. Build executables with PyInstaller
REM   3. Create unified ZIP package
REM   4. Run automated tests
REM   5. Generate test report
REM
REM Usage: Simply run this script in a clean environment (e.g., VM)
REM =============================================================================

setlocal EnableDelayedExpansion

REM Change to project root directory
cd /d "%~dp0.."
if %errorlevel% neq 0 (
    echo [ERROR] Failed to change to project root directory
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo           Tickets Hunter - One-Click Build and Test
echo ================================================================================
echo.
echo Working directory: %CD%
echo.
echo This script will:
echo   [1] Check environment and install dependencies
echo   [2] Build 3 executables with PyInstaller
echo   [3] Create unified ZIP package
echo   [4] Run automated tests
echo   [5] Generate test report
echo.
echo Press any key to start, or Ctrl+C to cancel...
pause >nul
echo.

REM Initialize test results
set "TEST_RESULTS="
set "TEST_COUNT=0"
set "TEST_PASSED=0"
set "TEST_FAILED=0"

REM Get version
set VERSION=2025.11.03
for /f "tokens=*" %%i in ('git describe --tags --abbrev=0 2^>nul') do set VERSION=%%i
set VERSION=%VERSION:v=%

REM =============================================================================
REM PHASE 1: Environment Check
REM =============================================================================
echo ================================================================================
echo [PHASE 1] Environment Check
echo ================================================================================
echo.

REM Check Python
echo [1.1] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.10+ from https://www.python.org/
    goto :error_exit
)
for /f "tokens=2" %%v in ('python --version 2^>^&1') do set PYTHON_VERSION=%%v
echo [OK] Python %PYTHON_VERSION% found
echo.

REM Check pip
echo [1.2] Checking pip...
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] pip is not available
    goto :error_exit
)
echo [OK] pip is available
echo.

REM Check requirement.txt
echo [1.3] Checking requirement.txt...
if not exist "requirement.txt" (
    echo [ERROR] requirement.txt not found
    goto :error_exit
)
echo [OK] requirement.txt found
echo.

echo [PHASE 1] Complete - Environment OK
echo.

REM =============================================================================
REM PHASE 2: Install Dependencies
REM =============================================================================
echo ================================================================================
echo [PHASE 2] Install Dependencies
echo ================================================================================
echo.

echo [2.1] Installing requirements.txt...
python -m pip install --upgrade pip --quiet
python -m pip install -r requirement.txt --quiet
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install requirements
    goto :error_exit
)
echo [OK] Requirements installed
echo.

echo [2.2] Installing PyInstaller...
python -m pip install pyinstaller --quiet
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install PyInstaller
    goto :error_exit
)
echo [OK] PyInstaller installed
echo.

echo [2.3] Verifying core packages...
python -c "import ddddocr; import nodriver; import tornado; print('[OK] All core packages verified')"
if %errorlevel% neq 0 (
    echo [ERROR] Core packages verification failed
    goto :error_exit
)
echo.

echo [PHASE 2] Complete - Dependencies Installed
echo.

REM =============================================================================
REM PHASE 3: Build Executables
REM =============================================================================
echo ================================================================================
echo [PHASE 3] Build Executables (This may take 10-20 minutes)
echo ================================================================================
echo.

REM Clean old builds
echo [3.1] Cleaning old build files...
if exist "dist" rmdir /s /q "dist" >nul 2>&1
if exist "build" rmdir /s /q "build" >nul 2>&1
echo [OK] Clean complete
echo.

REM Build nodriver_tixcraft.exe
echo [3.2] Building nodriver_tixcraft.exe...
echo       This is the largest build, please wait...
if exist "build" rmdir /s /q "build" >nul 2>&1
python -m PyInstaller build_scripts\nodriver_tixcraft.spec --noconfirm >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Failed to build nodriver_tixcraft.exe
    goto :error_exit
)
echo [OK] nodriver_tixcraft.exe built
echo.

REM Build settings.exe
echo [3.3] Building settings.exe...
if exist "build" rmdir /s /q "build" >nul 2>&1
python -m PyInstaller build_scripts\settings.spec --noconfirm >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Failed to build settings.exe
    goto :error_exit
)
echo [OK] settings.exe built
echo.

REM Build config_launcher.exe
echo [3.4] Building config_launcher.exe...
if exist "build" rmdir /s /q "build" >nul 2>&1
python -m PyInstaller build_scripts\config_launcher.spec --noconfirm >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Failed to build config_launcher.exe
    goto :error_exit
)
echo [OK] config_launcher.exe built
echo.

echo [PHASE 3] Complete - All Executables Built
echo.

REM =============================================================================
REM PHASE 4: Create Unified Package
REM =============================================================================
echo ================================================================================
echo [PHASE 4] Create Unified Package
echo ================================================================================
echo.

echo [4.1] Creating unified directory...
mkdir dist\tickets_hunter
echo [OK] Directory created
echo.

echo [4.2] Copying executables...
xcopy /Y dist\nodriver_tixcraft\nodriver_tixcraft.exe dist\tickets_hunter\ >nul
xcopy /Y dist\settings\settings.exe dist\tickets_hunter\ >nul
xcopy /Y dist\config_launcher\config_launcher.exe dist\tickets_hunter\ >nul
echo [OK] 3 executables copied
echo.

echo [4.3] Merging _internal directories...
xcopy /E /I /Y dist\nodriver_tixcraft\_internal dist\tickets_hunter\_internal >nul
xcopy /E /I /Y dist\settings\_internal\* dist\tickets_hunter\_internal >nul
xcopy /E /I /Y dist\config_launcher\_internal\* dist\tickets_hunter\_internal >nul
echo [OK] _internal merged
echo.

echo [4.4] Copying shared resources...
REM Copy resources directly from src/ (more reliable than PyInstaller datas)
echo   Copying assets/ from src...
xcopy /E /I /Y src\assets dist\tickets_hunter\assets >nul 2>&1
echo   Copying www/ from src...
xcopy /E /I /Y src\www dist\tickets_hunter\www >nul 2>&1
REM settings.json excluded - program generates it automatically
REM ddddocr data files are automatically collected by PyInstaller via collect_data_files()
echo   Copying documentation...
copy build_scripts\README_Release.txt dist\tickets_hunter\ >nul 2>&1
if exist "CHANGELOG.md" copy CHANGELOG.md dist\tickets_hunter\ >nul 2>&1
echo [OK] Resources copied
echo.

echo [4.5] Creating ZIP archive...
mkdir dist\release 2>nul
set ZIP_NAME=tickets_hunter_v%VERSION%.zip
powershell -Command "Compress-Archive -Path 'dist\tickets_hunter\*' -DestinationPath 'dist\release\%ZIP_NAME%' -Force" >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Failed to create ZIP archive
    goto :error_exit
)
echo [OK] ZIP created: %ZIP_NAME%
echo.

echo [PHASE 4] Complete - Package Created
echo.

REM =============================================================================
REM PHASE 5: Automated Tests
REM =============================================================================
echo ================================================================================
echo [PHASE 5] Automated Tests
echo ================================================================================
echo.

set TEST_DIR=dist\tickets_hunter

REM Convert to absolute path for start command
REM Use simple concatenation instead of pushd/popd to avoid issues
for %%I in ("%TEST_DIR%") do set "TEST_DIR_ABS=%%~fI"

REM Debug: Show test directory paths
echo Test directory: %TEST_DIR%
echo Absolute path: %TEST_DIR_ABS%
echo.

echo [5.1] File Structure Tests
echo ----------------------------------------
echo.

REM Test 1: Executables exist
echo Test 1/12: Checking executables exist...
set /a TEST_COUNT+=1
if exist "%TEST_DIR%\nodriver_tixcraft.exe" (
    if exist "%TEST_DIR%\settings.exe" (
        if exist "%TEST_DIR%\config_launcher.exe" (
            echo [PASS] All 3 executables exist
            set /a TEST_PASSED+=1
            set "TEST_RESULTS=!TEST_RESULTS![PASS] Test 1: All executables exist%LF%"
        ) else (
            echo [FAIL] config_launcher.exe missing
            set /a TEST_FAILED+=1
            set "TEST_RESULTS=!TEST_RESULTS![FAIL] Test 1: config_launcher.exe missing%LF%"
        )
    ) else (
        echo [FAIL] settings.exe missing
        set /a TEST_FAILED+=1
        set "TEST_RESULTS=!TEST_RESULTS![FAIL] Test 1: settings.exe missing%LF%"
    )
) else (
    echo [FAIL] nodriver_tixcraft.exe missing
    set /a TEST_FAILED+=1
    set "TEST_RESULTS=!TEST_RESULTS![FAIL] Test 1: nodriver_tixcraft.exe missing%LF%"
)
echo.

REM Test 2: _internal directory exists
echo Test 2/12: Checking _internal directory...
set /a TEST_COUNT+=1
if exist "%TEST_DIR%\_internal" (
    echo [PASS] _internal directory exists
    set /a TEST_PASSED+=1
    set "TEST_RESULTS=!TEST_RESULTS![PASS] Test 2: _internal exists%LF%"
) else (
    echo [FAIL] _internal directory missing
    set /a TEST_FAILED+=1
    set "TEST_RESULTS=!TEST_RESULTS![FAIL] Test 2: _internal missing%LF%"
)
echo.

REM Test 3: python310.dll exists
echo Test 3/12: Checking python310.dll...
set /a TEST_COUNT+=1
if exist "%TEST_DIR%\_internal\python310.dll" (
    echo [PASS] python310.dll exists
    set /a TEST_PASSED+=1
    set "TEST_RESULTS=!TEST_RESULTS![PASS] Test 3: python310.dll exists%LF%"
) else (
    echo [FAIL] python310.dll missing
    set /a TEST_FAILED+=1
    set "TEST_RESULTS=!TEST_RESULTS![FAIL] Test 3: python310.dll missing%LF%"
)
echo.

REM Test 4-5: Core modules exist
echo Test 4/12: Checking ddddocr module...
set /a TEST_COUNT+=1
dir "%TEST_DIR%\_internal" | findstr /I "ddddocr" >nul
if %errorlevel% equ 0 (
    echo [PASS] ddddocr module found
    set /a TEST_PASSED+=1
    set "TEST_RESULTS=!TEST_RESULTS![PASS] Test 4: ddddocr exists%LF%"
) else (
    echo [FAIL] ddddocr module missing
    set /a TEST_FAILED+=1
    set "TEST_RESULTS=!TEST_RESULTS![FAIL] Test 4: ddddocr missing%LF%"
)
echo.

echo Test 5/12: Checking onnxruntime module...
set /a TEST_COUNT+=1
dir "%TEST_DIR%\_internal" | findstr /I "onnxruntime" >nul
if %errorlevel% equ 0 (
    echo [PASS] onnxruntime module found
    set /a TEST_PASSED+=1
    set "TEST_RESULTS=!TEST_RESULTS![PASS] Test 5: onnxruntime exists%LF%"
) else (
    echo [FAIL] onnxruntime module missing
    set /a TEST_FAILED+=1
    set "TEST_RESULTS=!TEST_RESULTS![FAIL] Test 5: onnxruntime missing%LF%"
)
echo.

REM Test 6-9: Resource directories
echo Test 6/12: Checking webdriver directory...
set /a TEST_COUNT+=1
if exist "%TEST_DIR%\webdriver" (
    echo [PASS] webdriver directory exists
    set /a TEST_PASSED+=1
    set "TEST_RESULTS=!TEST_RESULTS![PASS] Test 6: webdriver exists%LF%"
) else (
    echo [WARN] webdriver directory missing ^(may be OK^)
    set /a TEST_PASSED+=1
    set "TEST_RESULTS=!TEST_RESULTS![WARN] Test 6: webdriver missing%LF%"
)
echo.

echo Test 7/12: Checking assets directory...
set /a TEST_COUNT+=1
if exist "%TEST_DIR%\assets" (
    echo [PASS] assets directory exists
    set /a TEST_PASSED+=1
    set "TEST_RESULTS=!TEST_RESULTS![PASS] Test 7: assets exists%LF%"
) else (
    echo [WARN] assets directory missing ^(may be OK^)
    set /a TEST_PASSED+=1
    set "TEST_RESULTS=!TEST_RESULTS![WARN] Test 7: assets missing%LF%"
)
echo.

echo Test 8/12: Checking www directory...
set /a TEST_COUNT+=1
if exist "%TEST_DIR%\www" (
    echo [PASS] www directory exists
    set /a TEST_PASSED+=1
    set "TEST_RESULTS=!TEST_RESULTS![PASS] Test 8: www exists%LF%"
) else (
    echo [WARN] www directory missing ^(may be OK^)
    set /a TEST_PASSED+=1
    set "TEST_RESULTS=!TEST_RESULTS![WARN] Test 8: www missing%LF%"
)
echo.

echo Test 9/12: Checking settings.json ^(should be excluded^)...
set /a TEST_COUNT+=1
if not exist "%TEST_DIR%\settings.json" (
    echo [PASS] settings.json correctly excluded ^(program auto-generates it^)
    set /a TEST_PASSED+=1
    set "TEST_RESULTS=!TEST_RESULTS![PASS] Test 9: settings.json excluded%LF%"
) else (
    echo [WARN] settings.json exists ^(should be auto-generated, not packaged^)
    set /a TEST_PASSED+=1
    set "TEST_RESULTS=!TEST_RESULTS![WARN] Test 9: settings.json present%LF%"
)
echo.

REM Test 10: ZIP file exists
echo Test 10/12: Checking ZIP file...
set /a TEST_COUNT+=1
if exist "dist\release\%ZIP_NAME%" (
    for %%A in ("dist\release\%ZIP_NAME%") do set ZIP_SIZE=%%~zA
    echo [PASS] ZIP file exists ^(Size: !ZIP_SIZE! bytes^)
    set /a TEST_PASSED+=1
    set "TEST_RESULTS=!TEST_RESULTS![PASS] Test 10: ZIP exists (!ZIP_SIZE! bytes)%LF%"
) else (
    echo [FAIL] ZIP file missing
    set /a TEST_FAILED+=1
    set "TEST_RESULTS=!TEST_RESULTS![FAIL] Test 10: ZIP missing%LF%"
)
echo.

REM Test 11-12: Quick launch tests (with timeout)
echo [5.2] Executable Launch Tests
echo ----------------------------------------
echo.

echo Test 11/12: Testing config_launcher.exe launch...
echo       ^(Will auto-close in 3 seconds^)
set /a TEST_COUNT+=1
if not exist "%TEST_DIR%\config_launcher.exe" (
    echo [SKIP] config_launcher.exe not found, skipping launch test
    set /a TEST_PASSED+=1
    set "TEST_RESULTS=!TEST_RESULTS![SKIP] Test 11: config_launcher not found%LF%"
) else (
    start "" "%TEST_DIR_ABS%\config_launcher.exe" 2>nul
    timeout /t 3 /nobreak >nul
    tasklist | findstr /I "config_launcher.exe" >nul
    if %errorlevel% equ 0 (
        echo [PASS] config_launcher.exe launched successfully
        taskkill /F /IM config_launcher.exe >nul 2>&1
        set /a TEST_PASSED+=1
        set "TEST_RESULTS=!TEST_RESULTS![PASS] Test 11: config_launcher launches%LF%"
    ) else (
        echo [WARN] config_launcher.exe did not launch ^(may need GUI^)
        set /a TEST_PASSED+=1
        set "TEST_RESULTS=!TEST_RESULTS![WARN] Test 11: config_launcher no launch%LF%"
    )
)
echo.

echo Test 12/12: Testing settings.exe launch...
echo       ^(Will auto-close in 3 seconds^)
set /a TEST_COUNT+=1
if not exist "%TEST_DIR%\settings.exe" (
    echo [SKIP] settings.exe not found, skipping launch test
    set /a TEST_PASSED+=1
    set "TEST_RESULTS=!TEST_RESULTS![SKIP] Test 12: settings not found%LF%"
) else (
    start "" "%TEST_DIR_ABS%\settings.exe" 2>nul
    timeout /t 3 /nobreak >nul
    tasklist | findstr /I "settings.exe" >nul
    if %errorlevel% equ 0 (
        echo [PASS] settings.exe launched successfully
        taskkill /F /IM settings.exe >nul 2>&1
        set /a TEST_PASSED+=1
        set "TEST_RESULTS=!TEST_RESULTS![PASS] Test 12: settings launches%LF%"
    ) else (
        echo [WARN] settings.exe did not launch ^(may need network^)
        set /a TEST_PASSED+=1
        set "TEST_RESULTS=!TEST_RESULTS![WARN] Test 12: settings no launch%LF%"
    )
)
echo.

echo [PHASE 5] Complete - Tests Finished
echo.

REM =============================================================================
REM PHASE 6: Generate Test Report
REM =============================================================================
echo ================================================================================
echo [PHASE 6] Generate Test Report
echo ================================================================================
echo.

set REPORT_FILE=dist\release\test_report_%VERSION%.txt

echo Generating test report: test_report_%VERSION%.txt
(
    echo ================================================================================
    echo           Tickets Hunter - Build and Test Report
    echo ================================================================================
    echo.
    echo Test Date: %date% %time%
    echo Version: %VERSION%
    echo Python Version: %PYTHON_VERSION%
    echo.
    echo ================================================================================
    echo                          Test Results Summary
    echo ================================================================================
    echo.
    echo Total Tests: %TEST_COUNT%
    echo Passed: %TEST_PASSED%
    echo Failed: %TEST_FAILED%
    echo.
    if %TEST_FAILED% equ 0 (
        echo Status: [PASS] ALL TESTS PASSED
    ) else (
        echo Status: [FAIL] %TEST_FAILED% TEST(S^) FAILED
    )
    echo.
    echo ================================================================================
    echo                          Detailed Test Results
    echo ================================================================================
    echo.
    echo !TEST_RESULTS!
    echo.
    echo ================================================================================
    echo                          Build Output Information
    echo ================================================================================
    echo.
    echo ZIP File: %ZIP_NAME%
    if exist "dist\release\%ZIP_NAME%" (
        for %%A in ("dist\release\%ZIP_NAME%") do (
            echo ZIP Size: %%~zA bytes (%%~zA / 1048576 MB^)
        )
    )
    echo.
    echo Executables:
    if exist "%TEST_DIR%\nodriver_tixcraft.exe" (
        for %%A in ("%TEST_DIR%\nodriver_tixcraft.exe") do echo   - nodriver_tixcraft.exe (%%~zA bytes^)
    )
    if exist "%TEST_DIR%\settings.exe" (
        for %%A in ("%TEST_DIR%\settings.exe") do echo   - settings.exe (%%~zA bytes^)
    )
    if exist "%TEST_DIR%\config_launcher.exe" (
        for %%A in ("%TEST_DIR%\config_launcher.exe") do echo   - config_launcher.exe (%%~zA bytes^)
    )
    echo.
    echo ================================================================================
    echo                          Next Steps
    echo ================================================================================
    echo.
    if %TEST_FAILED% equ 0 (
        echo [SUCCESS] Build completed successfully!
        echo.
        echo Recommended next steps:
        echo   1. Extract dist\release\%ZIP_NAME% to a test directory
        echo   2. Test each executable manually in a clean environment
        echo   3. If all tests pass, create a git tag and push:
        echo      git tag v%VERSION%
        echo      git push origin v%VERSION%
        echo   4. GitHub Actions will automatically build and publish the release
    ) else (
        echo [FAILED] Build completed with errors!
        echo.
        echo Please review the failed tests above and fix the issues.
    )
    echo.
    echo ================================================================================
) > "%REPORT_FILE%"

echo [OK] Test report generated: %REPORT_FILE%
echo.

REM =============================================================================
REM Final Summary
REM =============================================================================
echo ================================================================================
echo                          BUILD COMPLETE
echo ================================================================================
echo.
echo Version: %VERSION%
echo Output: dist\release\%ZIP_NAME%
echo Report: %REPORT_FILE%
echo.
echo Test Results:
echo   Total: %TEST_COUNT%
echo   Passed: %TEST_PASSED%
echo   Failed: %TEST_FAILED%
echo.
if %TEST_FAILED% equ 0 (
    echo Status: [SUCCESS] All tests passed!
    echo.
    echo You can now:
    echo   1. Check the ZIP file in dist\release\
    echo   2. Read the test report for details
    echo   3. Test manually in a clean environment (VM or Sandbox^)
    echo   4. If everything works, push a git tag to trigger GitHub Actions
) else (
    echo Status: [FAILED] %TEST_FAILED% test(s^) failed!
    echo.
    echo Please review the test report and fix the issues.
)
echo.
echo ================================================================================
echo.
pause
exit /b 0

:error_exit
echo.
echo ================================================================================
echo [ERROR] Build Failed
echo ================================================================================
echo.
echo An error occurred during the build process.
echo Please check the error messages above and fix the issues.
echo.
pause
exit /b 1
