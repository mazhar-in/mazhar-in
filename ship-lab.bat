@echo off
rem ==============================================================================
rem ship-lab.bat — One-Command Shipper for mazhar.in/labs (Windows)
rem Usage: ship-lab.bat "projectile-motion: add velocity vector telemetry"
rem ==============================================================================

set MSG=%~1
if "%MSG%"=="" set MSG=quick update

echo ⚡ Step 1: Running Labs Auto-Discovery ^& SEO Indexer...
python scripts\update_labs.py
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] update_labs.py failed!
    exit /b %ERRORLEVEL%
)

echo 📦 Step 2: Staging repository changes...
git add .

echo 📝 Step 3: Committing: ship lab: %MSG%...
git commit -m "ship lab: %MSG%"

echo 🚀 Step 4: Pushing to origin...
git push origin main

echo ✅ Lab successfully shipped to production!
