#!/bin/bash
# Quick run script for visualization
# Usage: bash run_visualization.sh

echo "=========================================="
echo "October 2025 Crypto Crash Visualization"
echo "=========================================="
echo ""

# Check if data file exists
if [ ! -f "FINAL_COMMUNITY_DATASET_145.csv" ]; then
    echo "❌ Error: FINAL_COMMUNITY_DATASET_145.csv not found!"
    echo "   Please ensure the CSV file is in the same directory."
    exit 1
fi

echo "✅ Data file found"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 not found!"
    exit 1
fi

echo "✅ Python 3 detected"
echo ""

# Check required packages
echo "Checking packages..."
python3 -c "import pandas, numpy, matplotlib, seaborn, wordcloud, networkx" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Some packages missing. Installing..."
    pip install pandas numpy matplotlib seaborn wordcloud networkx scikit-learn textblob vadersentiment koreanize-matplotlib
fi

echo "✅ All packages ready"
echo ""

# Run visualization
echo "🎨 Running visualization script..."
echo "   This may take 1-2 minutes..."
echo ""

python3 comprehensive_visualization.py

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✅ Visualization Complete!"
    echo "=========================================="
    echo ""
    echo "Generated files:"
    ls -1 *.png 2>/dev/null | nl
    echo ""
    echo "Total: $(ls -1 *.png 2>/dev/null | wc -l) PNG files"
else
    echo ""
    echo "❌ Error occurred during visualization"
    exit 1
fi
