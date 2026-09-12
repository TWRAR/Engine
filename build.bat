@echo off
setlocal

echo Installing build dependencies...
python -m pip install -r requirements.txt -q
if errorlevel 1 exit /b 1
python -m pip install pyinstaller -q
if errorlevel 1 exit /b 1

echo.
python scripts\build_exe.py

endlocal
