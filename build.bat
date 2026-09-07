@echo off
setlocal

echo Installing build dependencies...
python -m pip install -e ".[build]" -q
if errorlevel 1 exit /b 1

echo.
python scripts\build_exe.py

endlocal
