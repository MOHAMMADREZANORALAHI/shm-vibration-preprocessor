@echo off
title SHM Batch Feature Extractor
echo ===================================================
echo    Checking Extended Analytics Dependencies...
echo ===================================================
echo.

python -c "import scipy, pandas, matplotlib, xlsxwriter" 2>nul
if %errorlevel% neq 0 (
    echo [INFO] Excel processing modules are missing. Installing...
    pip install scipy pandas matplotlib xlsxwriter openpyxl
) else (
    echo [OK] All analytical dependencies are successfully verified.
)

echo.
echo Launching SHM Modular Feature Extraction Dashboard...
echo ---------------------------------------------------
python shm_feature_extractor.py

echo.
echo ---------------------------------------------------
echo Analysis Session Ended.
pause