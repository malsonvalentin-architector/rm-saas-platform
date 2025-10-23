web: gunicorn rm.wsgi --bind 0.0.0.0:$PORT
worker: python start_worker_with_emulator.py
beat: celery -A rm beat --loglevel=info
emulator: python modbus_emulator.py
