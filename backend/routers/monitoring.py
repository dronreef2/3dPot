"""
3dPot Backend - Rotas de Monitoramento
Sistema de Prototipagem Sob Demanda
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel, Field
from loguru import logger

from backend.database import get_db
from backend.models.iot_user import User
from backend.models.iot_sensor_data import SensorData, SensorType
from backend.models.iot_device import Device

router = APIRouter()


class SensorDataResponse(BaseModel):
    """Schema para resposta de dados de sensor"""
    id: int
    device_id: int
    sensor_type: str
    sensor_name: str
    value: float
    calibrated_value: float
    unit: str
    quality: str
    is_anomaly: bool
    timestamp: datetime
    location: Optional[str]
    
    class Config:
        from_attributes = True


class SensorDataCreate(BaseModel):
    """Schema para criar dados de sensor"""
    device_id: int
    sensor_type: str
    sensor_name: str
    value: float
    unit: str
    timestamp: Optional[datetime] = None
    location: Optional[str] = None
    quality: str = "good"
    metadata: Optional[Dict[str, Any]] = None


class MonitoringStatsResponse(BaseModel):
    """Schema para estatísticas de monitoramento"""
    total_readings: int
    devices_online: int
    last_reading: Optional[datetime]
    readings_by_type: Dict[str, int]
    readings_last_hour: int


@router.get("/data", response_model=List[SensorDataResponse])
async def get_sensor_data(
    device_id: Optional[int] = Query(None, description="Filtrar por dispositivo"),
    sensor_type: Optional[str] = Query(None, description="Filtrar por tipo de sensor"),
    start_time: Optional[datetime] = Query(None, description="Data/hora inicial"),
    end_time: Optional[datetime] = Query(None, description="Data/hora final"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros"),
    db: AsyncSession = Depends(get_db)
):
    """Retorna dados de sensores com filtros opcionais"""
    try:
        query = select(SensorData)
        
        if device_id:
            query = query.where(SensorData.device_id == device_id)
        
        if sensor_type:
            query = query.where(SensorData.sensor_type == sensor_type)
        
        if start_time:
            query = query.where(SensorData.timestamp >= start_time)
        
        if end_time:
            query = query.where(SensorData.timestamp <= end_time)
        
        query = query.order_by(SensorData.timestamp.desc()).limit(limit)
        
        result = await db.execute(query)
        data = result.scalars().all()
        
        return data
        
    except Exception as e:
        logger.error(f"Error getting sensor data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get sensor data"
        )


@router.post("/data", response_model=SensorDataResponse, status_code=status.HTTP_201_CREATED)
async def create_sensor_data(
    data: SensorDataCreate,
    db: AsyncSession = Depends(get_db)
):
    """Cria novos dados de sensor"""
    try:
        # Verificar se dispositivo existe
        result = await db.execute(select(Device).where(Device.id == data.device_id))
        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Device not found"
            )
        
        # Criar dados de sensor
        sensor_data = SensorData(
            device_id=data.device_id,
            sensor_type=data.sensor_type,
            sensor_name=data.sensor_name,
            value=data.value,
            timestamp=data.timestamp or datetime.utcnow(),
            location=data.location,
            quality=data.quality,
            metadata=data.metadata
        )
        
        db.add(sensor_data)
        await db.commit()
        await db.refresh(sensor_data)
        
        logger.info(f"Sensor data created: {data.sensor_type} for device {data.device_id}")
        
        return sensor_data
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating sensor data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create sensor data"
        )


@router.get("/stats", response_model=MonitoringStatsResponse)
async def get_monitoring_stats(db: AsyncSession = Depends(get_db)):
    """Retorna estatísticas de monitoramento"""
    try:
        # Total de leituras
        total_result = await db.execute(select(func.count(SensorData.id)))
        total_readings = total_result.scalar() or 0
        
        # Dispositivos online
        devices_result = await db.execute(select(func.count(Device.id)).where(Device.status == "online"))
        devices_online = devices_result.scalar() or 0
        
        # Última leitura
        last_result = await db.execute(select(func.max(SensorData.timestamp)))
        last_reading = last_result.scalar()
        
        # Leituras por tipo
        type_result = await db.execute(select(SensorData.sensor_type, func.count(SensorData.id)).group_by(SensorData.sensor_type))
        readings_by_type = {sensor_type: count for sensor_type, count in type_result.all()}
        
        # Leituras na última hora
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        recent_result = await db.execute(
            select(func.count(SensorData.id)).where(SensorData.timestamp >= one_hour_ago)
        )
        readings_last_hour = recent_result.scalar() or 0
        
        return {
            "total_readings": total_readings,
            "devices_online": devices_online,
            "last_reading": last_reading,
            "readings_by_type": readings_by_type,
            "readings_last_hour": readings_last_hour
        }
        
    except Exception as e:
        logger.error(f"Error getting monitoring stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get monitoring statistics"
        )
