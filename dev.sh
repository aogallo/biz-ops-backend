#!/bin/bash

# Get the directory of the script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Activate virtual environment
if [ -d "$DIR/.venv" ]; then
    source "$DIR/.venv/bin/activate"
else
    echo "Creating virtual environment..."
    python3 -m venv "$DIR/.venv"
    source "$DIR/.venv/bin/activate"
    pip install -r requirements.txt
fi

# Set environment variables for LazyVim
export NVIM_APPNAME="lazyvim"
export NVIM_PYTHON="$DIR/.venv/bin/python"

# Launch LazyVim
nvim "$@" 