@echo off
title SmartDesk Build
echo ============================================================
echo   SmartDesk — Repackage to .exe
echo ============================================================
echo.

:: Activate virtual environment
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo [WARNING] Virtual environment not found. Using system Python.
)

:: Step 1: Generate icon if missing
if not exist "assets\icon.ico" (
    echo [1/4] Generating application icon...
    python scripts\generate_icon.py
) else (
    echo [1/4] Icon already exists.
)

:: Step 2: Train ML model if missing
if not exist "app\ml\models\clause_classifier.pkl" (
    echo [2/4] Training clause classifier model...
    python scripts\train_clause_model.py
) else (
    echo [2/4] ML model already trained.
)

:: Step 3: Run PyInstaller
echo [3/4] Building executable with PyInstaller...
echo       This may take 2-5 minutes...
if exist "smartdesk.spec" (
    pyinstaller smartdesk.spec --noconfirm --clean
) else (
    pyinstaller solodash.spec --noconfirm --clean
)
if errorlevel 1 (
    echo.
    echo [ERROR] PyInstaller build failed!
    pause
    exit /b 1
)

:: Step 4: Create runtime directories in dist
echo [4/4] Setting up distribution folder...
if not exist "dist\SmartDesk\data" mkdir "dist\SmartDesk\data"
if not exist "dist\SmartDesk\exports" mkdir "dist\SmartDesk\exports"

echo.
echo ============================================================
echo   BUILD COMPLETE
echo ============================================================
echo.
echo   Output:     dist\SmartDesk\
echo   Executable: dist\SmartDesk\SmartDesk.exe
echo.
echo   To run: double-click SmartDesk.exe
echo   To distribute: zip the entire SmartDesk folder
echo.
pause
