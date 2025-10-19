@echo off
chcp 65001 >nul
color 0A
echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║                                                          ║
echo ║      УСТАНОВКА ПРОГРАММЫ МОНИТОРИНГА АСУТП               ║
echo ║                                                          ║
echo ╚══════════════════════════════════════════════════════════╝
echo.
echo [1/5] Проверка Python...
echo.

REM Проверка наличия Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ОШИБКА: Python не найден!
    echo.
    echo 📥 Пожалуйста, установите Python с сайта:
    echo    https://www.python.org/downloads/
    echo.
    echo ⚠️  ВАЖНО: При установке поставьте галочку "Add Python to PATH"!
    echo.
    pause
    exit /b 1
)

echo ✅ Python установлен
python --version
echo.

echo [2/5] Проверка pip...
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip не найден, попытка установки...
    python -m ensurepip --default-pip
)
echo ✅ pip готов
echo.

echo [3/5] Установка зависимостей...
echo    Это может занять 2-3 минуты, подождите...
echo.

pip install --quiet Django django-crispy-forms crispy-bootstrap4 django-humanize requests django-phonenumber-field phonenumbers celery redis django-celery-beat django-extensions django-view-breadcrumbs django-plotly-dash

if errorlevel 1 (
    echo.
    echo ❌ Ошибка при установке зависимостей!
    echo    Попробуйте запустить установку еще раз
    pause
    exit /b 1
)

echo ✅ Все библиотеки установлены
echo.

echo [4/5] Настройка базы данных...
python manage.py migrate --fake django_celery_beat >nul 2>&1
python manage.py migrate

if errorlevel 1 (
    echo ❌ Ошибка при настройке базы данных
    pause
    exit /b 1
)

echo ✅ База данных готова
echo.

echo [5/5] Создание администратора...
echo.
echo 📝 Введите данные администратора:
echo    (Email будет использоваться для входа в систему)
echo.

python manage.py createsuperuser

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║                                                          ║
echo ║           ✅ УСТАНОВКА ЗАВЕРШЕНА УСПЕШНО! ✅             ║
echo ║                                                          ║
echo ║  Теперь запустите программу двойным кликом на файл:     ║
echo ║                                                          ║
echo ║              ▶️  START.bat  ◀️                           ║
echo ║                                                          ║
echo ╚══════════════════════════════════════════════════════════╝
echo.
pause
