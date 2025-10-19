@echo off
chcp 65001 >nul
color 0A
cls
echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║                                                          ║
echo ║              🔍 ПРОВЕРКА СИСТЕМЫ 🔍                      ║
echo ║                                                          ║
echo ╚══════════════════════════════════════════════════════════╝
echo.
echo [1/4] Проверка Python...
echo.

python --version
if errorlevel 1 (
    echo ❌ Python НЕ установлен!
    echo    Установите с https://www.python.org/downloads/
) else (
    echo ✅ Python установлен
)
echo.

echo [2/4] Проверка pip...
pip --version
if errorlevel 1 (
    echo ❌ pip не найден
) else (
    echo ✅ pip работает
)
echo.

echo [3/4] Проверка Django...
python -c "import django; print('Django версия:', django.get_version())" 2>nul
if errorlevel 1 (
    echo ❌ Django НЕ установлен!
    echo    Запустите INSTALL.bat
) else (
    echo ✅ Django установлен
)
echo.

echo [4/4] Проверка базы данных...
if exist db.sqlite3 (
    echo ✅ База данных найдена
) else (
    echo ❌ База данных НЕ найдена!
    echo    Запустите INSTALL.bat
)
echo.

echo ════════════════════════════════════════════════════════════
echo.
echo 📊 Путь к программе:
cd
echo.
echo 📂 Файлы в папке:
dir /B *.bat *.txt *.py 2>nul | more
echo.
echo ════════════════════════════════════════════════════════════
echo.

REM Проверка запущена ли программа
tasklist /FI "IMAGENAME eq python.exe" 2>NUL | find /I /N "python.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo ✅ Программа ЗАПУЩЕНА (процесс python.exe работает)
) else (
    echo ⚠️  Программа НЕ запущена
)

echo.
pause
