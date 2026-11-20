@echo off
REM ============================================================
REM  AuraCut - double-click to start. No technical knowledge needed.
REM
REM  This file checks everything AuraCut needs, installs what is
REM  missing, and then starts AuraCut in your browser.
REM  Keep this black window open while you use AuraCut.
REM  To stop AuraCut, just close this window.
REM ============================================================

title AuraCut
cd /d "%~dp0"

echo.
echo   AuraCut is getting ready...
echo.

REM --- 1. Is Python installed? ---
python --version >nul 2>&1
if errorlevel 1 (
  echo   Python is not installed on this computer yet.
  echo   AuraCut needs Python 3.10 or newer.
  echo.
  echo   Please install it first:
  echo     1. Open https://www.python.org/downloads/
  echo     2. Download Python and run the installer.
  echo     3. IMPORTANT: on the first installer screen, tick
  echo        "Add python.exe to PATH" before you click Install.
  echo     4. Then double-click run.bat again.
  echo.
  pause
  exit /b 1
)

REM --- 2. Is it Python 3.10 or newer? ---
python -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>&1
if errorlevel 1 (
  echo   Your Python is too old. AuraCut needs Python 3.10 or newer.
  echo   Please install a newer Python from https://www.python.org/downloads/
  echo   (remember to tick "Add python.exe to PATH"), then run this file again.
  echo.
  pause
  exit /b 1
)

REM --- 3. Install the pieces AuraCut needs (only if they are missing) ---
python -c "import fastapi, uvicorn, sqlalchemy, PIL" >nul 2>&1
if errorlevel 1 (
  echo   Installing the pieces AuraCut needs. This takes a few minutes
  echo   the first time, and only once.
  echo.
  python -m pip install --upgrade pip >nul 2>&1
  python -m pip install -r requirements.txt
  if errorlevel 1 (
    echo.
    echo   That install did not work. Check your internet connection
    echo   and double-click run.bat to try again.
    echo.
    pause
    exit /b 1
  )
  echo.
  echo   Done.
  echo.
)

REM --- 4. Is ffmpeg installed? (AuraCut uses it for video and sound) ---
where ffmpeg >nul 2>&1
if errorlevel 1 (
  echo   ffmpeg is missing. AuraCut uses it for video and sound.
  where winget >nul 2>&1
  if not errorlevel 1 (
    echo   Trying to install it for you now...
    echo.
    winget install Gyan.FFmpeg --accept-source-agreements --accept-package-agreements
    echo.
    REM A fresh winget install is not on PATH in this window yet, so look for it.
    for /d %%D in ("%LOCALAPPDATA%\Microsoft\WinGet\Packages\Gyan.FFmpeg*") do (
      if exist "%%D\bin\ffmpeg.exe" set "PATH=%%D\bin;%PATH%"
    )
  ) else (
    echo   Please install ffmpeg from https://www.gyan.dev/ffmpeg/builds/
    echo   (download the "release essentials" zip, and put ffmpeg.exe
    echo    somewhere Windows can find it). AuraCut will still open
    echo    without it, but video features will not work.
    echo.
  )
  where ffmpeg >nul 2>&1
  if errorlevel 1 (
    echo   ffmpeg is still not found, but AuraCut will start anyway.
    echo   You can install ffmpeg later - AuraCut will tell you in
    echo   the dashboard if it is missing.
    echo.
  )
)

REM --- 5. Start AuraCut and open it in the browser ---
echo   Starting AuraCut...
echo.
start "" /b cmd /c "timeout /t 5 /nobreak >nul & start http://127.0.0.1:8765"
echo   AuraCut will open in your browser in a few seconds.
echo   (If it does not, open http://127.0.0.1:8765 yourself.)
echo.
echo   Keep this black window open while you use AuraCut.
echo   To stop AuraCut, close this window.
echo.
python -m studio.server
