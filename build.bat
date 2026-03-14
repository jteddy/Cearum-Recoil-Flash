@echo off
echo ================================
echo  Cearum Build Script
echo ================================

:: Move to the script's directory regardless of where it's run from
cd /d "%~dp0"

:: Create venv if it doesn't exist
if not exist build_env (
    echo Creating virtual environment...
    python -m venv build_env
)

:: Activate venv
call build_env\Scripts\activate

:: Install / upgrade dependencies
echo Installing dependencies...
pip install --quiet --upgrade customtkinter pillow makcu pyinstaller

:: Clean previous build
echo Cleaning previous build...
if exist output\Cearum.exe del /f output\Cearum.exe
if exist build rmdir /s /q build

:: Ensure output directory exists
if not exist output mkdir output

:: Build
echo Building Cearum.exe...
pyinstaller --onefile --noconsole --name Cearum ^
  --distpath output ^
  --exclude-module matplotlib ^
  --exclude-module numpy ^
  --exclude-module pandas ^
  --exclude-module scipy ^
  --exclude-module unittest ^
  --exclude-module email ^
  --exclude-module http ^
  --exclude-module xml ^
  --exclude-module pydoc ^
  main.pyw

:: Check result
if exist output\Cearum.exe (
    echo.
    echo ================================
    echo  Build successful!
    echo  Output: output\Cearum.exe
    echo ================================
) else (
    echo.
    echo ================================
    echo  Build FAILED - check errors above
    echo ================================
)

pause
