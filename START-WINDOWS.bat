@echo off
setlocal
cd /d "%~dp0"
echo Pramaan frontend setup
where node >nul 2>nul
if errorlevel 1 (
  echo Node.js is not installed. Install Node.js 20.19 or newer from https://nodejs.org/ and rerun this file.
  pause
  exit /b 1
)
where npm >nul 2>nul
if errorlevel 1 (
  echo npm was not found. Reinstall Node.js from https://nodejs.org/ and make sure npm is included.
  pause
  exit /b 1
)
node -e "const v=process.versions.node.split('.').map(Number); if(v[0]<20 || (v[0]===20 && v[1]<19)) process.exit(1)" >nul 2>nul
if errorlevel 1 (
  echo This project needs Node.js 20.19 or newer. Update Node.js, then run this file again.
  pause
  exit /b 1
)
if not exist "node_modules\.bin\vite.cmd" (
  echo Installing all project dependencies. This can take a few minutes...
  if exist package-lock.json (
    call npm ci
  ) else (
    call npm install
  )
  if errorlevel 1 (
    echo Dependency installation failed. Check your internet connection and package-lock.json, then try again.
    pause
    exit /b 1
  )
)
if not exist "node_modules\.bin\vite.cmd" (
  echo Vite is still missing after dependency installation. Please send us this terminal output.
  pause
  exit /b 1
)
echo Starting Pramaan. Keep this window open while using the app.
echo If port 5173 is busy, Vite will automatically choose another available port.
call npm run dev -- --host 127.0.0.1
pause
