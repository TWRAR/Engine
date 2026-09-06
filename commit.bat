@echo off
setlocal enabledelayedexpansion

if "%~1"=="" (
    echo Usage: commit.bat "commit message"
    exit /b 1
)

set /p VERSION=<VERSION.md
set TAG=v%VERSION%

git add -A
git commit -m "%~1"

git rev-parse "%TAG%" >nul 2>&1
if %errorlevel%==0 (
    echo Tag %TAG% already exists, skipping tag creation.
) else (
    git tag -a "%TAG%" -m "Release %TAG%"
    echo Created tag %TAG%
)

endlocal
