# Используем GitHub Container Registry - обходим Docker Hub outage
FROM ghcr.io/alphagov/python:3.10-alpine3.18

# Устанавливаем системные зависимости для Python packages
RUN apk add --no-cache \
    postgresql-client \
    postgresql-dev \
    gcc \
    musl-dev \
    linux-headers \
    g++ \
    make \
    freetype-dev \
    libpng-dev \
    openblas-dev \
    lapack-dev \
    gfortran

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

EXPOSE 8000
