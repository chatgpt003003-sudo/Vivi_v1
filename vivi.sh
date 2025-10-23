#!/bin/bash
# VIVI Quick Launcher
# Usage: ./vivi.sh [command]
# Commands: full, ui, collect, setup, check

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

if [ ! -d "$SCRIPT_DIR/venv" ]; then
    echo "❌ Virtual environment not found. Please run setup first."
    exit 1
fi

# Default to full operation if no command specified
COMMAND="${1:-full}"

exec "$SCRIPT_DIR/venv/bin/python" "$SCRIPT_DIR/vivi" "$COMMAND"
