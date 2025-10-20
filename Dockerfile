FROM python:3.10-slim-bullseye

# Установка системных зависимостей
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    libpq-dev \
    gcc \
    g++ \
    make \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копируем requirements и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем приложение
COPY . /app/

# Создаём необходимые директории
RUN mkdir -p /app/staticfiles /app/media

# Собираем статику (игнорируем ошибки для первого build)
RUN python manage.py collectstatic --noinput || true

# Делаем start_web.sh исполняемым
RUN chmod +x /app/start_web.sh

# Expose port (Railway автоматически назначает)
EXPOSE 8000

# Railway будет использовать Procfile для команд запуска
