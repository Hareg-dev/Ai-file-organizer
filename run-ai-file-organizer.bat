@echo off
REM Create virtual environment if missing
IF NOT EXIST venv (
    python -m venv venv
)
call venv\Scripts\activate

REM Install requirements if needed
pip install --upgrade pip
pip install -r requirements.txt

REM Run the AI File Organizer GUI
python -m organizer.main
pause
