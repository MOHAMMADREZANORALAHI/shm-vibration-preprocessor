@echo off
title Running Detailed Vibration Framework
echo Checking environment...
python -c "import pandas, matplotlib" 2>nul
if %errorlevel% neq 0 (
    echo Installing dependencies...
    pip install pandas matplotlib
)
echo Launching Interactive Analysis GUI...
python plot_vibration.py
exit