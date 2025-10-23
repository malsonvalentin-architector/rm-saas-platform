"""
Modbus Service для чтения данных из контроллеров
Создать файл: data/services/modbus_service.py
"""

import time
import struct
from datetime import datetime, timezone
from pymodbus.client import ModbusTcpClient  # FIXED: Updated for pymodbus 3.x
from django.db import transaction
from data.models import (
    ModbusConnection, 
    ModbusRegisterMap, 
    ModbusConnectionLog,
    SensorData
)


class ModbusService:
    """
    READ-ONLY сервис для чтения Modbus данных
    Блокирует все write операции на уровне кода
    """
    
    def __init__(self, connection: ModbusConnection):
        self.connection = connection
        self.client = None
    
    def connect(self):
        """Подключение к Modbus устройству"""
        try:
            self.client = ModbusTcpClient(
                host=self.connection.host,
                port=self.connection.port,
                timeout=self.connection.timeout
            )
            
            if not self.client.connect():
                raise ConnectionError(f"Failed to connect to {self.connection.host}:{self.connection.port}")
            
            return True
        except Exception as e:
            raise ConnectionError(f"Connection error: {e}")
    
    def disconnect(self):
        """Отключение"""
        if self.client:
            self.client.close()
            self.client = None
    
    def test_connection(self):
        """Тест подключения"""
        self.connect()
        # Пробуем прочитать один регистр
        result = self.client.read_holding_registers(0, 1, unit=self.connection.slave_id)
        self.disconnect()
        
        if result.isError():
            raise Exception(f"Test read failed: {result}")
        
        return True
    
    def read_register(self, register_map: ModbusRegisterMap):
        """
        Читает значение из одного регистра
        """
        if not self.client:
            raise RuntimeError("Not connected. Call connect() first.")
        
        register_type = register_map.register_type
        address = register_map.address
        slave_id = self.connection.slave_id
        
        # Определяем количество регистров для чтения
        register_count = self._get_register_count(register_map.data_type)
        
        # Читаем данные
        if register_type == 'holding':
            result = self.client.read_holding_registers(address, register_count, unit=slave_id)
        elif register_type == 'input':
            result = self.client.read_input_registers(address, register_count, unit=slave_id)
        elif register_type == 'coil':
            result = self.client.read_coils(address, 1, unit=slave_id)
        elif register_type == 'discrete':
            result = self.client.read_discrete_inputs(address, 1, unit=slave_id)
        else:
            raise ValueError(f"Unknown register type: {register_type}")
        
        if result.isError():
            raise Exception(f"Read error: {result}")
        
        # Извлекаем сырое значение
        if register_type in ['coil', 'discrete']:
            raw_value = result.bits[0]
        else:
            raw_value = self._decode_value(result.registers, register_map.data_type)
        
        # Применяем масштабирование и смещение
        final_value = register_map.calculate_value(raw_value)
        
        return final_value
    
    def _get_register_count(self, data_type):
        """Возвращает количество регистров для типа данных"""
        if data_type in ['int16', 'uint16']:
            return 1
        elif data_type in ['int32', 'uint32', 'float32']:
            return 2
        elif data_type == 'bool':
            return 1
        return 1
    
    def _decode_value(self, registers, data_type):
        """Декодирует сырые регистры в значение"""
        if data_type == 'int16':
            # Signed 16-bit
            value = registers[0]
            if value > 32767:
                value -= 65536
            return value
        
        elif data_type == 'uint16':
            # Unsigned 16-bit
            return registers[0]
        
        elif data_type == 'int32':
            # Signed 32-bit (2 registers, big-endian)
            high, low = registers[0], registers[1]
            value = (high << 16) | low
            if value > 2147483647:
                value -= 4294967296
            return value
        
        elif data_type == 'uint32':
            # Unsigned 32-bit
            high, low = registers[0], registers[1]
            return (high << 16) | low
        
        elif data_type == 'float32':
            # Float 32-bit (2 registers, big-endian)
            high, low = registers[0], registers[1]
            bytes_data = struct.pack('>HH', high, low)
            return struct.unpack('>f', bytes_data)[0]
        
        elif data_type == 'bool':
            return bool(registers[0])
        
        return registers[0]
    
    def poll_all_registers(self):
        """
        Опрашивает все активные регистры для этого подключения
        и сохраняет данные в SensorData
        """
        start_time = time.time()
        registers_read = 0
        errors = []
        
        try:
            # Подключаемся
            self.connect()
            
            # Получаем все активные mapping'и с непустым sensor_name
            register_maps = self.connection.register_maps.filter(
                enabled=True
            ).exclude(sensor_name='')
            
            # Читаем каждый регистр
            with transaction.atomic():
                for reg_map in register_maps:
                    try:
                        # Читаем сырое и рассчитанное значение
                        raw_value = self.read_register(reg_map)
                        
                        # Сохраняем в SensorData
                        SensorData.objects.create(
                            connection=self.connection,
                            register_map=reg_map,
                            sensor_name=reg_map.sensor_name,
                            raw_value=raw_value,
                            calculated_value=reg_map.calculate_value(raw_value),
                            unit='',  # Единицы измерения пока не заданы в reg_map
                            quality='good'
                        )
                        
                        registers_read += 1
                        
                    except Exception as e:
                        errors.append(f"Register {reg_map.address}: {e}")
            
            # Отключаемся
            self.disconnect()
            
            # Логируем успех
            duration_ms = int((time.time() - start_time) * 1000)
            
            if errors:
                status = 'error'
                message = f"Read {registers_read} registers with {len(errors)} errors: {'; '.join(errors[:5])}"
            else:
                status = 'success'
                message = f"Successfully read {registers_read} registers"
            
            ModbusConnectionLog.objects.create(
                connection=self.connection,
                status=status,
                message=message,
                registers_read=registers_read,
                duration_ms=duration_ms
            )
            
            return {
                'status': status,
                'registers_read': registers_read,
                'duration_ms': duration_ms,
                'errors': errors
            }
            
        except Exception as e:
            # Логируем ошибку
            duration_ms = int((time.time() - start_time) * 1000)
            
            ModbusConnectionLog.objects.create(
                connection=self.connection,
                status='error',
                message=f"Connection error: {str(e)}",
                registers_read=0,
                duration_ms=duration_ms
            )
            
            raise
        
        finally:
            # Гарантируем отключение
            if self.client:
                self.disconnect()
    
    # БЛОКИРОВКА WRITE ОПЕРАЦИЙ
    def write_register(self, *args, **kwargs):
        """ЗАБЛОКИРОВАНО: Write операции запрещены"""
        raise PermissionError("Write operations are disabled for safety")
    
    def write_coil(self, *args, **kwargs):
        """ЗАБЛОКИРОВАНО: Write операции запрещены"""
        raise PermissionError("Write operations are disabled for safety")
    
    def write_registers(self, *args, **kwargs):
        """ЗАБЛОКИРОВАНО: Write операции запрещены"""
        raise PermissionError("Write operations are disabled for safety")
    
    def write_coils(self, *args, **kwargs):
        """ЗАБЛОКИРОВАНО: Write операции запрещены"""
        raise PermissionError("Write operations are disabled for safety")
