@echo off
chcp 65001 >nul
echo ============================================================
echo  估價單 AI 擷取工具 - 打包腳本
echo ============================================================
echo.

:: 安裝依賴
echo [1/2] 安裝依賴套件...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo 安裝失敗，請確認 Python 環境
    pause
    exit /b 1
)

:: 打包
echo.
echo [2/2] 打包成 .exe ...
pyinstaller ^
    --onefile ^
    --windowed ^
    --name "估價單擷取工具" ^
    --icon NONE ^
    --hidden-import=anthropic ^
    --hidden-import=fitz ^
    --hidden-import=openpyxl ^
    extractor.py

if %errorlevel% neq 0 (
    echo 打包失敗
    pause
    exit /b 1
)

echo.
echo ============================================================
echo  打包完成！執行檔位於 dist\估價單擷取工具.exe
echo ============================================================
pause
