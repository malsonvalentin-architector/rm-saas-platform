#!/usr/bin/env python3
"""
MODBUS ЭМУЛЯТОР Enhanced v2.0 для ProMonitor.kz
Версия с 800+ регистрами и расширенными адресами 1000-4000
"""
import random
import time
import threading
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
from pymodbus.server import StartTcpServer
from pymodbus.device import ModbusDeviceIdentification

class EnhancedModbusEmulatorV2:
    """Enhanced Emulator v2.0 с 800+ регистрами и динамическими обновлениями"""
    
    def __init__(self):
        print("🚀 Enhanced Modbus Emulator v2.0")
        print("=" * 60)
        print("Features:")
        print("  • 800+ registers (200+ each type)")
        print("  • 4 temperature zones (addresses 1000-1003)")
        print("  • 3 humidity sensors (addresses 2000-2002)")
        print("  • 2 pressure sensors (addresses 3000-3001)")
        print("  • 3 power meters (addresses 4000-4002)")
        print("  • Dynamic updates every 5 seconds")
        print("=" * 60)
        
        self.context = None
        self.update_thread = None
        self.running = False
    
    def float_to_registers(self, value):
        """Преобразование Float32 в два Modbus регистра"""
        import struct
        packed = struct.pack('>f', value)
        high, low = struct.unpack('>HH', packed)
        return [high, low]
    
    def generate_temperature(self, zone_id):
        """Генерация реалистичной температуры 18-25°C"""
        base_temp = 21.5
        variation = 2.0
        return base_temp + (random.random() * variation * 2 - variation)
    
    def generate_humidity(self, sensor_id):
        """Генерация реалистичной влажности 40-70% RH"""
        base_hum = 55.0
        variation = 10.0
        return base_hum + (random.random() * variation * 2 - variation)
    
    def generate_pressure(self, sensor_type):
        """Генерация реалистичного давления"""
        if sensor_type == 'HP':  # High Pressure 8-12 bar
            base = 10.0
            variation = 2.0
        else:  # Low Pressure 1-3 bar
            base = 2.0
            variation = 1.0
        return base + (random.random() * variation * 2 - variation)
    
    def generate_power(self, meter_type):
        """Генерация реалистичной мощности"""
        if meter_type == 'compressor':  # 5-15 kW
            base = 10.0
            variation = 5.0
        else:  # fans 2-8 kW
            base = 5.0
            variation = 3.0
        return base + (random.random() * variation * 2 - variation)
    
    def create_datastore(self):
        """Создание datastore с 800+ регистрами"""
        
        # === HOLDING REGISTERS (200 регистров) ===
        holding = [0] * 10000  # Большой буфер для всех адресов
        
        # Базовые регистры 0-99
        for i in range(100):
            holding[i] = random.randint(0, 65535)
        
        # 1000-1007: Температурные зоны (4 зоны x 2 регистра Float32)
        for zone in range(4):
            addr = 1000 + zone * 2
            temp = self.generate_temperature(zone)
            regs = self.float_to_registers(temp)
            holding[addr] = regs[0]
            holding[addr + 1] = regs[1]
        
        # 2000-2005: Датчики влажности (3 датчика x 2 регистра Float32)
        for sensor in range(3):
            addr = 2000 + sensor * 2
            hum = self.generate_humidity(sensor)
            regs = self.float_to_registers(hum)
            holding[addr] = regs[0]
            holding[addr + 1] = regs[1]
        
        # 3000-3003: Датчики давления (2 датчика x 2 регистра Float32)
        for sensor in range(2):
            addr = 3000 + sensor * 2
            press = self.generate_pressure('HP' if sensor == 0 else 'LP')
            regs = self.float_to_registers(press)
            holding[addr] = regs[0]
            holding[addr + 1] = regs[1]
        
        # 4000-4005: Счётчики мощности (3 счётчика x 2 регистра Float32)
        for meter in range(3):
            addr = 4000 + meter * 2
            power = self.generate_power('compressor' if meter < 2 else 'fans')
            regs = self.float_to_registers(power)
            holding[addr] = regs[0]
            holding[addr + 1] = regs[1]
        
        # === INPUT REGISTERS (200 регистров) ===
        input_regs = [0] * 200
        for i in range(200):
            input_regs[i] = random.randint(0, 65535)
        
        # === COILS (200 регистров) ===
        coils = [False] * 200
        for i in range(0, 200, 3):
            coils[i] = random.choice([True, False])
        
        # === DISCRETE INPUTS (200 регистров) ===
        discrete = [False] * 200
        for i in range(0, 200, 2):
            discrete[i] = random.choice([True, False])
        
        # Создание datastore
        store = ModbusSlaveContext(
            di=ModbusSequentialDataBlock(0, discrete),
            co=ModbusSequentialDataBlock(0, coils),
            hr=ModbusSequentialDataBlock(0, holding),
            ir=ModbusSequentialDataBlock(0, input_regs)
        )
        
        return ModbusServerContext(slaves=store, single=True)
    
    def update_dynamic_values(self):
        """Динамическое обновление значений каждые 5 секунд"""
        while self.running:
            try:
                time.sleep(5)
                
                if not self.context:
                    continue
                
                slave_id = 0x00
                fx_code = 3  # Holding registers
                
                # Обновление температур (1000-1007)
                for zone in range(4):
                    addr = 1000 + zone * 2
                    temp = self.generate_temperature(zone)
                    regs = self.float_to_registers(temp)
                    self.context[slave_id].setValues(fx_code, addr, regs)
                
                # Обновление влажности (2000-2005)
                for sensor in range(3):
                    addr = 2000 + sensor * 2
                    hum = self.generate_humidity(sensor)
                    regs = self.float_to_registers(hum)
                    self.context[slave_id].setValues(fx_code, addr, regs)
                
                # Обновление давления (3000-3003)
                for sensor in range(2):
                    addr = 3000 + sensor * 2
                    press = self.generate_pressure('HP' if sensor == 0 else 'LP')
                    regs = self.float_to_registers(press)
                    self.context[slave_id].setValues(fx_code, addr, regs)
                
                # Обновление мощности (4000-4005)
                for meter in range(3):
                    addr = 4000 + meter * 2
                    power = self.generate_power('compressor' if meter < 2 else 'fans')
                    regs = self.float_to_registers(power)
                    self.context[slave_id].setValues(fx_code, addr, regs)
                
            except Exception as e:
                print(f"⚠️  Update error: {e}")
    
    def run(self):
        """Запуск эмулятора"""
        # Создание datastore
        self.context = self.create_datastore()
        
        # Device identification
        identity = ModbusDeviceIdentification()
        identity.VendorName = 'ProMonitor.kz'
        identity.ProductCode = 'ENHANCED-EMULATOR-V2'
        identity.VendorUrl = 'https://promonitor.kz'
        identity.ProductName = 'Enhanced Modbus Emulator v2.0'
        identity.ModelName = 'EMU-V2-800+'
        identity.MajorMinorRevision = '2.0.0'
        
        # Запуск потока обновления
        self.running = True
        self.update_thread = threading.Thread(target=self.update_dynamic_values, daemon=True)
        self.update_thread.start()
        
        print("\n✅ Emulator started successfully!")
        print(f"   Listening on: 0.0.0.0:5020")
        print(f"   Dynamic updates: Every 5 seconds")
        print(f"   Ready to accept connections...\n")
        
        # Запуск TCP сервера
        StartTcpServer(
            self.context,
            identity=identity,
            address=("0.0.0.0", 5020)
        )

if __name__ == "__main__":
    emulator = EnhancedModbusEmulatorV2()
    try:
        emulator.run()
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping emulator...")
        emulator.running = False
        print("✅ Emulator stopped")
