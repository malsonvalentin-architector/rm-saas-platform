#!/usr/bin/env python3
"""
MODBUS ЭМУЛЯТОР для ProMonitor.kz
Эмулирует CAREL pCO контроллер с данными из production системы
"""
import json
import random
import time
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
from pymodbus.server.sync import StartTcpServer
from pymodbus.device import ModbusDeviceIdentification

class CarelPcoEmulator:
    """
    Эмулятор CAREL pCO контроллера
    Использует реальные данные из production snapshot
    """
    
    def __init__(self, snapshot_file):
        print(f"📦 Загружаю snapshot: {snapshot_file}")
        with open(snapshot_file, 'r') as f:
            self.snapshot = json.load(f)
        
        device = self.snapshot['discovered_devices'][2]  # CAREL контроллер
        self.device_info = device
        
        # Базовые значения из production
        self.base_holding = device['modbus']['holding_registers']['sample_values']
        
        print(f"✅ Загружен: {device['manufacturer']} {device['model']}")
        print(f"   IP: {device['ip']} (эмулируем локально)")
        print(f"   Holding Registers: {self.base_holding}")
    
    def create_datastore(self):
        """
        Создаём Modbus datastore с реальными значениями
        """
        # Holding Registers (40001+) - основные данные
        # Добавляем вариацию к базовым значениям для симуляции изменений
        holding_registers = self.base_holding + [0] * 90  # Расширяем до 100 регистров
        
        # Input Registers (30001+) - входные данные (генерируем случайные)
        input_registers = [random.randint(0, 1000) for _ in range(100)]
        
        # Coils (00001+) - дискретные выходы
        coils = [False] * 100
        
        # Discrete Inputs (10001+) - дискретные входы
        discrete_inputs = [False] * 100
        
        # Создаём datastore
        store = ModbusSlaveContext(
            di=ModbusSequentialDataBlock(0, discrete_inputs),
            co=ModbusSequentialDataBlock(0, coils),
            hr=ModbusSequentialDataBlock(0, holding_registers),
            ir=ModbusSequentialDataBlock(0, input_registers)
        )
        
        context = ModbusServerContext(slaves=store, single=True)
        
        print(f"✅ Datastore создан:")
        print(f"   • Holding Registers: 100 регистров")
        print(f"   • Input Registers: 100 регистров")
        print(f"   • Coils: 100 регистров")
        print(f"   • Discrete Inputs: 100 регистров")
        
        return context
    
    def create_device_identity(self):
        """
        Создаём идентификационную информацию устройства
        """
        identity = ModbusDeviceIdentification()
        identity.VendorName = self.device_info['manufacturer']
        identity.ProductCode = self.device_info['model']
        identity.VendorUrl = 'http://www.carel.com'
        identity.ProductName = 'CAREL pCO Emulator'
        identity.ModelName = self.device_info['model']
        identity.MajorMinorRevision = self.device_info['firmware_version']
        
        print(f"✅ Device Identity создан:")
        print(f"   • Vendor: {identity.VendorName}")
        print(f"   • Model: {identity.ModelName}")
        print(f"   • Firmware: {identity.MajorMinorRevision}")
        
        return identity

def start_emulator(host='0.0.0.0', port=5020, snapshot_file='/home/user/production_snapshot.json'):
    """
    Запускает Modbus TCP эмулятор
    """
    print("="*60)
    print("🏭 MODBUS EMULATOR - CAREL pCO Controller")
    print("="*60)
    
    emulator = CarelPcoEmulator(snapshot_file)
    context = emulator.create_datastore()
    identity = emulator.create_device_identity()
    
    print("\n" + "="*60)
    print(f"🚀 Запускаю Modbus TCP сервер на {host}:{port}")
    print("="*60)
    print(f"📡 Подключение: modbus://{host}:{port}")
    print(f"🔧 Slave ID: 1")
    print(f"📊 Эмулирует: CAREL pCO (192.168.11.101)")
    print("\n💡 Для остановки: Ctrl+C")
    print("="*60 + "\n")
    
    # Запускаем сервер
    StartTcpServer(
        context, 
        identity=identity,
        address=(host, port),
        allow_reuse_address=True
    )

if __name__ == "__main__":
    start_emulator()
