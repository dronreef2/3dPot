#!/usr/bin/env python3
"""
3dPot Backend - Script de Inicialização
Sistema de Prototipagem Sob Demanda

Este script inicializa o backend FastAPI criando tabelas e dados de teste.
"""

import asyncio
import sys
import os
from pathlib import Path

# Adicionar o diretório do projeto ao path
sys.path.insert(0, str(Path(__file__).parent))

from loguru import logger
from app.database import create_tables, AsyncSessionLocal
from app.models.user import User
from app.models.device import Device, DeviceType
from app.models.project import Project, ProjectType


async def create_test_user(db) -> User:
    """Cria um usuário de teste"""
    # Verificar se usuário já existe
    from sqlalchemy import select
    result = await db.execute(select(User).where(User.email == "admin@3dpot.com"))
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        logger.info("Usuário de teste já existe")
        return existing_user
    
    # Criar usuário admin
    admin_user = User.create_user(
        email="admin@3dpot.com",
        username="admin",
        password="admin123",
        full_name="Administrador 3dPot"
    )
    
    admin_user.is_superuser = True
    admin_user.is_verified = True
    admin_user.role = "admin"
    
    db.add(admin_user)
    await db.commit()
    await db.refresh(admin_user)
    
    logger.info(f"✅ Usuário de teste criado: {admin_user.email}")
    return admin_user


async def create_test_devices(db, user: User) -> list[Device]:
    """Cria dispositivos de teste"""
    devices = []
    
    # ESP32 Monitor de Filamento
    esp32_device = Device.create_esp32_monitor(
        name="Monitor Filamento Principal",
        serial_number="ESP32_001",
        mac_address="AA:BB:CC:DD:EE:01",
        location="Lab Principal",
        owner_id=user.id
    )
    esp32_device.status = "online"
    esp32_device.firmware_version = "1.0.0"
    
    db.add(esp32_device)
    devices.append(esp32_device)
    
    # Arduino Esteira Transportadora
    arduino_device = Device.create_arduino_esteira(
        name="Esteira Transportadora",
        serial_number="ARDUINO_001", 
        location="Estação de Impressão",
        owner_id=user.id
    )
    arduino_device.status = "online"
    
    db.add(arduino_device)
    devices.append(arduino_device)
    
    # Raspberry QC Station
    raspberry_device = Device(
        name="Estação QC Raspberry",
        device_type=DeviceType.RASPBERRY_QC.value,
        serial_number="RPI_001",
        location="Estação de Controle",
        status="online",
        owner_id=user.id,
        config={
            "camera": {
                "resolution": "1920x1080",
                "fps": 30
            },
            "opencv": {
                "debug_mode": False
            }
        }
    )
    
    db.add(raspberry_device)
    devices.append(raspberry_device)
    
    await db.commit()
    
    for device in devices:
        await db.refresh(device)
        logger.info(f"✅ Dispositivo criado: {device.name} ({device.device_type})")
    
    return devices


async def create_test_projects(db, user: User) -> list[Project]:
    """Cria projetos de teste"""
    projects = []
    
    # Projeto de Protótipo
    prototype_project = Project.create_prototype_project(
        name="Protótipo Suporte ESP32",
        owner_id=user.id,
        description="Projeto para criar suporte parametric para monitor ESP32",
        filament_type="PLA"
    )
    prototype_project.status = "in_progress"
    prototype_project.progress_percentage = 65
    prototype_project.filament_weight_start = 1000.0
    prototype_project.filament_weight_end = 850.0
    prototype_project.budget = 250.0
    
    db.add(prototype_project)
    projects.append(prototype_project)
    
    # Projeto de Produção
    production_project = Project(
        name="Lote Estações QC",
        description="Projeto de produção para 10 estações de controle de qualidade",
        project_type=ProjectType.PRODUCTION.value,
        priority="high",
        owner_id=user.id,
        status="planning",
        progress_percentage=10,
        budget=5000.0,
        estimated_hours=40.0
    )
    
    db.add(production_project)
    projects.append(production_project)
    
    await db.commit()
    
    for project in projects:
        await db.refresh(project)
        logger.info(f"✅ Projeto criado: {project.name}")
    
    return projects


async def main():
    """Função principal de inicialização"""
    logger.info("🚀 Iniciando 3dPot Backend...")
    
    try:
        # Criar tabelas
        logger.info("📊 Criando tabelas do banco de dados...")
        await create_tables()
        
        # Conectar ao banco
        async with AsyncSessionLocal() as db:
            # Criar usuário de teste
            logger.info("👤 Criando usuário de teste...")
            user = await create_test_user(db)
            
            # Criar dispositivos de teste
            logger.info("📱 Criando dispositivos de teste...")
            devices = await create_test_devices(db, user)
            
            # Criar projetos de teste
            logger.info("📁 Criando projetos de teste...")
            projects = await create_test_projects(db, user)
        
        logger.info("✅ 3dPot Backend inicializado com sucesso!")
        logger.info(f"📊 Usuário: admin@3dpot.com / admin123")
        logger.info(f"📱 Dispositivos criados: {len(devices)}")
        logger.info(f"📁 Projetos criados: {len(projects)}")
        logger.info("🌐 Acesse: http://localhost:8000/docs")
        
    except Exception as e:
        logger.error(f"❌ Erro na inicialização: {e}")
        raise


if __name__ == "__main__":
    # Configurar logging
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO"
    )
    
    # Executar inicialização
    asyncio.run(main())
