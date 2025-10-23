web: gunicorn rm.wsgi --bind 0.0.0.0:$PORT
worker: celery -A rm worker --loglevel=info --concurrency=2
beat: celery -A rm beat --loglevel=info
emulator: python modbus_emulator.py
