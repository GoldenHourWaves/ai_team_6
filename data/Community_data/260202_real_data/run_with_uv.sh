#!/bin/bash
# UV environment visualization script
# Usage: bash run_with_uv.sh

echo "=========================================="
echo "UV Environment - Crypto Crash Visualization"
echo "=========================================="
echo ""

# Check UV
if ! command -v uv &> /dev/null; then
    echo "❌ Error: UV not found!"
    echo "   Install UV: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo "✅ UV detected: $(uv --version)"
echo ""

# Check data file
if [ ! -f "FINAL_COMMUNITY_DATASET_145.csv" ]; then
    echo "❌ Error: FINAL_COMMUNITY_DATASET_145.csv not found!"
    exit 1
fi

echo "✅ Data file found"
echo ""

# Sync environment
echo "🔄 Syncing UV environment..."
cd .. 2>/dev/null || true
uv sync
cd - > /dev/null 2>&1 || true

echo "✅ Environment ready"
echo ""

# Run with UV
echo "🎨 Running visualization with UV..."
echo "   This may take 1-2 minutes..."
echo ""

uv run python comprehensive_visualization.py

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✅ Success! Visualization Complete"
    echo "=========================================="
    echo ""
    echo "📁 Generated files:"
    ls -1 *.png 2>/dev/null | while read file; do
        size=$(du -h "$file" 2>/dev/null | cut -f1)
        echo "   • $file ($size)"
    done
    echo ""
    total=$(ls -1 *.png 2>/dev/null | wc -l)
    echo "📊 Total: $total visualizations"
    echo ""
    echo "💡 Tip: Open files with:"
    echo "   macOS: open *.png"
    echo "   Linux: xdg-open *.png"
    echo "   Windows: start *.png"
else
    echo ""
    echo "❌ Visualization failed"
    echo "   Check error messages above"
    exit 1
fi
