@echo off
chcp 65001

rem Benutzer klonen
"C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe" "..\1_clone_groups.py" "1_clone_groups.json"

pause


