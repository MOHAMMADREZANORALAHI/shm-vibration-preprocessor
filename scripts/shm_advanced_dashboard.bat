@echo off
title SHM Advanced Dashboard Runner
echo ===================================================
echo    Checking Advanced Processing Dependencies...
echo ===================================================
echo.

python -c "import scipy, pandas, matplotlib" 2>nul
if %errorlevel% neq 0 (
    echo [INFO] Required processing libraries missing. Installing...
    pip install scipy pandas matplotlib
) else (
    echo [OK] All system dependencies are verified.
)

echo.
echo Launching Custom Signal Filtering Interface...
echo ---------------------------------------------------
python shm_advanced_dashboard.py

echo.
echo ---------------------------------------------------
echo Execution finished.
pause
