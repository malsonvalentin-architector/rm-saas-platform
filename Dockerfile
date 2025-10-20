# Используем Quay.io registry (Red Hat) - стабильная альтернатива Docker Hub
FROM quay.io/jupyter/base-notebook:python-3.10

# Переключаемся на root для установки системных пакетов
USER root

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    libpq-dev \
    gcc \
    g++ \
    make \
    pkg-config \
    libfreetype6-dev \
    libpng-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копируем requirements и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

# Копируем приложение
COPY . /app/

# Создаём необходимые директории
RUN mkdir -p /app/staticfiles /app/media

# Собираем статику
RUN python manage.py collectstatic --noinput || true

# Делаем start_web.sh исполняемым
RUN chmod +x /app/start_web.sh

# Устанавливаем права доступа
RUN chown -R 1000:1000 /app

# Возвращаемся к non-root user
USER 1000

EXPOSE 8000
