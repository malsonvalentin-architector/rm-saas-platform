web: gunicorn rm.wsgi --bind 0.0.0.0:$PORT
worker: bash start_worker_with_emulator.sh
beat: celery -A rm beat --loglevel=info
emulator: python modbus_emulator.py
