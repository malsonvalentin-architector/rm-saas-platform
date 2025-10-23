"""
Django AppConfig для data приложения
С автоматическим запуском Enhanced Emulator v2.0
"""

from django.apps import AppConfig
import os
import subprocess
import threading


class DataConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'data'
    emulator_process = None
    
    def ready(self):
        """
        Вызывается при инициализации Django приложения
        Запускает Enhanced Emulator если это Worker процесс
        """
        # Проверяем что это Worker, а не Web/Beat
        # Worker определяется через CELERY_WORKER_RUNNING env или отсутствие gunicorn
        is_worker = self._is_worker_process()
        
        if is_worker and not DataConfig.emulator_process:
            self._start_emulator()
    
    def _is_worker_process(self):
        """Определяет, является ли текущий процесс Worker"""
        import sys
        
        # Проверяем аргументы командной строки
        cmdline = ' '.join(sys.argv)
        
        # Worker определяется по наличию 'celery' и 'worker' в командной строке
        if 'celery' in cmdline and 'worker' in cmdline:
            return True
        
        # Проверяем переменную окружения
        if os.environ.get('CELERY_WORKER', ''):
            return True
        
        return False
    
    def _start_emulator(self):
        """Запускает Enhanced Emulator v2.0 в background thread"""
        import sys
        
        def run_emulator():
            try:
                print("="*70, file=sys.stderr)
                print(" [DataConfig] Starting Enhanced Emulator v2.0", file=sys.stderr)
                print("="*70, file=sys.stderr)
                
                # Путь к emulator script (относительно project root)
                emulator_path = os.path.join(
                    os.path.dirname(os.path.dirname(__file__)),
                    'modbus_emulator.py'
                )
                
                if not os.path.exists(emulator_path):
                    print(f" [DataConfig] ERROR: Emulator not found at {emulator_path}", file=sys.stderr)
                    return
                
                # Запускаем emulator как subprocess
                DataConfig.emulator_process = subprocess.Popen(
                    [sys.executable, emulator_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                    bufsize=1
                )
                
                print(f" [DataConfig] ✅ Enhanced Emulator started (PID: {DataConfig.emulator_process.pid})", file=sys.stderr)
                print(" [DataConfig]    Listening on localhost:5020", file=sys.stderr)
                print("="*70, file=sys.stderr)
                
                # Читаем output emulator (для логирования)
                if DataConfig.emulator_process.stdout:
                    for line in DataConfig.emulator_process.stdout:
                        print(f" [Emulator] {line.rstrip()}", file=sys.stderr)
                
            except Exception as e:
                print(f" [DataConfig] ERROR starting emulator: {e}", file=sys.stderr)
        
        # Запускаем в отдельном thread, чтобы не блокировать Django startup
        emulator_thread = threading.Thread(target=run_emulator, daemon=True)
        emulator_thread.start()
        
        print(" [DataConfig] Enhanced Emulator v2.0 initialization started in background", file=sys.stderr)
