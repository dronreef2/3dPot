"""
3dPot Backend - Rotas de Gerenciamento de Alertas
Sistema de Prototipagem Sob Demanda
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from pydantic import BaseModel, Field
from loguru import logger

from ..database import get_db
from ..models.user import User
from ..models.alert import Alert, AlertStatus, AlertSeverity

router = APIRouter()


class AlertResponse(BaseModel):
    """Schema para resposta de alerta"""
    id: int
    title: str
    description: str
    alert_type: str
    severity: str
    status: str
    device_id: Optional[int]
    threshold_value: Optional[float]
    actual_value: Optional[float]
    sensor_unit: Optional[str]
    location: Optional[str]
    created_at: datetime
    acknowledged_at: Optional[datetime]
    resolved_at: Optional[datetime]
    age_hours: float
    needs_attention: bool
    is_expired: bool
    
    class Config:
        from_attributes = True


class AlertAcknowledge(BaseModel):
    """Schema para reconhecimento de alerta"""
    notes: Optional[str] = None


class AlertResolve(BaseModel):
    """Schema para resolução de alerta"""
    notes: str = Field(..., min_length=1)


@router.get("/", response_model=List[AlertResponse])
async def list_alerts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None, description="Filtrar por status"),
    severity: Optional[str] = Query(None, description="Filtrar por severidade"),
    device_id: Optional[int] = Query(None, description="Filtrar por dispositivo"),
    is_active: Optional[bool] = Query(True, description="Apenas alertas ativos"),
    db: AsyncSession = Depends(get_db)
):
    """Lista alertas com filtros opcionais"""
    try:
        query = select(Alert)
        
        if status:
            query = query.where(Alert.status == status)
        
        if severity:
            query = query.where(Alert.severity == severity)
        
        if device_id:
            query = query.where(Alert.device_id == device_id)
        
        if is_active:
            query = query.where(Alert.status == AlertStatus.ACTIVE.value)
        
        query = query.order_by(Alert.created_at.desc()).offset(skip).limit(limit)
        
        result = await db.execute(query)
        alerts = result.scalars().all()
        
        # Adicionar campos calculados
        alert_responses = []
        for alert in alerts:
            alert_dict = alert.to_dict()
            alert_responses.append(AlertResponse(**alert_dict))
        
        return alert_responses
        
    except Exception as e:
        logger.error(f"Error listing alerts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list alerts"
        )


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(
    alert_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Retorna detalhes de um alerta"""
    try:
        result = await db.execute(select(Alert).where(Alert.id == alert_id))
        alert = result.scalar_one_or_none()
        
        if not alert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alert not found"
            )
        
        return AlertResponse(**alert.to_dict())
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting alert {alert_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get alert"
        )


@router.post("/{alert_id}/acknowledge", response_model=AlertResponse)
async def acknowledge_alert(
    acknowledge_data: AlertAcknowledge,
    alert_id: int,
    current_user: User = Depends(lambda: None),
    db: AsyncSession = Depends(get_db)
):
    """Reconhece um alerta"""
    try:
        result = await db.execute(select(Alert).where(Alert.id == alert_id))
        alert = result.scalar_one_or_none()
        
        if not alert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alert not found"
            )
        
        alert.acknowledge(current_user.id if current_user else 1)
        await db.commit()
        await db.refresh(alert)
        
        logger.info(f"Alert acknowledged: {alert.title}")
        
        return AlertResponse(**alert.to_dict())
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error acknowledging alert {alert_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to acknowledge alert"
        )


@router.post("/{alert_id}/resolve", response_model=AlertResponse)
async def resolve_alert(
    resolve_data: AlertResolve,
    alert_id: int,
    current_user: User = Depends(lambda: None),
    db: AsyncSession = Depends(get_db)
):
    """Resolve um alerta"""
    try:
        result = await db.execute(select(Alert).where(Alert.id == alert_id))
        alert = result.scalar_one_or_none()
        
        if not alert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alert not found"
            )
        
        alert.resolve(current_user.id if current_user else 1, resolve_data.notes)
        await db.commit()
        await db.refresh(alert)
        
        logger.info(f"Alert resolved: {alert.title}")
        
        return AlertResponse(**alert.to_dict())
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error resolving alert {alert_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to resolve alert"
        )


@router.post("/{alert_id}/dismiss", response_model=AlertResponse)
async def dismiss_alert(
    alert_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Ignora um alerta"""
    try:
        result = await db.execute(select(Alert).where(Alert.id == alert_id))
        alert = result.scalar_one_or_none()
        
        if not alert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alert not found"
            )
        
        alert.dismiss()
        await db.commit()
        await db.refresh(alert)
        
        logger.info(f"Alert dismissed: {alert.title}")
        
        return AlertResponse(**alert.to_dict())
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error dismissing alert {alert_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to dismiss alert"
        )


@router.get("/stats/summary")
async def get_alerts_stats(db: AsyncSession = Depends(get_db)):
    """Retorna estatísticas de alertas"""
    try:
        # Total de alertas
        total_result = await db.execute(select(func.count(Alert.id)))
        total_alerts = total_result.scalar() or 0
        
        # Alertas ativos
        active_result = await db.execute(
            select(func.count(Alert.id)).where(Alert.status == AlertStatus.ACTIVE.value)
        )
        active_alerts = active_result.scalar() or 0
        
        # Alertas críticos
        critical_result = await db.execute(
            select(func.count(Alert.id)).where(
                Alert.severity == AlertSeverity.CRITICAL.value,
                Alert.status == AlertStatus.ACTIVE.value
            )
        )
        critical_alerts = critical_result.scalar() or 0
        
        # Alertas nas últimas 24 horas
        day_ago = datetime.utcnow() - timedelta(days=1)
        day_result = await db.execute(
            select(func.count(Alert.id)).where(Alert.created_at >= day_ago)
        )
        alerts_last_day = day_result.scalar() or 0
        
        # Alertas por severidade
        severity_result = await db.execute(
            select(Alert.severity, func.count(Alert.id))
            .group_by(Alert.severity)
        )
        alerts_by_severity = {severity: count for severity, count in severity_result.all()}
        
        # Alertas por status
        status_result = await db.execute(
            select(Alert.status, func.count(Alert.id))
            .group_by(Alert.status)
        )
        alerts_by_status = {status: count for status, count in status_result.all()}
        
        return {
            "total_alerts": total_alerts,
            "active_alerts": active_alerts,
            "critical_alerts": critical_alerts,
            "alerts_last_day": alerts_last_day,
            "alerts_by_severity": alerts_by_severity,
            "alerts_by_status": alerts_by_status,
            "last_updated": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Error getting alerts stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get alerts statistics"
        )
