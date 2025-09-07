@echo off
echo Installing oppm system-wide...
pip install -e .
if %ERRORLEVEL% neq 0 (
    echo Something went wrong. Make sure Python and pip are installed and on PATH.
    pause
    exit /b %ERRORLEVEL%
)
echo.
echo Done! You can now use oppm from anywhere with:
echo     oppm install <package>
pause
