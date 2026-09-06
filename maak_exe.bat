@echo off
setlocal

REM Maak een .exe van tankkompas.py met PyInstaller
REM Gebruik: dubbelklik op dit bestand

python -m pip install pyinstaller
pyinstaller --onefile --noconsole --icon=NONE tankkompas.py

echo.
echo Build klaar.
echo EXE staat in de map dist\
endlocal
pause
