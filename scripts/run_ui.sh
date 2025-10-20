#!/bin/bash
# Launch the Celebrity Index Collector UI

echo "======================================"
echo "Celebrity Index Collector UI"
echo "======================================"
echo ""
echo "Starting Streamlit dashboard..."
echo ""

cd "$(dirname "$0")/.."
venv/bin/streamlit run src/ui/app.py
