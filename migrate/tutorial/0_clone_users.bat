@echo off
chcp 65001

rem Benutzer klonen
"C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe" "..\0_clone_users.py" "0_clone_users.json"

pause


