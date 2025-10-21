@echo off
echo Attendance System Production Setup
echo ==================================

cd /d "C:\AttendanceSystem"

echo Step 1: Creating Python virtual environment...
python -m venv venv
if errorlevel 1 goto error

echo Step 2: Activating environment and installing dependencies...
call venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 goto error

echo Step 3: Verifying installation...
python verify_dependencies.py
if errorlevel 1 goto error

echo.
echo SUCCESS: All dependencies installed!
echo.
echo Next steps:
echo 1. Configure your .env file with database credentials
echo 2. Test the system: python main_continuous.py
echo 3. Install as Windows service
echo.
pause
exit /b 0

:error
echo.
echo ERROR: Setup failed at step %errorlevel%
echo Please check the errors above.
pause
exit /b 1