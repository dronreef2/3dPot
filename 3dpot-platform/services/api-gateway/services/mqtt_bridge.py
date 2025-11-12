"""
3dPot Platform - MQTT Bridge Service
Criado em: 2025-11-12 22:42:43
Autor: MiniMax Agent

Ponte entre MQTT (hardware) e REST API (frontend)
"""

import asyncio
import json
from typing import Dict, Any, Optional
import paho.mqtt.client as mqtt
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, insert
from datetime import datetime

# Import local modules
from models.database_models import HardwareDevice, DeviceTelemetry, Alert
from database.database import get_database
from utils.logger import get_logger

logger = get_logger("mqtt.bridge")

class MQTTBridgeService:
    """
    Service que conecta o hardware legado (ESP32, Arduino, Raspberry Pi) 
    via MQTT com a API REST da plataforma
    """
    
    def __init__(self, broker_url: str):
        self.broker_url = broker_url
        self.client = mqtt.Client()
        self.is_connected = False
        self.callbacks = {}
        self.router = APIRouter()
        
        # Configurar callbacks MQTT
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect
        
        # Registrar rotas da API
        self._register_routes()
        
    async def start(self):
        """Inicia conexão com broker MQTT"""
        try:
            # Parse URL
            if self.broker_url.startswith("mqtt://"):
                host_port = self.broker_url[7:]  # Remove "mqtt://"
            else:
                host_port = self.broker_url
                
            if ":" in host_port:
                host, port = host_port.split(":")
                port = int(port)
            else:
                host = host_port
                port = 1883
            
            self.client.connect(host, port, 60)
            self.client.loop_start()
            
            logger.info(f"🔌 Conectando ao MQTT broker: {host}:{port}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao conectar ao MQTT broker: {e}")
            raise
    
    async def stop(self):
        """Para conexão com broker MQTT"""
        self.client.loop_stop()
        self.client.disconnect()
        self.is_connected = False
        logger.info("🔌 Desconectado do MQTT broker")
    
    def _on_connect(self, client, userdata, flags, rc):
        """Callback quando conecta ao MQTT"""
        if rc == 0:
            self.is_connected = True
            logger.info("✅ Conectado ao MQTT broker")
            
            # Subscrever a todos os topics do 3dPot
            client.subscribe("3dpot/+/+/+")  # 3dpot/device_type/device_id/metric
            
        else:
            logger.error(f"❌ Falha na conexão MQTT: {rc}")
    
    def _on_disconnect(self, client, userdata, rc):
        """Callback quando desconecta do MQTT"""
        self.is_connected = False
        logger.warning(f"⚠️ Desconectado do MQTT broker: {rc}")
    
    def _on_message(self, client, userdata, msg):
        """Callback quando recebe mensagem MQTT"""
        try:
            topic = msg.topic.decode()
            payload = msg.payload.decode()
            
            logger.debug(f"📨 MQTT recebido: {topic} = {payload}")
            
            # Parse do topic: 3dpot/device_type/device_id/metric
            parts = topic.split('/')
            if len(parts) >= 4 and parts[0] == "3dpot":
                device_type = parts[1]
                device_id = parts[2]
                metric = parts[3]
                
                # Dispatch para handler específico
                asyncio.create_task(self._handle_message(device_type, device_id, metric, payload))
                
        except Exception as e:
            logger.error(f"❌ Erro ao processar mensagem MQTT: {e}")
    
    async def _handle_message(self, device_type: str, device_id: str, metric: str, payload: str):
        """Processa mensagem MQTT recebida"""
        try:
            # Buscar dispositivo no database
            # Implementação simplificada - usar cache Redis em produção
            logger.info(f"🔄 Processando mensagem: {device_type}/{device_id}/{metric}")
            
            # Simular processamento baseado no tipo de dispositivo
            if device_type == "esp32" and metric == "weight":
                await self._handle_weight_message(device_id, payload)
            elif device_type == "arduino" and metric == "status":
                await self._handle_status_message(device_id, payload)
            elif device_type == "raspberry" and metric == "qc_result":
                await self._handle_qc_message(device_id, payload)
            else:
                logger.warning(f"⚠️ Tipo de mensagem não suportado: {device_type}/{metric}")
                
        except Exception as e:
            logger.error(f"❌ Erro ao processar mensagem: {e}")
    
    async def _handle_weight_message(self, device_id: str, payload: str):
        """Processa mensagem de peso do ESP32"""
        try:
            data = json.loads(payload)
            weight_g = data.get("weight_g", 0)
            percentage = data.get("percentage", 0)
            
            logger.info(f"⚖️ Peso recebido: {weight_g}g ({percentage}%)")
            
            # Verificar alertas
            if percentage < 20:
                logger.warning(f"🚨 Filamento baixo: {percentage}%")
            
        except Exception as e:
            logger.error(f"❌ Erro ao processar peso: {e}")
    
    async def _handle_status_message(self, device_id: str, payload: str):
        """Processa mensagem de status do Arduino"""
        try:
            data = json.loads(payload)
            speed = data.get("speed", 0)
            object_detected = data.get("object_detected", False)
            
            status = "parado" if speed == 0 else "operacional"
            if object_detected:
                status = "processando"
            
            logger.info(f"🏃 Esteira {device_id}: {status} (velocidade: {speed})")
            
        except Exception as e:
            logger.error(f"❌ Erro ao processar status: {e}")
    
    async def _handle_qc_message(self, device_id: str, payload: str):
        """Processa mensagem de resultado QC do Raspberry Pi"""
        try:
            data = json.loads(payload)
            result = data.get("result", "unknown")
            score = data.get("score", 0)
            
            if result == "pass":
                logger.info(f"✅ QC aprovado: {score}%")
            else:
                logger.warning(f"❌ QC reprovado: {score}%")
                
        except Exception as e:
            logger.error(f"❌ Erro ao processar QC: {e}")
    
    def _register_routes(self):
        """Registra rotas REST para o hardware"""
        
        @self.router.get("/devices/status")
        async def get_devices_status(db: AsyncSession = Depends(get_database)):
            """Lista status de todos os dispositivos"""
            try:
                result = await db.execute(
                    select(HardwareDevice)
                    .order_by(HardwareDevice.device_type, HardwareDevice.name)
                )
                devices = result.scalars().all()
                
                return {
                    "devices": [
                        {
                            "device_id": d.device_id,
                            "device_type": d.device_type,
                            "name": d.name,
                            "status": d.status,
                            "location": d.location,
                            "last_seen": d.last_seen,
                            "configuration": d.configuration
                        }
                        for d in devices
                    ]
                }
            except Exception as e:
                logger.error(f"❌ Erro ao buscar dispositivos: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.get("/devices/{device_id}/telemetry")
        async def get_device_telemetry(
            device_id: str, 
            limit: int = 100,
            db: AsyncSession = Depends(get_database)
        ):
            """Busca telemetria de um dispositivo"""
            try:
                # Primeiro buscar o dispositivo
                device_result = await db.execute(
                    select(HardwareDevice).where(HardwareDevice.device_id == device_id)
                )
                device = device_result.scalar_one_or_none()
                
                if not device:
                    raise HTTPException(status_code=404, detail="Dispositivo não encontrado")
                
                # Buscar telemetria
                telemetry_result = await db.execute(
                    select(DeviceTelemetry)
                    .where(DeviceTelemetry.device_id == device.id)
                    .order_by(DeviceTelemetry.recorded_at.desc())
                    .limit(limit)
                )
                telemetry = telemetry_result.scalars().all()
                
                return {
                    "device_id": device_id,
                    "device_name": device.name,
                    "telemetry": [
                        {
                            "metric_type": t.metric_type,
                            "value": str(t.value),
                            "unit": t.unit,
                            "metadata": t.metadata,
                            "recorded_at": t.recorded_at.isoformat()
                        }
                        for t in telemetry
                    ]
                }
            except Exception as e:
                logger.error(f"❌ Erro ao buscar telemetria: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.post("/devices/{device_id}/send-command")
        async def send_device_command(
            device_id: str,
            command: Dict[str, Any],
            background_tasks: BackgroundTasks,
            db: AsyncSession = Depends(get_database)
        ):
            """Envia comando para um dispositivo"""
            try:
                # Buscar dispositivo
                device_result = await db.execute(
                    select(HardwareDevice).where(HardwareDevice.device_id == device_id)
                )
                device = device_result.scalar_one_or_none()
                
                if not device:
                    raise HTTPException(status_code=404, detail="Dispositivo não encontrado")
                
                # Executar comando em background
                background_tasks.add_task(self._execute_device_command, device, command)
                
                return {"message": "Comando enviado", "device_id": device_id, "command": command}
                
            except Exception as e:
                logger.error(f"❌ Erro ao enviar comando: {e}")
                raise HTTPException(status_code=500, detail=str(e))
    
    async def _execute_device_command(self, device: HardwareDevice, command: Dict[str, Any]):
        """Executa comando no dispositivo via MQTT"""
        try:
            # Definir comando baseado no tipo de dispositivo
            topic = f"3dpot/{device.device_type}/{device.device_id}/command"
            
            # Simular envio do comando
            logger.info(f"📤 Enviando comando para {device.device_id}: {command}")
            
            # Em produção, publicar no MQTT
            # self.client.publish(topic, json.dumps(command))
            
        except Exception as e:
            logger.error(f"❌ Erro ao executar comando: {e}")

# Instância global (será inicializada no main.py)
mqtt_bridge = None