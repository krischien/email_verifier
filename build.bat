@echo off
echo Building Mail Commander Pro Executable...
echo.

echo Installing build dependencies...
pip install -r requirements_build.txt

echo.
echo Building executable...
python build_exe.py

echo.
echo Build process completed!
pause
