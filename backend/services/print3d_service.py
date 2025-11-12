"""
3dPot v2.0 - Serviço de Impressão 3D (Sprint 6+)
================================================

Serviço para gerenciamento completo de impressão 3D, incluindo:
- Gerenciamento de impressoras (Printer)
- Controle de fila de impressão (PrintQueue)
- Geração de G-code e configurações
- Monitoramento de jobs em tempo real
- Integração com APIs de impressoras

Autor: MiniMax Agent
Data: 2025-11-13
Versão: 2.0.0 - Sprint 6+
"""

import os
import json
import logging
import asyncio
import subprocess
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from uuid import UUID
from pathlib import Path

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
import numpy as np

from core.config import settings
from models import (
    Printer, Material, PrintJob, PrintQueue, PrintSettings, PrintJobLog,
    User, Project, Model3D
)
# Removido - schemas não implementados no momento
# from schemas import (
#     dict, dict, dict, dict, 
#     dict, dict, dict
# )

logger = logging.getLogger(__name__)


class Print3DService:
    """Serviço principal de impressão 3D"""
    
    def __init__(self):
        self.printer_apis = {}
        self.active_jobs = {}
        self.gcode_generators = {
            'cura': self._generate_gcode_cura,
            'slic3r': self._generate_gcode_slic3r,
            'simplify3d': self._generate_gcode_simplify3d,
            'custom': self._generate_gcode_custom
        }
    
    # =============================================================================
    # GERENCIAMENTO DE IMPRESSORAS
    # =============================================================================
    
    async def create_printer(
        self, 
        db: Session, 
        user_id: UUID, 
        printer_data: dict  # Substitui dict
    ) -> Printer:
        """Criar nova impressora"""
        try:
            # Verificar se usuário já tem impressora com mesmo nome
            existing_printer = db.query(Printer).filter(
                and_(
                    Printer.user_id == user_id,
                    Printer.nome == printer_data.nome
                )
            ).first()
            
            if existing_printer:
                raise ValueError("Usuário já possui uma impressora com este nome")
            
            # Criar impressora
            printer = Printer(
                user_id=user_id,
                **printer_data.dict()
            )
            
            db.add(printer)
            db.commit()
            db.refresh(printer)
            
            logger.info(f"Impressora criada: {printer.id} para usuário {user_id}")
            return printer
            
        except Exception as e:
            logger.error(f"Erro ao criar impressora: {e}")
            raise
    
    async def list_printers(
        self, 
        db: Session, 
        user_id: UUID, 
        include_inactive: bool = False
    ) -> List[Printer]:
        """Listar impressoras do usuário"""
        query = db.query(Printer).filter(Printer.user_id == user_id)
        
        if not include_inactive:
            query = query.filter(Printer.status != 'offline')
        
        printers = query.order_by(desc(Printer.created_at)).all()
        return printers
    
    async def update_printer(
        self,
        db: Session,
        printer_id: UUID,
        user_id: UUID,
        printer_data: dict  # Substitui dict
    ) -> Optional[Printer]:
        """Atualizar configuração de impressora"""
        try:
            printer = db.query(Printer).filter(
                and_(
                    Printer.id == printer_id,
                    Printer.user_id == user_id
                )
            ).first()
            
            if not printer:
                raise ValueError("Impressora não encontrada")
            
            # Atualizar campos
            update_data = printer_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(printer, field, value)
            
            printer.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(printer)
            
            logger.info(f"Impressora atualizada: {printer.id}")
            return printer
            
        except Exception as e:
            logger.error(f"Erro ao atualizar impressora: {e}")
            raise
    
    async def delete_printer(
        self,
        db: Session,
        printer_id: UUID,
        user_id: UUID
    ) -> bool:
        """Excluir impressora (soft delete)"""
        try:
            printer = db.query(Printer).filter(
                and_(
                    Printer.id == printer_id,
                    Printer.user_id == user_id
                )
            ).first()
            
            if not printer:
                raise ValueError("Impressora não encontrada")
            
            # Verificar se há jobs ativos
            active_jobs = db.query(PrintJob).filter(
                and_(
                    PrintJob.printer_id == printer_id,
                    PrintJob.status.in_(['pending', 'queueing', 'preparing', 'printing', 'paused'])
                )
            ).count()
            
            if active_jobs > 0:
                raise ValueError(f"Não é possível excluir impressora com {active_jobs} jobs ativos")
            
            # Marcar como inativa
            printer.status = 'offline'
            printer.esta_conectado = False
            printer.updated_at = datetime.utcnow()
            
            db.commit()
            
            logger.info(f"Impressora removida: {printer_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao excluir impressora: {e}")
            raise
    
    # =============================================================================
    # GERENCIAMENTO DE MATERIAIS
    # =============================================================================
    
    async def create_material(
        self,
        db: Session,
        user_id: UUID,
        material_data: dict
    ) -> Material:
        """Criar novo material"""
        try:
            # Verificar se material já existe
            existing_material = db.query(Material).filter(
                and_(
                    Material.nome == material_data.nome,
                    Material.fabricante == material_data.fabricante,
                    Material.codigo_produto == material_data.codigo_produto
                )
            ).first()
            
            if existing_material:
                raise ValueError("Material já existe no catálogo")
            
            # Criar material
            material = Material(**material_data.dict())
            
            db.add(material)
            db.commit()
            db.refresh(material)
            
            logger.info(f"Material criado: {material.id}")
            return material
            
        except Exception as e:
            logger.error(f"Erro ao criar material: {e}")
            raise
    
    async def get_materials(
        self,
        db: Session,
        category: Optional[str] = None,
        active_only: bool = True
    ) -> List[Material]:
        """Obter materiais disponíveis"""
        query = db.query(Material)
        
        if active_only:
            query = query.filter(Material.ativo == True)
        
        if category:
            query = query.filter(Material.categoria == category)
        
        materials = query.order_by(Material.nome).all()
        return materials
    
    async def search_materials(
        self,
        db: Session,
        query: str,
        max_results: int = 20
    ) -> List[Material]:
        """Buscar materiais por nome ou fabricante"""
        materials = db.query(Material).filter(
            and_(
                Material.ativo == True,
                or_(
                    Material.nome.ilike(f"%{query}%"),
                    Material.fabricante.ilike(f"%{query}%")
                )
            )
        ).limit(max_results).all()
        
        return materials
    
    # =============================================================================
    # GERENCIAMENTO DE JOBS DE IMPRESSÃO
    # =============================================================================
    
    async def create_print_job(
        self,
        db: Session,
        user_id: UUID,
        job_data: dict
    ) -> PrintJob:
        """Criar novo job de impressão"""
        try:
            # Verificar se projeto pertence ao usuário
            if job_data.project_id:
                project = db.query(Project).filter(
                    and_(
                        Project.id == job_data.project_id,
                        Project.owner_id == user_id
                    )
                ).first()
                
                if not project:
                    raise ValueError("Projeto não encontrado")
            
            # Verificar se modelo existe
            model_3d = db.query(Model3D).filter(Model3D.id == job_data.modelo_3d_id).first()
            if not model_3d:
                raise ValueError("Modelo 3D não encontrado")
            
            # Verificar impressora
            printer = db.query(Printer).filter(
                and_(
                    Printer.id == job_data.printer_id,
                    Printer.user_id == user_id
                )
            ).first()
            
            if not printer:
                raise ValueError("Impressora não encontrada")
            
            # Verificar material
            material = db.query(Material).filter(Material.id == job_data.material_id).first()
            if not material:
                raise ValueError("Material não encontrado")
            
            # Verificar compatibilidade
            if material.id not in printer.materiais_compatíveis:
                raise ValueError("Material não compatível com a impressora")
            
            # Calcular métricas do job
            metrics = await self._calculate_job_metrics(db, model_3d, material, printer, job_data)
            
            # Criar job
            print_job = PrintJob(
                user_id=user_id,
                project_id=job_data.project_id,
                printer_id=job_data.printer_id,
                material_id=job_data.material_id,
                arquivo_modelo=model_3d.arquivo_path,
                **metrics,
                **job_data.dict(exclude={'project_id', 'modelo_3d_id'})
            )
            
            db.add(print_job)
            db.commit()
            db.refresh(print_job)
            
            # Adicionar à fila
            await self._add_to_queue(db, print_job)
            
            logger.info(f"Job de impressão criado: {print_job.id}")
            return print_job
            
        except Exception as e:
            logger.error(f"Erro ao criar job de impressão: {e}")
            raise
    
    async def list_print_jobs(
        self,
        db: Session,
        user_id: UUID,
        status_filter: Optional[List[str]] = None,
        printer_id: Optional[UUID] = None,
        limit: int = 50
    ) -> List[PrintJob]:
        """Listar jobs de impressão do usuário"""
        query = db.query(PrintJob).filter(PrintJob.user_id == user_id)
        
        if status_filter:
            query = query.filter(PrintJob.status.in_(status_filter))
        
        if printer_id:
            query = query.filter(PrintJob.printer_id == printer_id)
        
        jobs = query.order_by(desc(PrintJob.created_at)).limit(limit).all()
        return jobs
    
    async def update_job_status(
        self,
        db: Session,
        job_id: UUID,
        user_id: UUID,
        status_update: dict,
        progress_data: Optional[Dict] = None
    ) -> Optional[PrintJob]:
        """Atualizar status e progresso do job"""
        try:
            job = db.query(PrintJob).filter(
                and_(
                    PrintJob.id == job_id,
                    PrintJob.user_id == user_id
                )
            ).first()
            
            if not job:
                raise ValueError("Job não encontrado")
            
            # Atualizar status
            old_status = job.status
            job.status = status_update.status
            job.updated_at = datetime.utcnow()
            
            # Atualizar timestamps específicos do status
            if status_update.status == 'printing' and old_status != 'printing':
                job.started_at = datetime.utcnow()
            elif status_update.status == 'completed':
                job.completed_at = datetime.utcnow()
                if job.started_at:
                    job.tempo_real_segundos = int(
                        (datetime.utcnow() - job.started_at).total_seconds()
                    )
            elif status_update.status == 'paused':
                job.paused_at = datetime.utcnow()
            elif status_update.status == 'failed':
                job.failed_at = datetime.utcnow()
            
            # Atualizar progresso
            if progress_data:
                if 'progress' in progress_data:
                    job.progresso_percentual = progress_data['progress']
                if 'current_layer' in progress_data:
                    job.camada_atual = progress_data['current_layer']
                if 'total_layers' in progress_data:
                    job.camadas_totais = progress_data['total_layers']
                if 'temperatures' in progress_data:
                    # Atualizar logs de temperatura
                    await self._log_job_event(
                        db, job.id, 'info', 
                        f"Temperaturas: Bico {progress_data['temperatures'].get('nozzle', 'N/A')}°C, "
                        f"Mesa {progress_data['temperatures'].get('bed', 'N/A')}°C"
                    )
            
            # Atualizar fila
            if status_update.status in ['printing', 'completed', 'failed', 'cancelled']:
                await self._update_queue_position(db, job)
            
            db.commit()
            db.refresh(job)
            
            logger.info(f"Status do job {job.id} atualizado para: {status_update.status}")
            return job
            
        except Exception as e:
            logger.error(f"Erro ao atualizar status do job: {e}")
            raise
    
    # =============================================================================
    # GERAÇÃO DE G-CODE
    # =============================================================================
    
    async def generate_gcode(
        self,
        db: Session,
        job_id: UUID,
        user_id: UUID,
        slicer_type: str = 'cura'
    ) -> str:
        """Gerar G-code para job de impressão"""
        try:
            job = db.query(PrintJob).filter(
                and_(
                    PrintJob.id == job_id,
                    PrintJob.user_id == user_id
                )
            ).first()
            
            if not job:
                raise ValueError("Job não encontrado")
            
            # Verificar se G-code já existe
            if job.arquivo_gcode and Path(job.arquivo_gcode).exists():
                return job.arquivo_gcode
            
            # Obter dados necessários
            printer = db.query(Printer).filter(Printer.id == job.printer_id).first()
            material = db.query(Material).filter(Material.id == job.material_id).first()
            
            # Selecionar gerador
            if slicer_type not in self.gcode_generators:
                raise ValueError(f"Slicer não suportado: {slicer_type}")
            
            generator_func = self.gcode_generators[slicer_type]
            gcode_path = await generator_func(job, printer, material)
            
            # Atualizar job com caminho do G-code
            job.arquivo_gcode = gcode_path
            db.commit()
            
            logger.info(f"G-code gerado para job {job.id}: {gcode_path}")
            return gcode_path
            
        except Exception as e:
            logger.error(f"Erro ao gerar G-code: {e}")
            raise
    
    # =============================================================================
    # FILA DE IMPRESSÃO
    # =============================================================================
    
    async def get_queue_status(
        self,
        db: Session,
        printer_id: UUID
    ) -> Dict[str, Any]:
        """Obter status da fila de impressão"""
        try:
            # Jobs na fila
            queue_items = db.query(PrintQueue).filter(
                PrintQueue.printer_id == printer_id
            ).order_by(PrintQueue.posicao).all()
            
            # Job atual (se houver)
            current_job = None
            current_queue = db.query(PrintQueue).filter(
                and_(
                    PrintQueue.printer_id == printer_id,
                    PrintQueue.status == 'processing'
                )
            ).first()
            
            if current_queue:
                current_job = db.query(PrintJob).filter(
                    PrintJob.id == current_queue.print_job_id
                ).first()
            
            queue_data = {
                'printer_id': printer_id,
                'current_job': current_job.to_dict() if current_job else None,
                'queue_length': len(queue_items),
                'estimated_total_time': sum(
                    item.print_job.tempo_estimado_segundos or 0 
                    for item in queue_items if item.print_job.tempo_estimado_segundos
                ),
                'queue_items': [
                    {
                        'position': item.posicao,
                        'job_id': item.print_job_id,
                        'job_name': item.print_job.nome,
                        'estimated_time': item.print_job.tempo_estimado_segundos,
                        'material': item.print_job.material.nome
                    }
                    for item in queue_items
                ]
            }
            
            return queue_data
            
        except Exception as e:
            logger.error(f"Erro ao obter status da fila: {e}")
            raise
    
    async def reorder_queue(
        self,
        db: Session,
        printer_id: UUID,
        user_id: UUID,
        job_order: List[UUID]
    ) -> bool:
        """Reordenar jobs na fila"""
        try:
            # Verificar se usuário é dono da impressora
            printer = db.query(Printer).filter(
                and_(
                    Printer.id == printer_id,
                    Printer.user_id == user_id
                )
            ).first()
            
            if not printer:
                raise ValueError("Impressora não encontrada")
            
            # Verificar se todos os jobs pertencem ao usuário
            jobs_in_order = db.query(PrintJob).filter(
                and_(
                    PrintJob.id.in_(job_order),
                    PrintJob.user_id == user_id,
                    PrintJob.printer_id == printer_id
                )
            ).all()
            
            if len(jobs_in_order) != len(job_order):
                raise ValueError("Alguns jobs não foram encontrados ou não pertencem ao usuário")
            
            # Atualizar posições na fila
            for index, job_id in enumerate(job_order, 1):
                queue_item = db.query(PrintQueue).filter(
                    and_(
                        PrintQueue.printer_id == printer_id,
                        PrintQueue.print_job_id == job_id
                    )
                ).first()
                
                if queue_item:
                    queue_item.posicao = index
                    queue_item.updated_at = datetime.utcnow()
            
            db.commit()
            
            logger.info(f"Fila reordenada para impressora {printer_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao reordenar fila: {e}")
            raise
    
    # =============================================================================
    # MONITORAMENTO E LOGS
    # =============================================================================
    
    async def get_job_logs(
        self,
        db: Session,
        job_id: UUID,
        user_id: UUID,
        log_type: Optional[str] = None,
        limit: int = 100
    ) -> List[PrintJobLog]:
        """Obter logs detalhados do job"""
        try:
            # Verificar ownership
            job = db.query(PrintJob).filter(
                and_(
                    PrintJob.id == job_id,
                    PrintJob.user_id == user_id
                )
            ).first()
            
            if not job:
                raise ValueError("Job não encontrado")
            
            # Buscar logs
            query = db.query(PrintJobLog).filter(
                PrintJobLog.print_job_id == job_id
            )
            
            if log_type:
                query = query.filter(PrintJobLog.tipo_log == log_type)
            
            logs = query.order_by(desc(PrintJobLog.timestamp)).limit(limit).all()
            return logs
            
        except Exception as e:
            logger.error(f"Erro ao obter logs do job: {e}")
            raise
    
    async def _log_job_event(
        self,
        db: Session,
        job_id: UUID,
        log_type: str,
        message: str,
        **kwargs
    ):
        """Registrar evento no log do job"""
        log_entry = PrintJobLog(
            print_job_id=job_id,
            tipo_log=log_type,
            message=message,
            timestamp=datetime.utcnow(),
            **kwargs
        )
        
        db.add(log_entry)
        # Não fazer commit aqui, será feito pelo caller
    
    # =============================================================================
    # MÉTODOS PRIVADOS
    # =============================================================================
    
    async def _calculate_job_metrics(
        self,
        db: Session,
        model: Model3D,
        material: Material,
        printer: Printer,
        job_data: dict
    ) -> Dict[str, Any]:
        """Calcular métricas estimadas do job"""
        try:
            # Volume estimado (assumindo material densidade 1.0 g/cm³ por padrão)
            volume_cm3 = model.volume_calculado or 0
            peso_estimado_g = volume_cm3 * (material.densidade or 1.0)
            
            # Custo do material
            custo_material = (peso_estimado_g / 1000) * float(material.preco_por_kg or 0)
            
            # Tempo estimado (simplificado)
            # Baseado em volume, velocidade de impressão e altura de camada
            speed_mm_s = job_data.velocidade_impressao or printer.velocidade_impressao_padrao
            layer_height = job_data.altura_camada or printer.resolucao_camada_padrao
            
            # Estimativa simplificada (precisaria de análise geométrica real)
            estimated_time_minutes = int(volume_cm3 * 60 / (speed_mm_s * layer_height * 100))  # Adjust factor
            
            metrics = {
                'peso_material_g': peso_estimado_g,
                'custo_material': custo_material,
                'tempo_estimado_segundos': estimated_time_minutes * 60,
                'volume_impressao_cm3': volume_cm3,
                'dimensao_x': model.numero_vertices or 100,  # Placeholder
                'dimensao_y': model.numero_faces or 100,     # Placeholder
                'dimensao_z': layer_height * 100  # Placeholder
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Erro ao calcular métricas do job: {e}")
            # Retornar valores padrão em caso de erro
            return {
                'peso_material_g': 0,
                'custo_material': 0,
                'tempo_estimado_segundos': 3600,  # 1 hora padrão
                'volume_impressao_cm3': 0,
                'dimensao_x': 0,
                'dimensao_y': 0,
                'dimensao_z': 0
            }
    
    async def _add_to_queue(
        self,
        db: Session,
        print_job: PrintJob
    ):
        """Adicionar job à fila de impressão"""
        try:
            # Obter próxima posição na fila
            last_position = db.query(PrintQueue).filter(
                PrintQueue.printer_id == print_job.printer_id
            ).count()
            
            queue_item = PrintQueue(
                printer_id=print_job.printer_id,
                print_job_id=print_job.id,
                posicao=last_position + 1,
                status='queued',
                created_at=datetime.utcnow()
            )
            
            db.add(queue_item)
            
            # Calcular tempos estimados
            if print_job.tempo_estimado_segundos:
                estimated_start = datetime.utcnow() + timedelta(
                    seconds=sum([
                        job.tempo_estimado_segundos or 0
                        for job in db.query(PrintJob).join(PrintQueue).filter(
                            PrintQueue.printer_id == print_job.printer_id,
                            PrintQueue.posicao <= last_position
                        ).all()
                    ])
                )
                
                estimated_end = estimated_start + timedelta(
                    seconds=print_job.tempo_estimado_segundos
                )
                
                queue_item.estimado_inicio = estimated_start
                queue_item.estimado_conclusao = estimated_end
            
            print_job.fila_posicao = last_position + 1
            db.commit()
            
        except Exception as e:
            logger.error(f"Erro ao adicionar job à fila: {e}")
            raise
    
    async def _update_queue_position(
        self,
        db: Session,
        print_job: PrintJob
    ):
        """Atualizar posições na fila quando job muda de status"""
        try:
            if print_job.status in ['printing', 'completed', 'failed', 'cancelled']:
                # Remover da fila ou marcar como processado
                queue_item = db.query(PrintQueue).filter(
                    and_(
                        PrintQueue.printer_id == print_job.printer_id,
                        PrintQueue.print_job_id == print_job.id
                    )
                ).first()
                
                if queue_item:
                    if print_job.status == 'printing':
                        queue_item.status = 'processing'
                    else:
                        queue_item.status = 'cancelled'
                        # Reorganizar fila
                        await self._reorganize_queue(db, print_job.printer_id)
                
                db.commit()
                
        except Exception as e:
            logger.error(f"Erro ao atualizar fila: {e}")
    
    async def _reorganize_queue(
        self,
        db: Session,
        printer_id: UUID
    ):
        """Reorganizar posições na fila"""
        try:
            queue_items = db.query(PrintQueue).filter(
                and_(
                    PrintQueue.printer_id == printer_id,
                    PrintQueue.status == 'queued'
                )
            ).order_by(PrintQueue.posicao).all()
            
            for index, item in enumerate(queue_items, 1):
                if item.posicao != index:
                    item.posicao = index
                    item.updated_at = datetime.utcnow()
                    
                    # Atualizar job também
                    job = db.query(PrintJob).filter(PrintJob.id == item.print_job_id).first()
                    if job:
                        job.fila_posicao = index
            
            db.commit()
            
        except Exception as e:
            logger.error(f"Erro ao reorganizar fila: {e}")
    
    # =============================================================================
    # GERADORES DE G-CODE
    # =============================================================================
    
    async def _generate_gcode_cura(
        self,
        job: PrintJob,
        printer: Printer,
        material: Material
    ) -> str:
        """Gerar G-code usando Cura (UCONF)"""
        try:
            # Gerar arquivo G-code usando configurações do job
            gcode_content = self._generate_basic_gcode(job, printer, material)
            
            # Salvar arquivo
            output_dir = Path(settings.TEMP_STORAGE_PATH) / "gcode"
            output_dir.mkdir(exist_ok=True)
            
            filename = f"job_{job.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.gcode"
            filepath = output_dir / filename
            
            with open(filepath, 'w') as f:
                f.write(gcode_content)
            
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Erro ao gerar G-code Cura: {e}")
            raise
    
    async def _generate_gcode_slic3r(
        self,
        job: PrintJob,
        printer: Printer,
        material: Material
    ) -> str:
        """Gerar G-code usando Slic3r"""
        return await self._generate_gcode_cura(job, printer, material)  # Simplified
    
    async def _generate_gcode_simplify3d(
        self,
        job: PrintJob,
        printer: Printer,
        material: Material
    ) -> str:
        """Gerar G-code usando Simplify3D"""
        return await self._generate_gcode_cura(job, printer, material)  # Simplified
    
    async def _generate_gcode_custom(
        self,
        job: PrintJob,
        printer: Printer,
        material: Material
    ) -> str:
        """Gerar G-code customizado"""
        return await self._generate_gcode_cura(job, printer, material)  # Simplified
    
    def _generate_basic_gcode(
        self,
        job: PrintJob,
        printer: Printer,
        material: Material
    ) -> str:
        """Gerar G-code básico"""
        gcode_lines = []
        
        # Header
        gcode_lines.append("; 3D Print Job G-code")
        gcode_lines.append(f"; Job ID: {job.id}")
        gcode_lines.append(f"; Created: {datetime.now().isoformat()}")
        gcode_lines.append("")
        
        # Inicialização
        gcode_lines.append("G28 ; Home all axes")
        gcode_lines.append("G90 ; Absolute positioning")
        gcode_lines.append("M82 ; Absolute E")
        gcode_lines.append("")
        
        # Temperaturas
        if job.temperatura_bico or material.temperatura_bico_recomendada:
            temp_nozzle = job.temperatura_bico or material.temperatura_bico_recomendada
            gcode_lines.append(f"M104 S{temp_nozzle} ; Set nozzle temperature")
        
        if job.temperatura_mesa or material.temperatura_mesa_recomendada:
            temp_bed = job.temperatura_mesa or material.temperatura_mesa_recomendada
            gcode_lines.append(f"M140 S{temp_bed} ; Set bed temperature")
        
        gcode_lines.append("M190 S ; Wait for bed temperature")
        gcode_lines.append("M109 S ; Wait for nozzle temperature")
        gcode_lines.append("")
        
        # Configurações de velocidade
        speed = job.velocidade_impressao or printer.velocidade_impressao_padrao
        gcode_lines.append(f"M201 X{5000} Y{5000} Z{200} E{5000} ; Set accelerations")
        gcode_lines.append(f"M203 X{speed*60} Y{speed*60} Z{1200} E{speed*60} ; Set max feedrates")
        gcode_lines.append(f"M204 R{3000} P{3000} T{3000} ; Set retract acceleration")
        gcode_lines.append("")
        
        # Coordenadas de impressão (simulado)
        gcode_lines.append("G1 X0 Y0 Z0.3 F3000")
        gcode_lines.append("G92 E0")
        gcode_lines.append("G1 Z1 F3000")
        gcode_lines.append("")
        
        # Simulação básica do modelo (seria substituída por slicing real)
        for layer in range(int(job.camadas_totais or 100)):
            z_height = layer * (job.altura_camada or 0.2)
            gcode_lines.append(f"; Layer {layer + 1}")
            gcode_lines.append(f"G1 Z{z_height:.2f}")
            gcode_lines.append("G1 X10 Y10 E1")
            gcode_lines.append("G1 X90 Y10 E5")
            gcode_lines.append("G1 X90 Y90 E9")
            gcode_lines.append("G1 X10 Y90 E13")
            gcode_lines.append("G1 X10 Y10 E17")
        
        gcode_lines.append("")
        gcode_lines.append("; Print complete")
        gcode_lines.append("M104 S0 ; Turn off hotend")
        gcode_lines.append("M140 S0 ; Turn off bed")
        gcode_lines.append("G91 ; Relative positioning")
        gcode_lines.append("G1 E-1 F300 ; Retract filament")
        gcode_lines.append("G1 E-1 Z1 F240 ; Retract filament")
        gcode_lines.append("G1 X0 Y0 Z5 F900 ; Move Z up")
        gcode_lines.append("G90 ; Absolute positioning")
        gcode_lines.append("G1 X0 Y{printer.volume_impressao_y/2} F3000 ; Move to park position")
        gcode_lines.append("M84 ; Disable motors")
        
        return "\n".join(gcode_lines)
    
    # =============================================================================
    # MÉTODOS DE ASSISTÊNCIA
    # =============================================================================
    
    async def get_printer_statistics(
        self,
        db: Session,
        user_id: UUID,
        printer_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """Obter estatísticas de impressão"""
        try:
            query = db.query(PrintJob).filter(PrintJob.user_id == user_id)
            
            if printer_id:
                query = query.filter(PrintJob.printer_id == printer_id)
            
            all_jobs = query.all()
            
            if not all_jobs:
                return {
                    'total_jobs': 0,
                    'completed_jobs': 0,
                    'failed_jobs': 0,
                    'success_rate': 0,
                    'total_print_time_hours': 0,
                    'total_material_used_g': 0,
                    'average_job_time_minutes': 0
                }
            
            # Calcular estatísticas
            total_jobs = len(all_jobs)
            completed_jobs = len([j for j in all_jobs if j.status == 'completed'])
            failed_jobs = len([j for j in all_jobs if j.status == 'failed'])
            success_rate = (completed_jobs / total_jobs * 100) if total_jobs > 0 else 0
            
            total_print_time = sum(j.tempo_real_segundos or 0 for j in all_jobs if j.tempo_real_segundos)
            total_material = sum(j.peso_material_g or 0 for j in all_jobs if j.peso_material_g)
            
            completed_jobs_with_time = [j for j in all_jobs if j.tempo_real_segundos and j.status == 'completed']
            avg_time = sum(j.tempo_real_segundos for j in completed_jobs_with_time) / len(completed_jobs_with_time) if completed_jobs_with_time else 0
            
            return {
                'total_jobs': total_jobs,
                'completed_jobs': completed_jobs,
                'failed_jobs': failed_jobs,
                'success_rate': round(success_rate, 1),
                'total_print_time_hours': round(total_print_time / 3600, 2),
                'total_material_used_g': round(total_material, 1),
                'average_job_time_minutes': round(avg_time / 60, 1)
            }
            
        except Exception as e:
            logger.error(f"Erro ao calcular estatísticas: {e}")
            return {}