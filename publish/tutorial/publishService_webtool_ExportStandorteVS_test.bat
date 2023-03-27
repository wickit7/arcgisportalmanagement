@echo off
chcp 65001

rem Webtool publizieren
"C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe" "..\publish_webtool_portal.py" "publish_webtool_ExportStandorteVS_test.json"

pause


