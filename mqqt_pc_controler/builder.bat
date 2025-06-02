@echo off
cd /d %~dp0

:: Удалим старое 
rmdir /s /q build

:: Собираем
pyinstaller --noconfirm --onefile --windowed ^
--icon=icon.ico ^
mqqt.py

pause
