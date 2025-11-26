#!/bin/bash
# Create and activate virtual environment if missing
if [ ! -d "venv" ]; then
  python3 -m venv venv
fi
source venv/bin/activate

# Install/upgrade requirements
pip install --upgrade pip
pip install -r requirements.txt

# Run the AI File Organizer GUI
python -m organizer.main
