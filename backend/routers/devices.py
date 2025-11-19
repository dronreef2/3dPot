"""
3dPot Backend - Rotas de Gerenciamento de Dispositivos
Sistema de Prototipagem Sob Demanda
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from pydantic import BaseModel, Field
from loguru import logger

from backend.database import get_db
from backend.app.models.user import User
from backend.app.models.device import Device, DeviceType, DeviceStatus
from backend.core.config import settings


router = APIRouter()


# === SCHEMAS ===

class DeviceCreate(BaseModel):
    """Schema para criação de dispositivo"""
    name: str = Field(..., min_length=1, max_length=100)
    device_type: str = Field(..., min_length=1, max_length=50)
    serial_number: str = Field(..., min_length=1, max_length=100)
    mac_address: Optional[str] = Field(None, max_length=17)
    location: Optional[str] = Field(None, max_length=100)
    room: Optional[str] = Field(None, max_length=50)
    floor: Optional[int] = Field(None, ge=1, le=100)
    zone: Optional[str] = Field(None, max_length=50)
    firmware_version: Optional[str] = Field(None, max_length=50)
    config: Optional[Dict[str, Any]] = None
    settings: Optional[Dict[str, Any]] = None


class DeviceUpdate(BaseModel):
    """Schema para atualização de dispositivo"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    location: Optional[str] = Field(None, max_length=100)
    room: Optional[str] = Field(None, max_length=50)
    floor: Optional[int] = Field(None, ge=1, le=100)
    zone: Optional[str] = Field(None, max_length=50)
    firmware_version: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None
    config: Optional[Dict[str, Any]] = None
    settings: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class DeviceResponse(BaseModel):
    """Schema para resposta de dispositivo"""
    id: int
    name: str
    device_type: str
    serial_number: str
    mac_address: Optional[str]
    location: Optional[str]
    status: str
    is_active: bool
    last_seen: Optional[datetime]
    firmware_version: Optional[str]
    hardware_version: Optional[str]
    cpu_usage: Optional[float]
    memory_usage: Optional[float]
    battery_level: Optional[int]
    ip_address: Optional[str]
    wifi_ssid: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class DeviceStatusUpdate(BaseModel):
    """Schema para atualização de status do dispositivo"""
    status: str = Field(..., pattern="^(online|offline|error|maintenance|updating)$")
    additional_data: Optional[Dict[str, Any]] = None


class ESP32MonitorCreate(BaseModel):
    """Schema para criação de monitor ESP32"""
    name: str = Field(..., description="Nome do monitor")
    serial_number: str = Field(..., description="Número de série")
    mac_address: Optional[str] = Field(None, description="Endereço MAC")
    location: Optional[str] = Field(None, description="Localização")


class DeviceStatsResponse(BaseModel):
    """Schema para estatísticas de dispositivos"""
    total_devices: int
    online_devices: int
    offline_devices: int
    devices_by_type: Dict[str, int]
    devices_by_status: Dict[str, int]
    last_updated: datetime


# === DEPENDENCIES ===

async def get_device_by_id(
    device_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(lambda: None)  # Opcional para alguns endpoints
) -> Device:
    """
    Dependency para obter dispositivo por ID.
    
    Raises:
        HTTPException: Se dispositivo não encontrado
    """
    result = await db.execute(select(Device).where(Device.id == device_id))
    device = result.scalar_one_or_none()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    
    return device


# === DEVICE ENDPOINTS ===

@router.get("/", response_model=List[DeviceResponse])
async def list_devices(
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros"),
    device_type: Optional[str] = Query(None, description="Filtrar por tipo de dispositivo"),
    status: Optional[str] = Query(None, description="Filtrar por status"),
    location: Optional[str] = Query(None, description="Filtrar por localização"),
    is_active: Optional[bool] = Query(None, description="Filtrar por status ativo"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(lambda: None)  # Opcional para listagem pública
):
    """
    Lista dispositivos com filtros opcionais.
    
    - **skip**: Quantidade de registros para pular
    - **limit**: Quantidade máxima de registros (padrão: 100)
    - **device_type**: Filtrar por tipo (esp32_monitor, arduino_esteira, etc.)
    - **status**: Filtrar por status (online, offline, error, etc.)
    - **location**: Filtrar por localização
    - **is_active**: Filtrar por status ativo
    """
    try:
        query = select(Device)
        
        # Aplicar filtros
        if device_type:
            query = query.where(Device.device_type == device_type)
        
        if status:
            query = query.where(Device.status == status)
        
        if location:
            query = query.where(Device.location.contains(location))
        
        if is_active is not None:
            query = query.where(Device.is_active == is_active)
        
        # Paginação e ordenação
        query = query.order_by(Device.created_at.desc()).offset(skip).limit(limit)
        
        result = await db.execute(query)
        devices = result.scalars().all()
        
        return devices
        
    except Exception as e:
        logger.error(f"Error listing devices: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list devices"
        )


@router.post("/", response_model=DeviceResponse, status_code=status.HTTP_201_CREATED)
async def create_device(
    device_data: DeviceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(lambda: None)  # Opcional por enquanto
):
    """
    Cria um novo dispositivo.
    
    - **name**: Nome do dispositivo
    - **device_type**: Tipo do dispositivo
    - **serial_number**: Número de série único
    - **mac_address**: Endereço MAC (opcional)
    - **location**: Localização física
    """
    try:
        # Verificar se serial_number já existe
        result = await db.execute(
            select(Device).where(Device.serial_number == device_data.serial_number)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Device with this serial number already exists"
            )
        
        # Validar tipo de dispositivo
        valid_types = [device_type.value for device_type in DeviceType]
        if device_data.device_type not in valid_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid device type. Valid types: {', '.join(valid_types)}"
            )
        
        # Criar dispositivo
        db_device = Device(
            name=device_data.name,
            device_type=device_data.device_type,
            serial_number=device_data.serial_number,
            mac_address=device_data.mac_address,
            location=device_data.location,
            room=device_data.room,
            floor=device_data.floor,
            zone=device_data.zone,
            firmware_version=device_data.firmware_version,
            status=DeviceStatus.UNKNOWN.value,
            is_active=True,
            config=device_data.config,
            settings=device_data.settings,
            owner_id=current_user.id if current_user else None
        )
        
        db.add(db_device)
        await db.commit()
        await db.refresh(db_device)
        
        logger.info(f"Device created: {db_device.name} ({db_device.serial_number})")
        
        return db_device
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating device: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create device"
        )


@router.get("/{device_id}", response_model=DeviceResponse)
async def get_device(
    device: Device = Depends(get_device_by_id)
):
    """Retorna detalhes de um dispositivo específico"""
    return device


@router.put("/{device_id}", response_model=DeviceResponse)
async def update_device(
    device_data: DeviceUpdate,
    device: Device = Depends(get_device_by_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Atualiza informações de um dispositivo.
    
    Todos os campos são opcionais para atualização parcial.
    """
    try:
        # Aplicar atualizações
        update_data = device_data.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(device, field, value)
        
        device.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(device)
        
        logger.info(f"Device updated: {device.name}")
        
        return device
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating device {device.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update device"
        )


@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_device(
    device: Device = Depends(get_device_by_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Remove um dispositivo (soft delete - marca como inativo).
    
    Em vez de deletar, marca o dispositivo como inativo para manter histórico.
    """
    try:
        device.is_active = False
        device.updated_at = datetime.utcnow()
        
        await db.commit()
        
        logger.info(f"Device deactivated: {device.name}")
        
        return {"message": "Device deactivated successfully"}
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deactivating device {device.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to deactivate device"
        )


@router.patch("/{device_id}/status", response_model=DeviceResponse)
async def update_device_status(
    status_data: DeviceStatusUpdate,
    device: Device = Depends(get_device_by_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Atualiza o status de um dispositivo.
    
    - **status**: Novo status (online, offline, error, maintenance, updating)
    - **additional_data**: Dados adicionais para atualizar configurações
    """
    try:
        # Validar status
        valid_statuses = [status.value for status in DeviceStatus]
        if status_data.status not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Valid statuses: {', '.join(valid_statuses)}"
            )
        
        # Atualizar status
        device.status = status_data.status
        device.last_seen = datetime.utcnow()
        
        # Atualizar dados adicionais se fornecidos
        if status_data.additional_data:
            if not device.config:
                device.config = {}
            device.config.update(status_data.additional_data)
        
        await db.commit()
        await db.refresh(device)
        
        logger.info(f"Device status updated: {device.name} -> {device.status}")
        
        return device
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating device status {device.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update device status"
        )


@router.get("/{device_id}/config", response_model=Dict[str, Any])
async def get_device_config(
    device: Device = Depends(get_device_by_id)
):
    """Retorna configurações de um dispositivo"""
    return {
        "config": device.config or {},
        "settings": device.settings or {},
        "metadata": device.metadata or {}
    }


@router.put("/{device_id}/config", response_model=DeviceResponse)
async def update_device_config(
    config_data: Dict[str, Any],
    device: Device = Depends(get_device_by_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Atualiza configurações de um dispositivo.
    
    - **config**: Configurações específicas do dispositivo
    - **settings**: Configurações personalizadas
    - **metadata**: Metadados extras
    """
    try:
        if "config" in config_data:
            device.config = config_data["config"]
        
        if "settings" in config_data:
            device.settings = config_data["settings"]
        
        if "metadata" in config_data:
            device.metadata = config_data["metadata"]
        
        device.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(device)
        
        logger.info(f"Device config updated: {device.name}")
        
        return device
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating device config {device.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update device configuration"
        )


@router.get("/stats/summary", response_model=DeviceStatsResponse)
async def get_devices_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(lambda: None)  # Opcional por enquanto
):
    """
    Retorna estatísticas resumidas dos dispositivos.
    
    - **total_devices**: Total de dispositivos
    - **online_devices**: Dispositivos online
    - **offline_devices**: Dispositivos offline
    - **devices_by_type**: Contagem por tipo
    - **devices_by_status**: Contagem por status
    """
    try:
        # Total de dispositivos
        total_result = await db.execute(select(Device))
        total_devices = len(total_result.scalars().all())
        
        # Dispositivos online
        online_result = await db.execute(
            select(Device).where(Device.status == DeviceStatus.ONLINE.value)
        )
        online_devices = len(online_result.scalars().all())
        
        # Dispositivos offline
        offline_result = await db.execute(
            select(Device).where(Device.status.in_([DeviceStatus.OFFLINE.value, DeviceStatus.UNKNOWN.value]))
        )
        offline_devices = len(offline_result.scalars().all())
        
        # Dispositivos por tipo
        type_result = await db.execute(select(Device.device_type, Device.id))
        devices_by_type = {}
        for device_type, _ in type_result.all():
            devices_by_type[device_type] = devices_by_type.get(device_type, 0) + 1
        
        # Dispositivos por status
        status_result = await db.execute(select(Device.status, Device.id))
        devices_by_status = {}
        for status, _ in status_result.all():
            devices_by_status[status] = devices_by_status.get(status, 0) + 1
        
        return {
            "total_devices": total_devices,
            "online_devices": online_devices,
            "offline_devices": offline_devices,
            "devices_by_type": devices_by_type,
            "devices_by_status": devices_by_status,
            "last_updated": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Error getting devices stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get devices statistics"
        )


@router.post("/esp32/monitor", response_model=DeviceResponse, status_code=status.HTTP_201_CREATED)
async def create_esp32_monitor(
    device_data: ESP32MonitorCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(lambda: None)
):
    """
    Cria um monitor ESP32 com configurações padrão para monitoramento de filamento.
    
    Helper específico para dispositivos ESP32 que monitoram peso de filamento.
    """
    try:
        # Verificar se serial_number já existe
        result = await db.execute(
            select(Device).where(Device.serial_number == device_data.serial_number)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Device with this serial number already exists"
            )
        
        # Configurações padrão para ESP32 monitor
        default_config = {
            "mqtt_topic": f"sensors/{device_data.serial_number}/filament",
            "calibration": {"zero_point": 0, "scale_factor": 1.0},
            "alerts": {
                "min_weight": 10,    # Alerta quando filamento < 10g
                "max_weight": 1000,  # Alerta quando filamento > 1000g
                "check_interval": 30  # Verificação a cada 30 segundos
            },
            "sensor": {
                "type": "hx711",
                "pin_dout": 2,
                "pin_sck": 3
            },
            "wifi": {
                "auto_connect": True,
                "timeout": 30
            }
        }
        
        db_device = Device.create_esp32_monitor(
            name=device_data.name,
            serial_number=device_data.serial_number,
            mac_address=device_data.mac_address,
            location=device_data.location,
            owner_id=current_user.id if current_user else None
        )
        
        db.add(db_device)
        await db.commit()
        await db.refresh(db_device)
        
        logger.info(f"ESP32 monitor created: {db_device.name} ({db_device.serial_number})")
        
        return db_device
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating ESP32 monitor: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create ESP32 monitor"
        )
