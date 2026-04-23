@echo off
cd /d %~dp0
call venv\Scripts\activate

start /b ollama serve

timeout /t 10 /nobreak >nul

start python ui\app.py
