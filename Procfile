web: bash start_web.sh
worker: celery -A rm worker --loglevel=info --concurrency=4
beat: celery -A rm beat --loglevel=info
