web: bash start_web.sh
worker: celery -A rm worker --loglevel=info --concurrency=2
beat: celery -A rm beat --loglevel=info
emulator: bash start_emulator.sh
