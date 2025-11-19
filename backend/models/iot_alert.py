"""
3dPot Backend - Modelo de Alertas
Sistema de Prototipagem Sob Demanda
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum as PyEnum
from sqlalchemy import String, Boolean, DateTime, Integer, Float, Text, Column, JSON, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.database import Base


class AlertSeverity(PyEnum):
    """Severidade dos alertas"""
    LOW = "low"           # Informativo
    MEDIUM = "medium"     # Atenção necessária
    HIGH = "high"         # Problema importante
    CRITICAL = "critical" # Emergencia


class AlertStatus(PyEnum):
    """Status dos alertas"""
    ACTIVE = "active"      # Alerta ativo
    ACKNOWLEDGED = "acknowledged"  # Reconhecido
    RESOLVED = "resolved"  # Resolvido
    DISMISSED = "dismissed"  # Ignorado


class AlertType(PyEnum):
    """Tipos de alertas"""
    DEVICE_OFFLINE = "device_offline"          # Dispositivo offline
    TEMPERATURE_HIGH = "temperature_high"       # Temperatura alta
    TEMPERATURE_LOW = "temperature_low"         # Temperatura baixa
    HUMIDITY_HIGH = "humidity_high"            # Umidade alta
    HUMIDITY_LOW = "humidity_low"              # Umidade baixa
    WEIGHT_LOW = "weight_low"                  # Peso baixo (filamento)
    WEIGHT_HIGH = "weight_high"                # Peso alto
    BATTERY_LOW = "battery_low"                # Bateria baixa
    CONNECTIVITY_ISSUE = "connectivity_issue"   # Problema de conectividade
    SENSOR_MALFUNCTION = "sensor_malfunction"   # Mal funcionamento do sensor
    MAINTENANCE_REQUIRED = "maintenance_required"  # Manutenção necessária
    PERFORMANCE_DEGRADATION = "performance_degradation"  # Degradação de performance
    FIRMWARE_UPDATE = "firmware_update"         # Atualização de firmware disponível
    CALIBRATION_NEEDED = "calibration_needed"   # Calibração necessária
    CUSTOM = "custom"                           # Alerta personalizado


class Alert(Base):
    """Modelo de Alertas do sistema"""
    __tablename__ = "alerts"
    
    # === PRIMARY KEYS ===
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # === ALERT IDENTIFICATION ===
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=False)
    alert_type = Column(String(50), nullable=False, index=True)
    
    # === SEVERITY & STATUS ===
    severity = Column(String(20), nullable=False, index=True)
    status = Column(String(20), default=AlertStatus.ACTIVE.value, nullable=False, index=True)
    
    # === RELATED ENTITIES ===
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    sensor_data_id = Column(Integer, ForeignKey("sensor_data.id"), nullable=True, index=True)
    
    # === ALERT DATA ===
    threshold_value = Column(Float, nullable=True)  # Valor limite que disparou o alerta
    actual_value = Column(Float, nullable=True)     # Valor atual que causou o alerta
    sensor_unit = Column(String(20), nullable=True)
    
    # === RESOLUTION ===
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    resolution_notes = Column(Text, nullable=True)
    
    # === NOTIFICATIONS ===
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    acknowledged_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    notification_sent = Column(Boolean, default=False, nullable=False)
    notification_channels = Column(JSON, nullable=True)  # email, sms, push, webhook
    
    # === AUTO RESOLUTION ===
    auto_resolve = Column(Boolean, default=False, nullable=False)
    auto_resolve_threshold = Column(Float, nullable=True)
    
    # === CONTEXT ===
    location = Column(String(100), nullable=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True, index=True)
    alert_metadata = Column(JSON, nullable=True)  # Metadados extras
    
    # === RECURRENCE ===
    is_recurring = Column(Boolean, default=False, nullable=False)
    recurrence_count = Column(Integer, default=1, nullable=False)
    last_occurrence = Column(DateTime(timezone=True), nullable=True)
    
    # === TIMESTAMPS ===
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # === RELATIONSHIPS ===
    device = relationship("Device", back_populates="alerts")
    user = relationship("User", back_populates="alerts", foreign_keys=[user_id])
    resolved_by_user = relationship("User", foreign_keys=[resolved_by])
    acknowledged_by_user = relationship("User", foreign_keys=[acknowledged_by])
    sensor_data = relationship("SensorData")
    # project = relationship("Project", back_populates="alerts")
    
    def __repr__(self) -> str:
        return f"<Alert(id={self.id}, title='{self.title}', severity='{self.severity}', status='{self.status}')>"
    
    def acknowledge(self, user_id: int):
        """Marca o alerta como reconhecido"""
        self.status = AlertStatus.ACKNOWLEDGED.value
        self.acknowledged_at = datetime.utcnow()
        self.acknowledged_by = user_id
    
    def resolve(self, user_id: int, notes: str = None):
        """Marca o alerta como resolvido"""
        self.status = AlertStatus.RESOLVED.value
        self.resolved_at = datetime.utcnow()
        self.resolved_by = user_id
        if notes:
            self.resolution_notes = notes
    
    def dismiss(self):
        """Ignora o alerta"""
        self.status = AlertStatus.DISMISSED.value
    
    def is_active(self) -> bool:
        """Retorna True se o alerta está ativo"""
        return self.status == AlertStatus.ACTIVE.value
    
    def is_critical(self) -> bool:
        """Retorna True se o alerta é crítico"""
        return self.severity == AlertSeverity.CRITICAL.value
    
    def needs_attention(self) -> bool:
        """Retorna True se o alerta precisa de atenção"""
        return (
            self.is_active() and 
            self.severity in [AlertSeverity.HIGH.value, AlertSeverity.CRITICAL.value]
        )
    
    def get_age_hours(self) -> float:
        """Retorna a idade do alerta em horas"""
        if not self.created_at:
            return 0.0
        delta = datetime.utcnow() - self.created_at.replace(tzinfo=None)
        return delta.total_seconds() / 3600
    
    def is_expired(self, max_age_hours: int = 24) -> bool:
        """Verifica se o alerta expirou baseado na idade"""
        return self.get_age_hours() > max_age_hours
    
    def increment_recurrence(self):
        """Incrementa o contador de recorrência"""
        self.recurrence_count += 1
        self.last_occurrence = datetime.utcnow()
        if self.recurrence_count > 5:  # Limite de recorrências
            self.is_recurring = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte o alerta para dicionário"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "alert_type": self.alert_type,
            "severity": self.severity,
            "status": self.status,
            "device_id": self.device_id,
            "threshold_value": self.threshold_value,
            "actual_value": self.actual_value,
            "sensor_unit": self.sensor_unit,
            "location": self.location,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "age_hours": self.get_age_hours(),
            "needs_attention": self.needs_attention(),
            "is_expired": self.is_expired()
        }
    
    @classmethod
    def create_temperature_high(
        cls,
        device_id: int,
        temperature: float,
        threshold: float,
        user_id: int = None,
        location: str = None
    ) -> "Alert":
        """Helper para criar alerta de temperatura alta"""
        return cls(
            title=f"Temperatura Alta - {temperature}°C",
            description=f"A temperatura do dispositivo atingiu {temperature}°C, acima do limite de {threshold}°C",
            alert_type=AlertType.TEMPERATURE_HIGH.value,
            severity=AlertSeverity.HIGH.value if temperature > threshold + 5 else AlertSeverity.MEDIUM.value,
            device_id=device_id,
            user_id=user_id,
            threshold_value=threshold,
            actual_value=temperature,
            sensor_unit="°C",
            location=location,
            auto_resolve=True,
            auto_resolve_threshold=threshold - 2
        )
    
    @classmethod
    def create_weight_low(
        cls,
        device_id: int,
        weight: float,
        threshold: float,
        user_id: int = None,
        location: str = None
    ) -> "Alert":
        """Helper para criar alerta de peso baixo (filamento)"""
        return cls(
            title=f"Filamento Baixo - {weight}g",
            description=f"O peso do filamento está em {weight}g, abaixo do limite de {threshold}g",
            alert_type=AlertType.WEIGHT_LOW.value,
            severity=AlertSeverity.HIGH.value if weight < threshold / 2 else AlertSeverity.MEDIUM.value,
            device_id=device_id,
            user_id=user_id,
            threshold_value=threshold,
            actual_value=weight,
            sensor_unit="g",
            location=location,
            auto_resolve=False
        )
    
    @classmethod
    def create_device_offline(
        cls,
        device_id: int,
        last_seen: datetime,
        user_id: int = None,
        location: str = None
    ) -> "Alert":
        """Helper para criar alerta de dispositivo offline"""
        return cls(
            title="Dispositivo Offline",
            description=f"Dispositivo não responde há {last_seen.strftime('%Y-%m-%d %H:%M:%S')}",
            alert_type=AlertType.DEVICE_OFFLINE.value,
            severity=AlertSeverity.HIGH.value,
            device_id=device_id,
            user_id=user_id,
            location=location,
            auto_resolve=False
        )
    
    class Config:
        from_attributes = True


# Índices para otimização
Index('idx_alerts_device_status', Alert.device_id, Alert.status)
Index('idx_alerts_severity_status', Alert.severity, Alert.status)
Index('idx_alerts_user_status', Alert.user_id, Alert.status)
Index('idx_alerts_created_at', Alert.created_at)
Index('idx_alerts_active_critical', Alert.status, Alert.severity)
Index('idx_alerts_device_type', Alert.device_id, Alert.alert_type)
