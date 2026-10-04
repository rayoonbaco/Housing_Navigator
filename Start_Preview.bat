@echo off
py -3 -X utf8 "%~dp0preview.py"
if errorlevel 1 pause
