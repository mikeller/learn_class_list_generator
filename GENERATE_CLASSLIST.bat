@echo off
title UC Learn Class List Generator
cls

echo ===============================================================
echo  UC LEARN CLASS LIST GENERATOR - SELF-CONTAINED
echo ===============================================================
echo.
echo This version downloads and sets up portable Python automatically.
echo.

REM Check if portable Python exists
set PORTABLE_PYTHON_DIR=%~dp0python-portable
set PORTABLE_PYTHON=%PORTABLE_PYTHON_DIR%\python.exe

if exist "%PORTABLE_PYTHON%" (
    echo [INFO] Portable Python found
    goto :run_scraper
)

echo [INFO] Setting up portable Python environment...
echo [INFO] This will download about 30MB and only happens once.
echo.

REM Create directory
if not exist "%PORTABLE_PYTHON_DIR%" mkdir "%PORTABLE_PYTHON_DIR%"

REM Download Python
echo [STEP 1/4] Downloading Python 3.11...
set PYTHON_URL=https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip
set PYTHON_ZIP=%~dp0python-portable.zip

powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%PYTHON_ZIP%' -UserAgent 'Mozilla/5.0'"

if not exist "%PYTHON_ZIP%" (
    echo [ERROR] Download failed. Check internet connection.
    pause
    exit /b 1
)

echo [STEP 2/4] Extracting Python...
powershell -Command "Add-Type -AssemblyName System.IO.Compression.FileSystem; [System.IO.Compression.ZipFile]::ExtractToDirectory('%PYTHON_ZIP%', '%PORTABLE_PYTHON_DIR%')"
del "%PYTHON_ZIP%"

echo [STEP 3/4] Setting up pip...
REM Modify the existing pth file to enable site packages and pip
echo python311.zip > "%PORTABLE_PYTHON_DIR%\python311._pth"
echo . >> "%PORTABLE_PYTHON_DIR%\python311._pth"
echo. >> "%PORTABLE_PYTHON_DIR%\python311._pth"
echo # Uncomment to run site.main() automatically >> "%PORTABLE_PYTHON_DIR%\python311._pth"
echo import site >> "%PORTABLE_PYTHON_DIR%\python311._pth"

set GET_PIP_URL=https://bootstrap.pypa.io/get-pip.py
set GET_PIP_FILE=%~dp0get-pip.py
powershell -Command "Invoke-WebRequest -Uri '%GET_PIP_URL%' -OutFile '%GET_PIP_FILE%'"
"%PORTABLE_PYTHON%" "%GET_PIP_FILE%" --no-warn-script-location
del "%GET_PIP_FILE%"

echo [STEP 4/4] Installing packages...
"%PORTABLE_PYTHON%" -m pip install selenium==4.15.0 --quiet

echo [SUCCESS] Setup complete!

:run_scraper
echo.
echo ===============================================================
echo  RUNNING SCRAPER
echo ===============================================================

if not exist "%~dp0scraper_python3_self_contained.py" (
    echo [ERROR] Scraper file not found
    pause
    exit /b 1
)

echo [INFO] Starting scraper...
"%PORTABLE_PYTHON%" "%~dp0scraper_python3_self_contained.py"

echo.
if exist "%~dp0participants.json" (
    echo [SUCCESS] Class list generated: participants.json
    notepad "%~dp0participants.json"
) else (
    echo [WARNING] No output file found
)

pause
