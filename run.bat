@echo off
title Automated Resume Parser
color 0A
echo.
echo  ========================================
echo    Automated Resume Parser - Starting...
echo  ========================================
echo.
echo  [*] Server shuru ho raha hai...
echo  [*] Browser mein ye link kholo:
echo.
echo       http://127.0.0.1:5000
echo.
echo  [!] Ye window band mat karna jab tak
echo      app use karna ho.
echo.
echo  ========================================
echo.
cd /d "%~dp0"
python app.py
echo.
echo  [!] Server band ho gaya.
pause
