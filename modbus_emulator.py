#!/usr/bin/env python3
"""
MODBUS ЭМУЛЯТОР Enhanced для ProMonitor.kz
Версия для Railway deployment с улучшенными данными
"""
import json
import random
import os
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
from pymodbus.server.sync import StartTcpServer
from pymodbus.device import ModbusDeviceIdentification

class EnhancedCarelPcoEmulator:
    """Улучшенный эмулятор с 200+ регистрами и динамическими данными"""
    
    def __init__(self):
        # Базовые данные из production (реальные значения)
        self.base_holding = [28836, 16830, 22544, 16833, 25428, 16907, 16515, 16906, 61342, 16806]
        
        # Виртуальные датчики
        self.temp_zones = 4  # Температурные зоны
        self.humidity_sensors = 3  # Датчики влажности
        self.pressure_sensors = 2  # Датчики давления
        self.power_meters = 3  # Счётчики мощности
        
        print("✅ Enhanced Emulator initialized")
        print(f"   • Temperature zones: {self.temp_zones}")
        print(f"   • Humidity sensors: {self.humidity_sensors}")
        print(f"   • Pressure sensors: {self.pressure_sensors}")
        print(f"   • Power meters: {self.power_meters}")
    
    def create_datastore(self):
        """Создание расширенного datastore"""
        
        # === HOLDING REGISTERS (200 регистров) ===
        holding_registers = []
        
        # 0-9: Реальные данные из production
        holding_registers.extend(self.base_holding)
        
        # 10-29: Температуры (4 зоны x 5 параметров)
        # Реалистичные значения: 18-25°C (x10 для точности)
        for i in range(self.temp_zones):
            holding_registers.append(random.randint(180, 250))  # Текущая температура
            holding_registers.append(220)  # Уставка (22.0°C)
            holding_registers.append(random.randint(0, 100))  # Выход %
            holding_registers.append(random.randint(-30, 30))  # Оффсет
            holding_registers.append(random.randint(0, 3))  # Статус
        
        # 30-44: Влажность (3 датчика x 5 параметров)
        # Реалистичные значения: 40-70% RH
        for i in range(self.humidity_sensors):
            holding_registers.append(random.randint(400, 700))  # Текущая влажность
            holding_registers.append(550)  # Уставка (55%)
            holding_registers.append(random.randint(0, 100))  # Выход %
            holding_registers.append(random.randint(-100, 100))  # Оффсет
            holding_registers.append(random.randint(0, 3))  # Статус
        
        # 45-54: Давление (2 датчика x 5 параметров)
        # HP: 12-18 bar, LP: 3-7 bar
        for i in range(self.pressure_sensors):
            if i == 0:  # HP
                holding_registers.append(random.randint(120, 180))
                holding_registers.append(150)
            else:  # LP
                holding_registers.append(random.randint(30, 70))
                holding_registers.append(50)
            holding_registers.append(random.randint(0, 100))
            holding_registers.append(random.randint(-20, 20))
            holding_registers.append(random.randint(0, 3))
        
        # 55-69: Мощность (3 счётчика x 5 параметров)
        # Компрессоры: 300-400W, Вентиляторы: 100-150W
        for i in range(self.power_meters):
            if i < 2:  # Компрессоры
                holding_registers.append(random.randint(3000, 4000))
            else:  # Вентиляторы
                holding_registers.append(random.randint(1000, 1500))
            holding_registers.append(random.randint(0, 65535))  # kWh low
            holding_registers.append(random.randint(0, 100))  # kWh high
            holding_registers.append(random.randint(0, 500))  # Ток (x10)
            holding_registers.append(random.randint(0, 3))  # Статус
        
        # 70-199: Заполняем остальные регистры
        while len(holding_registers) < 200:
            holding_registers.append(random.randint(0, 1000))
        
        # === INPUT REGISTERS (200 регистров) ===
        input_registers = [random.randint(0, 1000) for _ in range(200)]
        
        # === COILS (200 регистров) ===
        coils = [False] * 200
        for i in range(0, 20, 3):
            coils[i] = random.choice([True, False])
        
        # === DISCRETE INPUTS (200 регистров) ===
        discrete_inputs = [False] * 200
        for i in range(0, 20, 4):
            discrete_inputs[i] = random.choice([True, False])
        
        # Создание datastore
        store = ModbusSlaveContext(
            di=ModbusSequentialDataBlock(0, discrete_inputs),
            co=ModbusSequentialDataBlock(0, coils),
            hr=ModbusSequentialDataBlock(0, holding_registers),
            ir=ModbusSequentialDataBlock(0, input_registers)
        )
        
        context = ModbusServerContext(slaves=store, single=True)
        
        print("✅ Enhanced Datastore created:")
        print(f"   • Holding: {len(holding_registers)} registers")
        print(f"   • Input: {len(input_registers)} registers")
        print(f"   • Coils: {len(coils)} registers")
        print(f"   • Discrete: {len(discrete_inputs)} registers")
        
        return context
    
    def create_identity(self):
        """Создание device identity"""
        identity = ModbusDeviceIdentification()
        identity.VendorName = "CAREL"
        identity.ProductCode = "C.pCO"
        identity.VendorUrl = "http://www.carel.com"
        identity.ProductName = "CAREL pCO Enhanced Emulator"
        identity.ModelName = "C.pCO"
        identity.MajorMinorRevision = "Webkit 6.0a"
        
        print("✅ Device Identity created")
        return identity

def start_emulator():
    """Запуск эмулятора"""
    port = int(os.environ.get('PORT', 5020))
    host = '0.0.0.0'
    
    print("="*70)
    print("🏭 MODBUS ENHANCED EMULATOR - ProMonitor.kz")
    print("="*70)
    
    emulator = EnhancedCarelPcoEmulator()
    context = emulator.create_datastore()
    identity = emulator.create_identity()
    
    print(f"\n🚀 Starting Modbus TCP server on {host}:{port}")
    print(f"📡 Connection: modbus://{host}:{port}")
    print(f"🎯 200+ registers per type")
    print(f"🔄 Dynamic realistic data")
    print("="*70 + "\n")
    
    StartTcpServer(
        context,
        identity=identity,
        address=(host, port),
        allow_reuse_address=True
    )

if __name__ == "__main__":
    start_emulator()
