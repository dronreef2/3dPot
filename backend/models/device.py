"""
3dPot Backend - Modelo de Dispositivo
Sistema de Prototipagem Sob Demanda
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum as PyEnum
from sqlalchemy import String, Boolean, DateTime, Integer, Float, Text, Column, JSON, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database import Base


class DeviceType(PyEnum):
    """Tipos de dispositivos suportados"""
    ESP32_MONITOR = "esp32_monitor"           # Monitor de filamento ESP32
    ARDUINO_ESTEIRA = "arduino_esteira"       # Esteira transportadora Arduino
    RASPBERRY_QC = "raspberry_qc"             # Estação de QC Raspberry Pi
    PRINTER = "printer"                       # Impressora 3D
    SENSOR_TEMPERATURE = "sensor_temperature" # Sensor de temperatura
    SENSOR_HUMIDITY = "sensor_humidity"       # Sensor de umidade
    SENSOR_WEIGHT = "sensor_weight"           # Sensor de peso


class DeviceStatus(PyEnum):
    """Status do dispositivo"""
    ONLINE = "online"         # Conectado e operacional
    OFFLINE = "offline"       # Desconectado
    ERROR = "error"           # Em estado de erro
    MAINTENANCE = "maintenance" # Em manutenção
    UPDATING = "updating"     # Atualizando firmware
    UNKNOWN = "unknown"       # Status desconhecido


class Device(Base):
    """Modelo de Dispositivo IoT"""
    __tablename__ = "devices"
    
    # === PRIMARY KEYS ===
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # === DEVICE IDENTIFICATION ===
    name = Column(String(100), nullable=False, index=True)
    device_type = Column(String(50), nullable=False, index=True)
    serial_number = Column(String(100), unique=True, index=True, nullable=False)
    mac_address = Column(String(17), unique=True, index=True, nullable=True)
    
    # === LOCATION ===
    location = Column(String(100), nullable=True)
    room = Column(String(50), nullable=True)
    floor = Column(Integer, nullable=True)
    zone = Column(String(50), nullable=True)
    
    # === STATUS ===
    status = Column(String(20), default=DeviceStatus.UNKNOWN.value, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    last_seen = Column(DateTime(timezone=True), nullable=True)
    
    # === HARDWARE INFO ===
    firmware_version = Column(String(50), nullable=True)
    hardware_version = Column(String(50), nullable=True)
    cpu_usage = Column(Float, nullable=True)
    memory_usage = Column(Float, nullable=True)
    battery_level = Column(Integer, nullable=True)  # 0-100%
    
    # === NETWORK INFO ===
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible
    wifi_ssid = Column(String(100), nullable=True)
    connection_type = Column(String(20), default="wifi", nullable=False)
    signal_strength = Column(Integer, nullable=True)  # dBm
    
    # === CONFIGURATION ===
    config = Column(JSON, nullable=True)  # Configurações específicas do dispositivo
    settings = Column(JSON, nullable=True)  # Configurações personalizadas
    device_metadata = Column(JSON, nullable=True)  # Metadados extras
    
    # === OWNERSHIP ===
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # === METADATA ===
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # === RELATIONSHIPS ===
    owner = relationship("User", back_populates="devices")
    sensor_data = relationship("SensorData", back_populates="device", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="device", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Device(id={self.id}, name='{self.name}', type='{self.device_type}', status='{self.status}')>"
    
    def update_status(self, status: DeviceStatus, additional_data: Dict[str, Any] = None):
        """Atualiza o status do dispositivo"""
        self.status = status.value
        self.last_seen = datetime.utcnow()
        
        if additional_data:
            if not self.config:
                self.config = {}
            self.config.update(additional_data)
    
    def is_online(self) -> bool:
        """Retorna True se o dispositivo está online"""
        return self.status == DeviceStatus.ONLINE.value
    
    def is_offline(self) -> bool:
        """Retorna True se o dispositivo está offline"""
        return self.status in [DeviceStatus.OFFLINE.value, DeviceStatus.UNKNOWN.value]
    
    def needs_maintenance(self) -> bool:
        """Retorna True se o dispositivo precisa de manutenção"""
        return (
            self.status == DeviceStatus.ERROR.value or
            self.cpu_usage and self.cpu_usage > 90 or
            self.memory_usage and self.memory_usage > 90 or
            self.battery_level and self.battery_level < 20
        )
    
    def get_config_value(self, key: str, default: Any = None) -> Any:
        """Obtém um valor específico da configuração"""
        if not self.config:
            return default
        return self.config.get(key, default)
    
    def set_config_value(self, key: str, value: Any):
        """Define um valor específico na configuração"""
        if not self.config:
            self.config = {}
        self.config[key] = value
    
    def get_setting_value(self, key: str, default: Any = None) -> Any:
        """Obtém um valor específico das configurações personalizadas"""
        if not self.settings:
            return default
        return self.settings.get(key, default)
    
    def set_setting_value(self, key: str, value: Any):
        """Define um valor específico nas configurações personalizadas"""
        if not self.settings:
            self.settings = {}
        self.settings[key] = value
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte o dispositivo para dicionário"""
        return {
            "id": self.id,
            "name": self.name,
            "device_type": self.device_type,
            "serial_number": self.serial_number,
            "status": self.status,
            "is_active": self.is_active,
            "location": self.location,
            "firmware_version": self.firmware_version,
            "last_seen": self.last_seen.isoformat() if self.last_seen else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def create_esp32_monitor(
        cls,
        name: str,
        serial_number: str,
        mac_address: str = None,
        location: str = None,
        owner_id: int = None
    ) -> "Device":
        """Helper para criar um monitor ESP32"""
        return cls(
            name=name,
            device_type=DeviceType.ESP32_MONITOR.value,
            serial_number=serial_number,
            mac_address=mac_address,
            location=location,
            owner_id=owner_id,
            config={
                "mqtt_topic": f"sensors/{serial_number}/filament",
                "calibration": {"zero_point": 0, "scale_factor": 1.0},
                "alerts": {"min_weight": 10, "max_weight": 1000}
            }
        )
    
    @classmethod
    def create_arduino_esteira(
        cls,
        name: str,
        serial_number: str,
        location: str = None,
        owner_id: int = None
    ) -> "Device":
        """Helper para criar uma esteira Arduino"""
        return cls(
            name=name,
            device_type=DeviceType.ARDUINO_ESTEIRA.value,
            serial_number=serial_number,
            location=location,
            owner_id=owner_id,
            config={
                "motor_settings": {"speed": 100, "acceleration": 50},
                "sensors": {"ir_threshold": 500, "limit_switches": True},
                "safety": {"max_runtime": 3600, "emergency_stop": True}
            }
        )
    
    class Config:
        from_attributes = True


# Índices para otimização
Index('idx_devices_serial', Device.serial_number)
Index('idx_devices_type', Device.device_type)
Index('idx_devices_status', Device.status)
Index('idx_devices_owner', Device.owner_id)
Index('idx_devices_last_seen', Device.last_seen)
Index('idx_devices_is_active', Device.is_active)
