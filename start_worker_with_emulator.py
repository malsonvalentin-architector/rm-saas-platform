#!/usr/bin/env python3
"""
Запуск Enhanced Emulator v2.0 + Celery Worker
Используется как wrapper для Railway Worker service
"""

import subprocess
import time
import sys
import os
import signal

def start_emulator():
    """Запускает Enhanced Emulator в фоновом процессе"""
    print("="*60)
    print(" Starting Enhanced Emulator v2.0")
    print("="*60)
    
    try:
        # Запускаем emulator как subprocess
        emulator_process = subprocess.Popen(
            ['python', 'modbus_emulator.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        
        # Ждём 3 секунды для инициализации
        time.sleep(3)
        
        # Проверяем что процесс живой
        if emulator_process.poll() is None:
            print("✅ Enhanced Emulator v2.0 started successfully")
            print("   PID:", emulator_process.pid)
            print("   Listening on: localhost:5020")
            print()
            return emulator_process
        else:
            print("❌ Enhanced Emulator failed to start")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error starting Enhanced Emulator: {e}")
        sys.exit(1)

def start_worker():
    """Запускает Celery Worker"""
    print("="*60)
    print(" Starting Celery Worker")
    print("="*60)
    
    try:
        # Запускаем worker через os.execvp (заменяет текущий процесс)
        os.execvp('celery', [
            'celery',
            '-A', 'rm',
            'worker',
            '--loglevel=info',
            '--concurrency=2'
        ])
    except Exception as e:
        print(f"❌ Error starting Celery Worker: {e}")
        sys.exit(1)

def main():
    """Главная функция"""
    print("\n" + "="*60)
    print(" Enhanced Emulator v2.0 + Worker Startup")
    print("="*60)
    print()
    
    # Запускаем emulator
    emulator_process = start_emulator()
    
    # Устанавливаем обработчик сигналов для graceful shutdown
    def signal_handler(signum, frame):
        print("\n⚠️  Shutting down...")
        if emulator_process and emulator_process.poll() is None:
            emulator_process.terminate()
            emulator_process.wait(timeout=5)
        sys.exit(0)
    
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    # Запускаем worker (этот процесс заменит текущий)
    start_worker()

if __name__ == "__main__":
    main()
