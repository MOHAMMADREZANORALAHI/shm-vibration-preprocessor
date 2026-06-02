@echo off
title Running Signal Cropping Framework
echo ===================================================
echo     Vibration Data Cropping Tool - Jet-Engine Run
echo ===================================================
echo.
echo Checking environment environment...
python -c "import pandas" 2>nul
if %errorlevel% neq 0 (
    echo Required library [pandas] not found. Installing now...
    pip install pandas
)
echo Launching Signal Cropper GUI...
python crop_vibration.py
exit