#!/bin/bash

# add-to-anki.sh - A wrapper script for the Cambridge Dictionary to Anki integration

# Configuration
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PYTHON_SCRIPT="$SCRIPT_DIR/cambridge_to_anki_direct.py"
LOG_FILE="$HOME/Downloads/tmp/anki_imports.log"

# Ensure log directory exists
mkdir -p "$HOME/Downloads/tmp"

# Help function
show_help() {
    echo "Usage: add-to-anki [OPTIONS] WORD"
    echo ""
    echo "Options:"
    echo "  -h, --help       Show this help message and exit"
    echo "  -u, --url URL    Direct Cambridge Dictionary URL"
    echo ""
    echo "Examples:"
    echo "  add-to-anki levity                     # Looks up 'levity' automatically"
    echo "  add-to-anki -u https://dictionary.cambridge.org/dictionary/english/levity"
    echo ""
}

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Check if Python script exists
if [ ! -f "$PYTHON_SCRIPT" ]; then
    log "Error: Python script not found at $PYTHON_SCRIPT"
    exit 1
fi

# Parse arguments
URL=""
WORD=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -u|--url)
            URL="$2"
            shift 2
            ;;
        *)
            WORD="$1"
            shift
            ;;
    esac
done

# If no URL provided but word is, construct the URL
if [ -z "$URL" ] && [ -n "$WORD" ]; then
    # Convert spaces to hyphens and make lowercase
    FORMATTED_WORD=$(echo "$WORD" | tr ' ' '-' | tr '[:upper:]' '[:lower:]')
    URL="https://dictionary.cambridge.org/dictionary/english/$FORMATTED_WORD"
fi

# Validate input
if [ -z "$URL" ]; then
    log "Error: No word or URL provided"
    show_help
    exit 1
fi

# Run the Python script
log "Looking up: $URL"
python3 "$PYTHON_SCRIPT" "$URL"

exit_code=$?

if [ $exit_code -eq 0 ]; then
    log "Successfully processed $URL"
else
    log "Failed to process $URL (exit code: $exit_code)"
fi

exit $exit_code
