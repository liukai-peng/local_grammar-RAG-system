@echo off
chcp 65001 >nul
cd /d "%~dp0"

:: Force offline mode
set TRANSFORMERS_OFFLINE=1
set HF_HUB_OFFLINE=1

:: Use your Conda Python that has PyQt5 installed
"C:\Users\12848\anaconda3\python.exe" rag_desktop_app.py

:: If fails, pause to show error
if %errorlevel% neq 0 pause