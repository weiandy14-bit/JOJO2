@echo off

echo ============================================================
echo  Quotation Extractor - Build Script
echo ============================================================
echo.

echo [1/2] Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: pip install failed. Please check your Python environment.
    pause
    exit /b 1
)

echo.
echo [2/2] Packaging with PyInstaller...
pyinstaller --onefile --windowed --name "QuotationExtractor" --hidden-import=anthropic --hidden-import=fitz --hidden-import=openpyxl extractor.py

if %errorlevel% neq 0 (
    echo ERROR: PyInstaller failed.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo  Done! Output: dist\QuotationExtractor.exe
echo ============================================================
pause
