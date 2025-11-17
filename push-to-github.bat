@echo off
echo ========================================
echo   Pushing AI Agent Team to GitHub
echo ========================================
echo.

cd /d "%~dp0"

echo Removing old remote...
git remote remove origin 2>nul

echo Adding GitHub remote...
git remote add origin https://github.com/preet1249/My-AI-Agent-team.git

echo.
echo Pushing to GitHub...
echo (A browser window will open for authentication)
echo.

git push -u origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo   SUCCESS! Code pushed to GitHub!
    echo ========================================
    echo.
    echo View your repo at:
    echo https://github.com/preet1249/My-AI-Agent-team
    echo.
) else (
    echo.
    echo ========================================
    echo   FAILED! Please check the error above
    echo ========================================
    echo.
    echo Try these solutions:
    echo 1. Use GitHub Desktop (easiest)
    echo 2. Generate new token with 'repo' permissions
    echo 3. Check FIX_GITHUB_PUSH.md for detailed help
    echo.
)

pause
