@echo off
REM Windows batch script for visualization
REM Usage: run_visualization.bat

echo ==========================================
echo October 2025 Crypto Crash Visualization
echo ==========================================
echo.

REM Check data file
if not exist "FINAL_COMMUNITY_DATASET_145.csv" (
    echo ERROR: FINAL_COMMUNITY_DATASET_145.csv not found!
    echo Please ensure the CSV file is in the same directory.
    pause
    exit /b 1
)

echo [OK] Data file found
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.11 or higher
    pause
    exit /b 1
)

echo [OK] Python detected
echo.

REM Install packages if needed
echo Checking required packages...
python -c "import pandas, numpy, matplotlib, seaborn, wordcloud, networkx" >nul 2>&1
if errorlevel 1 (
    echo Installing missing packages...
    pip install pandas numpy matplotlib seaborn wordcloud networkx scikit-learn textblob vadersentiment koreanize-matplotlib
)

echo [OK] All packages ready
echo.

REM Run visualization
echo Running visualization script...
echo This may take 1-2 minutes...
echo.

python comprehensive_visualization.py

if errorlevel 1 (
    echo.
    echo ERROR: Visualization failed
    pause
    exit /b 1
) else (
    echo.
    echo ==========================================
    echo SUCCESS! Visualization Complete
    echo ==========================================
    echo.
    echo Generated files:
    dir /b *.png
    echo.
    echo You can now view the PNG files
    pause
)
