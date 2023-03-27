@echo off
chcp 65001

rem Publish services
"C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe" "..\publish_service_portal.py" "publish_playground_test.json" "publish_citymaps_cache_test.json"

pause


