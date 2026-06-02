@echo off
title SHM Multi-Channel FDD Processing Tool
echo ===================================================
echo    Checking Operational Modal Analysis Modules...
echo ===================================================
echo.

python -c "import scipy, pandas, matplotlib, openpyxl" 2>nul
if %errorlevel% neq 0 (
    echo [INFO] Required mathematical modules are missing. Auto-installing...
    python -m pip install scipy pandas matplotlib openpyxl
) else (
    echo [OK] Matrix operations and SVD libraries are successfully verified.
)

echo.
echo Launching Batch FDD Multi-Channel Modal Identification Framework...
echo ---------------------------------------------------
python shm_fdd_batch_analyzer.py

echo.
echo ---------------------------------------------------
echo Analysis Session Ended.
pause