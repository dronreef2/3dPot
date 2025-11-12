"""
3dPot Backend - Modelo de Dados de Sensores
Sistema de Prototipagem Sob Demanda
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum as PyEnum
from sqlalchemy import String, Boolean, DateTime, Integer, Float, Text, Column, JSON, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database import Base


class SensorType(PyEnum):
    """Tipos de sensores suportados"""
    TEMPERATURE = "temperature"         # Temperatura (°C)
    HUMIDITY = "humidity"               # Umidade (%)
    WEIGHT = "weight"                   # Peso (g)
    VIBRATION = "vibration"            # Vibração (mm/s)
    SPEED = "speed"                     # Velocidade (mm/s)
    CURRENT = "current"                 # Corrente (A)
    VOLTAGE = "voltage"                 # Tensão (V)
    POWER = "power"                     # Potência (W)
    DISTANCE = "distance"               # Distância (mm)
    PRESSURE = "pressure"               # Pressão (Pa)
    FLOW_RATE = "flow_rate"             # Vazão (L/min)
    POSITION = "position"               # Posição (mm)


class DataQuality(PyEnum):
    """Qualidade dos dados coletados"""
    EXCELLENT = "excellent"    # Dados precisos e confiáveis
    GOOD = "good"             # Dados de boa qualidade
    FAIR = "fair"             # Dados aceitáveis
    POOR = "poor"             # Dados com ruído
    INVALID = "invalid"       # Dados inválidos


class SensorData(Base):
    """Modelo para dados de sensores coletados pelos dispositivos"""
    __tablename__ = "sensor_data"
    
    # === PRIMARY KEYS ===
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # === DEVICE REFERENCE ===
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    
    # === SENSOR INFO ===
    sensor_type = Column(String(50), nullable=False, index=True)
    sensor_name = Column(String(100), nullable=False)
    sensor_unit = Column(String(20), nullable=False)
    
    # === DATA VALUES ===
    value = Column(Float, nullable=False)
    raw_value = Column(Float, nullable=True)  # Valor bruto antes do processamento
    min_value = Column(Float, nullable=True)  # Valor mínimo da medição
    max_value = Column(Float, nullable=True)  # Valor máximo da medição
    avg_value = Column(Float, nullable=True)  # Valor médio da medição
    
    # === DATA QUALITY ===
    quality = Column(String(20), default=DataQuality.GOOD.value, nullable=False)
    confidence = Column(Float, nullable=True)  # 0.0 a 1.0
    is_anomaly = Column(Boolean, default=False, nullable=False)
    anomaly_score = Column(Float, nullable=True)
    
    # === TIMESTAMP ===
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    processing_time = Column(Float, nullable=True)  # Tempo de processamento em ms
    
    # === CONTEXT ===
    location = Column(String(100), nullable=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True, index=True)
    session_id = Column(String(100), nullable=True, index=True)
    
    # === SENSOR CALIBRATION ===
    calibration_offset = Column(Float, default=0.0, nullable=False)
    calibration_scale = Column(Float, default=1.0, nullable=False)
    is_calibrated = Column(Boolean, default=True, nullable=False)
    
    # === ENVIRONMENT ===
    temperature = Column(Float, nullable=True)  # Temperatura ambiente (°C)
    humidity = Column(Float, nullable=True)     # Umidade ambiente (%)
    pressure = Column(Float, nullable=True)     # Pressão ambiente (Pa)
    
    # === METADATA ===
    sensor_metadata = Column(JSON, nullable=True)  # Metadados extras do sensor
    notes = Column(Text, nullable=True)     # Observações sobre a medição
    
    # === TIMESTAMPS ===
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # === RELATIONSHIPS ===
    device = relationship("Device", back_populates="sensor_data")
    user = relationship("User", back_populates="sensor_data")
    # project = relationship("Project", back_populates="sensor_data")
    
    def __repr__(self) -> str:
        return f"<SensorData(id={self.id}, device_id={self.device_id}, type='{self.sensor_type}', value={self.value})>"
    
    def get_calibrated_value(self) -> float:
        """Retorna o valor calibrado da medição"""
        if not self.is_calibrated:
            return self.value
        return (self.value + self.calibration_offset) * self.calibration_scale
    
    def is_within_threshold(self, min_val: float, max_val: float) -> bool:
        """Verifica se o valor está dentro dos limites especificados"""
        value = self.get_calibrated_value()
        return min_val <= value <= max_val
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte os dados para dicionário"""
        return {
            "id": self.id,
            "device_id": self.device_id,
            "sensor_type": self.sensor_type,
            "sensor_name": self.sensor_name,
            "value": self.value,
            "calibrated_value": self.get_calibrated_value(),
            "unit": self.sensor_unit,
            "quality": self.quality,
            "is_anomaly": self.is_anomaly,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "location": self.location,
            "environment": {
                "temperature": self.temperature,
                "humidity": self.humidity,
                "pressure": self.pressure
            }
        }
    
    @classmethod
    def create_weight_data(
        cls,
        device_id: int,
        weight_g: float,
        timestamp: datetime = None,
        user_id: int = None,
        location: str = None
    ) -> "SensorData":
        """Helper para criar dados de peso"""
        return cls(
            device_id=device_id,
            user_id=user_id,
            sensor_type=SensorType.WEIGHT.value,
            sensor_name="HX711 Load Cell",
            sensor_unit="g",
            value=weight_g,
            raw_value=weight_g,
            timestamp=timestamp or datetime.utcnow(),
            location=location,
            calibration_offset=0.0,
            calibration_scale=1.0,
            quality=DataQuality.GOOD.value
        )
    
    @classmethod
    def create_temperature_data(
        cls,
        device_id: int,
        temperature_c: float,
        timestamp: datetime = None,
        user_id: int = None,
        location: str = None
    ) -> "SensorData":
        """Helper para criar dados de temperatura"""
        return cls(
            device_id=device_id,
            user_id=user_id,
            sensor_type=SensorType.TEMPERATURE.value,
            sensor_name="DS18B20 Temperature Sensor",
            sensor_unit="°C",
            value=temperature_c,
            timestamp=timestamp or datetime.utcnow(),
            location=location,
            calibration_offset=0.0,
            calibration_scale=1.0,
            quality=DataQuality.GOOD.value
        )
    
    @classmethod
    def create_humidity_data(
        cls,
        device_id: int,
        humidity_percent: float,
        timestamp: datetime = None,
        user_id: int = None,
        location: str = None
    ) -> "SensorData":
        """Helper para criar dados de umidade"""
        return cls(
            device_id=device_id,
            user_id=user_id,
            sensor_type=SensorType.HUMIDITY.value,
            sensor_name="DHT22 Humidity Sensor",
            sensor_unit="%",
            value=humidity_percent,
            timestamp=timestamp or datetime.utcnow(),
            location=location,
            calibration_offset=0.0,
            calibration_scale=1.0,
            quality=DataQuality.GOOD.value
        )
    
    class Config:
        from_attributes = True


# Índices para otimização de consultas
Index('idx_sensor_data_device_timestamp', SensorData.device_id, SensorData.timestamp)
Index('idx_sensor_data_type_timestamp', SensorData.sensor_type, SensorData.timestamp)
Index('idx_sensor_data_user_timestamp', SensorData.user_id, SensorData.timestamp)
Index('idx_sensor_data_project_timestamp', SensorData.project_id, SensorData.timestamp)
Index('idx_sensor_data_quality', SensorData.quality)
Index('idx_sensor_data_anomaly', SensorData.is_anomaly)
Index('idx_sensor_data_session', SensorData.session_id)
