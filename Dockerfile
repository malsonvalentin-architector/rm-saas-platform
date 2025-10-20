# Используем точный SHA256 который Railway уже имеет в кэше
FROM docker.io/library/python@sha256:f1fb49e4d5501ac93d0ca519fb7ee6250842245aba8612926a46a0832a1ed089

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

# Делаем скрипты исполняемыми
RUN chmod +x /app/start_web.sh || true

EXPOSE 8000

# Default command for web service
# Railway will override this with Procfile when deploying specific services
CMD ["bash", "start_web.sh"]
