#!/bin/bash
# start.sh - User start script for MM Wallpaper

# Check if virtual environment exists, if not create it
test -d ".venv" || python3 -m venv .venv

# Activate the virtual environment
source .venv/bin/activate

# Upgrade pip and install requirements
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet

# Start the API
python -m main "$@"