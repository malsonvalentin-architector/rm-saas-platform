@echo off
chcp 65001 >nul
color 0C
echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║                                                          ║
echo ║              🛑 ОСТАНОВКА ПРОГРАММЫ 🛑                   ║
echo ║                                                          ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

echo ⏳ Завершение процессов Django...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq Django*" >nul 2>&1
taskkill /F /IM python.exe >nul 2>&1

echo ✅ Все процессы остановлены
echo.
timeout /t 2 /nobreak >nul
