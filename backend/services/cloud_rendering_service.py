"""
3dPot v2.0 - Serviço de Renderização em Nuvem (Sprint 6+)
========================================================

Serviço para renderização em nuvem e processamento GPU distribuído, incluindo:
- Gestão de clusters de GPU (GPUCluster)
- Processamento de jobs de renderização (RenderJob)
- Configurações de renderização (RenderSettings)
- Templates de qualidade (QualityPreset)
- Renderização em lote (BatchRenderConfig)
- Estimativas de custo (CostEstimate)

Autor: MiniMax Agent
Data: 2025-11-13
Versão: 2.0.0 - Sprint 6+
"""

import os
import json
import logging
import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from uuid import UUID
from decimal import Decimal
from pathlib import Path

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func, text
from sqlalchemy.orm import joinedload

from backend.core.config import settings
from backend.models import (
    GPUCluster, RenderJob, RenderSettings, QualityPreset, BatchRenderConfig,
    CostEstimate, RenderNode, RenderJobLog,
    User, Project, Model3D
)

logger = logging.getLogger(__name__)


class CloudRenderingService:
    """Serviço principal de renderização em nuvem"""
    
    def __init__(self):
        # Configurações de renderização
        self.render_engines = {
            'cycles': {
                'name': 'Cycles',
                'description': 'Renderizador físico baseado em path tracing',
                'supports_gpu': True,
                'supports_cpu': True,
                'default_samples': 128
            },
            'eevee': {
                'name': 'Eevee',
                'description': 'Renderizador em tempo real rasterizado',
                'supports_gpu': True,
                'supports_cpu': False,
                'default_samples': 64
            },
            'octane': {
                'name': 'Octane Render',
                'description': 'Renderizador GPU comercial',
                'supports_gpu': True,
                'supports_cpu': False,
                'default_samples': 1000
            },
            'vray': {
                'name': 'V-Ray',
                'description': 'Renderizador comercial da Chaos Group',
                'supports_gpu': True,
                'supports_cpu': True,
                'default_samples': 500
            },
            'arnold': {
                'name': 'Arnold',
                'description': 'Renderizador Monte Carlo da Autodesk',
                'supports_gpu': True,
                'supports_cpu': True,
                'default_samples': 256
            }
        }
        
        # Tipos de GPU e seus custos por hora (USD)
        self.gpu_costs_per_hour = {
            'RTX_4090': 2.50,
            'RTX_3090': 2.00,
            'RTX_3080': 1.50,
            'RTX_3070': 1.00,
            'A100': 5.00,
            'V100': 3.00,
            'Tesla_T4': 1.25,
            'CPU_16_core': 0.50,
            'CPU_32_core': 1.00
        }
        
        # Qualidade padrão dos presets
        self.quality_presets = {
            'draft': {
                'samples': 32,
                'max_bounces': 4,
                'tile_size': 512,
                'time_multiplier': 0.5,
                'quality_score': 30
            },
            'standard': {
                'samples': 128,
                'max_bounces': 8,
                'tile_size': 256,
                'time_multiplier': 1.0,
                'quality_score': 60
            },
            'high': {
                'samples': 256,
                'max_bounces': 12,
                'tile_size': 128,
                'time_multiplier': 2.0,
                'quality_score': 85
            },
            'ultra': {
                'samples': 512,
                'max_bounces': 16,
                'tile_size': 64,
                'time_multiplier': 4.0,
                'quality_score': 95
            },
            'cinema': {
                'samples': 1024,
                'max_bounces': 24,
                'tile_size': 32,
                'time_multiplier': 8.0,
                'quality_score': 100
            }
        }
    
    # =============================================================================
    # GESTÃO DE CLUSTERS DE GPU
    # =============================================================================
    
    async def create_gpu_cluster(
        self,
        db: Session,
        cluster_data: Dict[str, Any]
    ) -> GPUCluster:
        """Criar novo cluster de GPU"""
        try:
            # Verificar se cluster com mesmo nome já existe
            existing = db.query(GPUCluster).filter(
                and_(
                    GPUCluster.nome == cluster_data['nome'],
                    GPUCluster.provider == cluster_data['provider'],
                    GPUCluster.region == cluster_data['region']
                )
            ).first()
            
            if existing:
                raise ValueError("Cluster com este nome já existe nesta região")
            
            # Calcular custo baseado em especificações
            cost_per_hour = await self._calculate_cluster_cost(cluster_data)
            
            # Criar cluster
            cluster = GPUCluster(
                nome=cluster_data['nome'],
                provider=cluster_data['provider'],
                region=cluster_data['region'],
                zona=cluster_data.get('zona'),
                tipo_cluster=cluster_data.get('tipo_cluster', 'gpu'),
                gpu_model=cluster_data.get('gpu_model'),
                gpu_count=cluster_data.get('gpu_count', 0),
                gpu_memory_gb=cluster_data.get('gpu_memory_gb'),
                cpu_cores=cluster_data['cpu_cores'],
                cpu_model=cluster_data.get('cpu_model'),
                cpu_memory_gb=cluster_data['cpu_memory_gb'],
                storage_gb=cluster_data['storage_gb'],
                storage_type=cluster_data.get('storage_type'),
                bandwidth_gbps=cluster_data.get('bandwidth_gbps'),
                latency_ms=cluster_data.get('latency_ms'),
                status='available',
                custo_para_hora=cost_per_hour,
                moeda=cluster_data.get('moeda', 'USD'),
                benchmarks=cluster_data.get('benchmarks', {}),
                auto_scaling=cluster_data.get('auto_scaling', False),
                min_instances=cluster_data.get('min_instances', 1),
                max_instances=cluster_data.get('max_instances', 10)
            )
            
            db.add(cluster)
            db.commit()
            db.refresh(cluster)
            
            logger.info(f"Cluster GPU criado: {cluster.id}")
            return cluster
            
        except Exception as e:
            logger.error(f"Erro ao criar cluster GPU: {e}")
            raise
    
    async def list_gpu_clusters(
        self,
        db: Session,
        status_filter: Optional[List[str]] = None,
        provider: Optional[str] = None,
        region: Optional[str] = None
    ) -> List[GPUCluster]:
        """Listar clusters de GPU disponíveis"""
        try:
            query = db.query(GPUCluster)
            
            if status_filter:
                query = query.filter(GPUCluster.status.in_(status_filter))
            
            if provider:
                query = query.filter(GPUCluster.provider == provider)
            
            if region:
                query = query.filter(GPUCluster.region == region)
            
            clusters = query.order_by(desc(GPUCluster.throughput_score)).all()
            return clusters
            
        except Exception as e:
            logger.error(f"Erro ao listar clusters GPU: {e}")
            raise
    
    async def get_cluster_status(
        self,
        db: Session,
        cluster_id: UUID
    ) -> Dict[str, Any]:
        """Obter status detalhado do cluster"""
        try:
            cluster = db.query(GPUCluster).filter(GPUCluster.id == cluster_id).first()
            
            if not cluster:
                raise ValueError("Cluster não encontrado")
            
            # Contar jobs ativos
            active_jobs = db.query(RenderJob).filter(
                and_(
                    RenderJob.gpu_cluster_id == cluster_id,
                    RenderJob.status.in_(['queued', 'preparing', 'rendering', 'post_processing'])
                )
            ).count()
            
            # Calcular uso de recursos
            total_gpu_memory = (cluster.gpu_memory_gb or 0) * (cluster.gpu_count or 0)
            used_gpu_memory = 0  # Simplificado - seria calculado baseado em jobs ativos
            
            # Obter nodes se houver
            nodes = db.query(RenderNode).filter(RenderNode.cluster_id == cluster_id).all()
            
            return {
                'cluster_id': cluster.id,
                'name': cluster.nome,
                'status': cluster.status,
                'active_jobs': active_jobs,
                'total_gpu_memory_gb': total_gpu_memory,
                'used_gpu_memory_gb': used_gpu_memory,
                'cpu_cores_total': cluster.cpu_cores,
                'cpu_memory_gb': cluster.cpu_memory_gb,
                'storage_gb': cluster.storage_gb,
                'nodes_count': len(nodes),
                'last_health_check': cluster.last_health_check,
                'cost_per_hour': float(cluster.custo_para_hora),
                'throughput_score': cluster.throughput_score
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter status do cluster: {e}")
            raise
    
    # =============================================================================
    # GESTÃO DE JOBS DE RENDERIZAÇÃO
    # =============================================================================
    
    async def create_render_job(
        self,
        db: Session,
        user_id: UUID,
        job_data: Dict[str, Any]
    ) -> RenderJob:
        """Criar novo job de renderização"""
        try:
            # Verificar se usuário existe
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValueError("Usuário não encontrado")
            
            # Verificar se projeto existe (se fornecido)
            project = None
            if job_data.get('project_id'):
                project = db.query(Project).filter(
                    and_(
                        Project.id == job_data['project_id'],
                        Project.owner_id == user_id
                    )
                ).first()
                
                if not project:
                    raise ValueError("Projeto não encontrado")
            
            # Verificar se modelo 3D existe
            model_3d = db.query(Model3D).filter(
                Model3D.id == job_data['modelo_3d_id']
            ).first()
            
            if not model_3d:
                raise ValueError("Modelo 3D não encontrado")
            
            # Verificar cluster
            cluster = db.query(GPUCluster).filter(
                GPUCluster.id == job_data['gpu_cluster_id']
            ).first()
            
            if not cluster:
                raise ValueError("Cluster GPU não encontrado")
            
            if cluster.status != 'available':
                raise ValueError("Cluster GPU não está disponível")
            
            # Verificar engine suportado
            if job_data['render_engine'] not in self.render_engines:
                raise ValueError(f"Engine não suportado: {job_data['render_engine']}")
            
            engine_info = self.render_engines[job_data['render_engine']]
            if job_data['device'] == 'gpu' and not engine_info['supports_gpu']:
                raise ValueError("Engine não suporta renderização por GPU")
            elif job_data['device'] == 'cpu' and not engine_info['supports_cpu']:
                raise ValueError("Engine não suporta renderização por CPU")
            
            # Calcular estimativas
            job_metrics = await self._calculate_job_metrics(
                model_3d, job_data, cluster
            )
            
            # Criar job
            render_job = RenderJob(
                user_id=user_id,
                project_id=job_data.get('project_id'),
                modelo_3d_path=model_3d.arquivo_path,
                configuracao_path=job_data.get('configuracao_path'),
                nome=job_data['nome'],
                descricao=job_data.get('descricao'),
                resolution_x=job_data['resolution_x'],
                resolution_y=job_data['resolution_y'],
                framerate=job_data.get('framerate', 30),
                duracao_segundos=job_data.get('duracao_segundos'),
                qualidade=job_data.get('qualidade', 'standard'),
                samples=job_data.get('samples') or engine_info['default_samples'],
                denoise=job_data.get('denoise', True),
                motion_blur=job_data.get('motion_blur', True),
                depth_of_field=job_data.get('depth_of_field', True),
                render_engine=job_data['render_engine'],
                device=job_data.get('device', 'gpu'),
                gpu_cluster_id=job_data['gpu_cluster_id'],
                gpu_memory_required_gb=job_data.get('gpu_memory_required_gb'),
                cpu_cores_required=job_data.get('cpu_cores_required'),
                status='queued',
                tempo_estimado_segundos=job_metrics['estimated_time'],
                custo_estimado=job_metrics['estimated_cost'],
                arquivos_saida=job_data.get('arquivos_saida', {}),
                notify_on_completion=job_data.get('notify_on_completion', True),
                notify_on_failure=job_data.get('notify_on_failure', True)
            )
            
            db.add(render_job)
            db.commit()
            db.refresh(render_job)
            
            # Agendar job para processamento
            await self._schedule_job(db, render_job)
            
            logger.info(f"Job de renderização criado: {render_job.id}")
            return render_job
            
        except Exception as e:
            logger.error(f"Erro ao criar job de renderização: {e}")
            raise
    
    async def list_render_jobs(
        self,
        db: Session,
        user_id: UUID,
        status_filter: Optional[List[str]] = None,
        cluster_id: Optional[UUID] = None,
        limit: int = 50
    ) -> List[RenderJob]:
        """Listar jobs de renderização do usuário"""
        try:
            query = db.query(RenderJob).filter(RenderJob.user_id == user_id)
            
            if status_filter:
                query = query.filter(RenderJob.status.in_(status_filter))
            
            if cluster_id:
                query = query.filter(RenderJob.gpu_cluster_id == cluster_id)
            
            jobs = query.order_by(desc(RenderJob.created_at)).limit(limit).options(
                joinedload(RenderJob.gpu_cluster),
                joinedload(RenderJob.project)
            ).all()
            
            return jobs
            
        except Exception as e:
            logger.error(f"Erro ao listar jobs de renderização: {e}")
            raise
    
    async def get_job_status(
        self,
        db: Session,
        job_id: UUID,
        user_id: UUID
    ) -> Dict[str, Any]:
        """Obter status detalhado do job"""
        try:
            job = db.query(RenderJob).filter(
                and_(
                    RenderJob.id == job_id,
                    RenderJob.user_id == user_id
                )
            ).first()
            
            if not job:
                raise ValueError("Job não encontrado")
            
            # Obter logs detalhados
            logs = db.query(RenderJobLog).filter(
                RenderJobLog.render_job_id == job_id
            ).order_by(desc(RenderJobLog.timestamp)).limit(50).all()
            
            return {
                'job_id': job.id,
                'name': job.nome,
                'status': job.status,
                'progress': job.progresso_percentual,
                'frames_completed': job.frames_completados,
                'frames_total': job.frames_total,
                'estimated_time_remaining': await self._calculate_remaining_time(job),
                'current_fps': job.frames_por_segundo,
                'gpu_utilization': job.performance_metrics.get('gpu_utilization', 0),
                'memory_usage': job.performance_metrics.get('memory_usage', 0),
                'cost_accrued': float(job.custo_real or 0),
                'error_message': job.error_log,
                'logs': [
                    {
                        'timestamp': log.timestamp.isoformat(),
                        'type': log.tipo_log,
                        'message': log.message,
                        'frame': log.frame_atual,
                        'details': log.detalhos
                    }
                    for log in logs
                ]
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter status do job: {e}")
            raise
    
    async def cancel_render_job(
        self,
        db: Session,
        job_id: UUID,
        user_id: UUID
    ) -> bool:
        """Cancelar job de renderização"""
        try:
            job = db.query(RenderJob).filter(
                and_(
                    RenderJob.id == job_id,
                    RenderJob.user_id == user_id
                )
            ).first()
            
            if not job:
                raise ValueError("Job não encontrado")
            
            if job.status in ['completed', 'failed', 'cancelled']:
                raise ValueError("Job já foi finalizado")
            
            # Atualizar status
            job.status = 'cancelled'
            job.cancelled_at = datetime.utcnow()
            
            # Calcular custo parcial se estava executando
            if job.started_at:
                elapsed_time = (datetime.utcnow() - job.started_at).total_seconds()
                job.custo_real = (job.custo_estimado or 0) * (elapsed_time / job.tempo_estimado_segundos)
            
            db.commit()
            
            # Liberar recursos do cluster
            await self._release_cluster_resources(db, job.gpu_cluster_id)
            
            logger.info(f"Job de renderização cancelado: {job_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao cancelar job: {e}")
            raise
    
    # =============================================================================
    # CONFIGURAÇÕES DE RENDERIZAÇÃO
    # =============================================================================
    
    async def create_render_settings(
        self,
        db: Session,
        user_id: UUID,
        settings_data: Dict[str, Any]
    ) -> RenderSettings:
        """Criar configurações de renderização"""
        try:
            # Verificar se nome já existe para o usuário
            existing = db.query(RenderSettings).filter(
                and_(
                    RenderSettings.user_id == user_id,
                    RenderSettings.nome == settings_data['nome']
                )
            ).first()
            
            if existing:
                raise ValueError("Configuração com este nome já existe")
            
            # Criar configurações
            render_settings = RenderSettings(
                user_id=user_id,
                nome=settings_data['nome'],
                descricao=settings_data.get('descricao'),
                tipo_configuracao=settings_data.get('tipo_configuracao', 'personal'),
                configuracoes=settings_data.get('configuracoes', {}),
                preset_quality=settings_data.get('preset_quality', 'standard'),
                gpu_requirements=settings_data.get('gpu_requirements', {}),
                fallback_options=settings_data.get('fallback_options', []),
                ativo=settings_data.get('ativo', True),
                favoritos=settings_data.get('favoritos', False)
            )
            
            db.add(render_settings)
            db.commit()
            db.refresh(render_settings)
            
            logger.info(f"Configurações de renderização criadas: {render_settings.id}")
            return render_settings
            
        except Exception as e:
            logger.error(f"Erro ao criar configurações: {e}")
            raise
    
    async def list_render_settings(
        self,
        db: Session,
        user_id: UUID,
        include_templates: bool = False
    ) -> List[RenderSettings]:
        """Listar configurações de renderização do usuário"""
        try:
            query = db.query(RenderSettings).filter(
                and_(
                    RenderSettings.user_id == user_id,
                    RenderSettings.ativo == True
                )
            )
            
            if not include_templates:
                query = query.filter(RenderSettings.tipo_configuracao != 'template')
            
            settings_list = query.order_by(desc(RenderSettings.updated_at)).all()
            return settings_list
            
        except Exception as e:
            logger.error(f"Erro ao listar configurações: {e}")
            raise
    
    # =============================================================================
    # PRESETS DE QUALIDADE
    # =============================================================================
    
    async def create_quality_preset(
        self,
        db: Session,
        preset_data: Dict[str, Any]
    ) -> QualityPreset:
        """Criar preset de qualidade"""
        try:
            # Verificar se nome já existe
            existing = db.query(QualityPreset).filter(
                QualityPreset.nome == preset_data['nome']
            ).first()
            
            if existing:
                raise ValueError("Preset com este nome já existe")
            
            # Validar configurações
            if preset_data['samples_per_pixel'] < 1:
                raise ValueError("Samples per pixel deve ser maior que 0")
            
            if preset_data['qualidade_relativa'] < 0 or preset_data['qualidade_relativa'] > 100:
                raise ValueError("Qualidade relativa deve estar entre 0 e 100")
            
            if preset_data['tempo_relativo'] < 0:
                raise ValueError("Tempo relativo deve ser positivo")
            
            # Criar preset
            quality_preset = QualityPreset(
                nome=preset_data['nome'],
                descricao=preset_data.get('descricao'),
                categoria=preset_data.get('categoria'),
                samples_per_pixel=preset_data['samples_per_pixel'],
                max_bounces=preset_data.get('max_bounces', 12),
                transparent_max_bounces=preset_data.get('transparent_max_bounces', 8),
                use_denoising=preset_data.get('use_denoising', True),
                denoise_method=preset_data.get('denoise_method', 'optix'),
                use_caustics=preset_data.get('use_caustics', False),
                tile_size=preset_data.get('tile_size', 256),
                threads_per_device=preset_data.get('threads_per_device', 1),
                use_progressive=preset_data.get('use_progressive', True),
                use_motion_blur=preset_data.get('use_motion_blur', False),
                use_depth_of_field=preset_data.get('use_depth_of_field', False),
                film_transparency=preset_data.get('film_transparency', False),
                experimental_features=preset_data.get('experimental_features', False),
                high_precision=preset_data.get('high_precision', False),
                tempo_relativo=preset_data['tempo_relativo'],
                qualidade_relativa=preset_data['qualidade_relativa'],
                ativo=preset_data.get('ativo', True),
                uso_padrao=preset_data.get('uso_padrao', False)
            )
            
            db.add(quality_preset)
            db.commit()
            db.refresh(quality_preset)
            
            logger.info(f"Preset de qualidade criado: {quality_preset.id}")
            return quality_preset
            
        except Exception as e:
            logger.error(f"Erro ao criar preset de qualidade: {e}")
            raise
    
    async def list_quality_presets(
        self,
        db: Session,
        category: Optional[str] = None
    ) -> List[QualityPreset]:
        """Listar presets de qualidade"""
        try:
            query = db.query(QualityPreset).filter(QualityPreset.ativo == True)
            
            if category:
                query = query.filter(QualityPreset.categoria == category)
            
            presets = query.order_by(QualityPreset.qualidade_relativa).all()
            return presets
            
        except Exception as e:
            logger.error(f"Erro ao listar presets: {e}")
            raise
    
    # =============================================================================
    # RENDERIZAÇÃO EM LOTE
    # =============================================================================
    
    async def create_batch_render(
        self,
        db: Session,
        user_id: UUID,
        batch_data: Dict[str, Any]
    ) -> BatchRenderConfig:
        """Criar configuração de renderização em lote"""
        try:
            # Verificar lista de jobs
            job_ids = batch_data.get('job_ids', [])
            if not job_ids:
                raise ValueError("Lista de jobs é obrigatória")
            
            # Verificar se todos os jobs existem e pertencem ao usuário
            jobs = db.query(RenderJob).filter(
                and_(
                    RenderJob.id.in_(job_ids),
                    RenderJob.user_id == user_id
                )
            ).all()
            
            if len(jobs) != len(job_ids):
                raise ValueError("Alguns jobs não foram encontrados")
            
            # Verificar se jobs estão em status adequado
            invalid_jobs = [job for job in jobs if job.status not in ['queued', 'failed']]
            if invalid_jobs:
                raise ValueError("Alguns jobs não podem ser processados em lote")
            
            # Criar configuração de lote
            batch_config = BatchRenderConfig(
                user_id=user_id,
                nome=batch_data['nome'],
                descricao=batch_data.get('descricao'),
                qualidade_padrao=batch_data.get('qualidade_padrao', 'standard'),
                engine_padrao=batch_data.get('engine_padrao', 'cycles'),
                parallell_jobs=batch_data.get('parallell_jobs', 1),
                priority=batch_data.get('priority', 'normal'),
                status='queued',
                total_jobs=len(job_ids),
                created_at=datetime.utcnow()
            )
            
            db.add(batch_config)
            db.commit()
            db.refresh(batch_config)
            
            # Associar jobs ao lote
            for job in jobs:
                job.batch_config_id = batch_config.id
                job.status = 'queued'  # Reset status
            
            db.commit()
            
            # Iniciar processamento do lote
            await self._process_batch_render(db, batch_config)
            
            logger.info(f"Renderização em lote criada: {batch_config.id}")
            return batch_config
            
        except Exception as e:
            logger.error(f"Erro ao criar lote de renderização: {e}")
            raise
    
    async def get_batch_status(
        self,
        db: Session,
        batch_id: UUID,
        user_id: UUID
    ) -> Dict[str, Any]:
        """Obter status de renderização em lote"""
        try:
            batch = db.query(BatchRenderConfig).filter(
                and_(
                    BatchRenderConfig.id == batch_id,
                    BatchRenderConfig.user_id == user_id
                )
            ).first()
            
            if not batch:
                raise ValueError("Lote não encontrado")
            
            # Calcular progresso
            completed_jobs = db.query(RenderJob).filter(
                and_(
                    RenderJob.batch_config_id == batch_id,
                    RenderJob.status == 'completed'
                )
            ).count()
            
            failed_jobs = db.query(RenderJob).filter(
                and_(
                    RenderJob.batch_config_id == batch_id,
                    RenderJob.status == 'failed'
                )
            ).count()
            
            progress_percentage = (batch.completed_jobs / batch.total_jobs * 100) if batch.total_jobs > 0 else 0
            
            return {
                'batch_id': batch.id,
                'name': batch.nome,
                'status': batch.status,
                'total_jobs': batch.total_jobs,
                'completed_jobs': completed_jobs,
                'failed_jobs': failed_jobs,
                'progress_percentage': progress_percentage,
                'created_at': batch.created_at,
                'started_at': batch.started_at,
                'estimated_completion': batch.started_at + timedelta(minutes=batch.total_jobs * 10) if batch.started_at else None
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter status do lote: {e}")
            raise
    
    # =============================================================================
    # ESTIMATIVAS DE CUSTO
    # =============================================================================
    
    async def calculate_cost_estimate(
        self,
        db: Session,
        user_id: UUID,
        estimate_data: Dict[str, Any]
    ) -> CostEstimate:
        """Calcular estimativa de custo de renderização"""
        try:
            # Verificar usuário
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValueError("Usuário não encontrado")
            
            # Verificar projeto se fornecido
            project = None
            if estimate_data.get('project_id'):
                project = db.query(Project).filter(
                    and_(
                        Project.id == estimate_data['project_id'],
                        Project.owner_id == user_id
                    )
                ).first()
                
                if not project:
                    raise ValueError("Projeto não encontrado")
            
            # Configurar job estimado
            job_config = estimate_data['job_config']
            
            # Calcular recursos necessários
            gpu_requirements = await self._calculate_gpu_requirements(job_config)
            
            # Encontrar cluster apropriado
            suitable_cluster = await self._find_suitable_cluster(db, gpu_requirements)
            
            if not suitable_cluster:
                raise ValueError("Nenhum cluster disponível atende aos requisitos")
            
            # Calcular custo
            cost_breakdown = await self._calculate_cost_breakdown(job_config, suitable_cluster)
            
            # Verificar alternativas
            alternative_clusters = await self._get_alternative_clusters(db, gpu_requirements, suitable_cluster.id)
            
            # Gerar estimativas alternativas
            alternatives = []
            for alt_cluster in alternative_clusters[:3]:  # Top 3 alternativas
                alt_cost = await self._calculate_cost_breakdown(job_config, alt_cluster)
                alternatives.append({
                    'cluster_id': str(alt_cluster.id),
                    'cluster_name': alt_cluster.nome,
                    'provider': alt_cluster.provider,
                    'region': alt_cluster.region,
                    'cost_per_hour': float(alt_cluster.custo_para_hora),
                    'estimated_total_cost': float(alt_cost['total_cost']),
                    'estimated_time_hours': alt_cost['estimated_time_hours'],
                    'performance_score': alt_cluster.throughput_score or 0
                })
            
            # Criar estimativa
            estimate = CostEstimate(
                user_id=user_id,
                project_id=estimate_data.get('project_id'),
                job_config=job_config,
                tempo_estimado_horas=cost_breakdown['estimated_time_hours'],
                gpu_cluster_sugerido_id=suitable_cluster.id,
                custo_computacao=cost_breakdown['compute_cost'],
                custo_armazenamento=cost_breakdown['storage_cost'],
                custo_tranferencia=cost_breakdown['transfer_cost'],
                custo_total=cost_breakdown['total_cost'],
                desconto_percentual=estimate_data.get('discount_percentage', 0),
                valor_desconto=cost_breakdown['discount_amount'],
                custo_final=cost_breakdown['final_cost'],
                moeda='USD',
                valor_em_reais=cost_breakdown['final_cost'] * 5.0,  # Taxa de câmbio aproximada
                taxa_cambio_usd_brl=5.0,
                alternativas_cluster=alternatives,
                estimativa_valida_por_horas=estimate_data.get('valid_hours', 24),
                precisao_estimada=estimate_data.get('accuracy_percentage', 85),
                expira_em=datetime.utcnow() + timedelta(hours=estimate_data.get('valid_hours', 24))
            )
            
            db.add(estimate)
            db.commit()
            db.refresh(estimate)
            
            logger.info(f"Estimativa de custo criada: {estimate.id}")
            return estimate
            
        except Exception as e:
            logger.error(f"Erro ao calcular estimativa de custo: {e}")
            raise
    
    # =============================================================================
    # MÉTODOS PRIVADOS DE ASSISTÊNCIA
    # =============================================================================
    
    async def _calculate_cluster_cost(self, cluster_data: Dict[str, Any]) -> Decimal:
        """Calcular custo por hora do cluster"""
        total_cost = Decimal('0.00')
        
        # Custo das GPUs
        if cluster_data.get('gpu_count', 0) > 0:
            gpu_model = cluster_data.get('gpu_model', 'RTX_3080')
            gpu_cost = self.gpu_costs_per_hour.get(gpu_model, 1.0)
            total_cost += Decimal(str(gpu_cost)) * cluster_data['gpu_count']
        
        # Custo da CPU
        cpu_cost = self.gpu_costs_per_hour.get('CPU_16_core', 0.5)
        total_cost += Decimal(str(cpu_cost)) * (cluster_data['cpu_cores'] / 16)
        
        # Custo de armazenamento
        storage_gb = cluster_data.get('storage_gb', 100)
        storage_cost = Decimal(str(storage_gb * 0.001))  # $0.001 per GB
        total_cost += storage_cost
        
        return total_cost
    
    async def _calculate_job_metrics(
        self,
        model_3d: Model3D,
        job_data: Dict[str, Any],
        cluster: GPUCluster
    ) -> Dict[str, Any]:
        """Calcular métricas estimadas do job"""
        try:
            # Estimar complexidade baseado no modelo
            complexity_factor = 1.0
            if model_3d.numero_vertices:
                if model_3d.numero_vertices > 1000000:
                    complexity_factor = 3.0
                elif model_3d.numero_vertices > 100000:
                    complexity_factor = 2.0
                elif model_3d.numero_vertices > 10000:
                    complexity_factor = 1.5
            
            # Base de tempo (em segundos) por configuração
            base_time = 3600  # 1 hora base
            
            # Ajustes baseados em qualidade
            quality_preset = job_data.get('qualidade', 'standard')
            quality_multiplier = self.quality_presets.get(quality_preset, {}).get('time_multiplier', 1.0)
            
            # Ajustes baseados em resolução
            resolution_area = job_data['resolution_x'] * job_data['resolution_y']
            resolution_multiplier = max(1.0, resolution_area / (1920 * 1080))
            
            # Ajustes baseados em samples
            samples = job_data.get('samples', 128)
            samples_multiplier = samples / 128  # Relativo a 128 samples
            
            # Ajustes baseados no cluster
            cluster_multiplier = 1.0
            if cluster.gpu_count and cluster.gpu_count > 0:
                # Clusters GPU são mais rápidos
                cluster_multiplier = max(0.1, 1.0 / cluster.gpu_count)
            
            # Calcular tempo estimado
            estimated_time = int(
                base_time * 
                complexity_factor * 
                quality_multiplier * 
                resolution_multiplier * 
                samples_multiplier * 
                cluster_multiplier
            )
            
            # Calcular custo estimado
            cost_per_second = float(cluster.custo_para_hora) / 3600
            estimated_cost = Decimal(str(cost_per_second * estimated_time))
            
            # Calcular consumo de energia (estimativa)
            energy_consumption = estimated_time * 0.3  # 300W médio por hora
            
            # Calcular pegada de carbono (estimativa)
            carbon_footprint = energy_consumption * 0.4  # kg CO2
            
            return {
                'estimated_time': estimated_time,
                'estimated_cost': estimated_cost,
                'energy_consumption': energy_consumption,
                'carbon_footprint': carbon_footprint,
                'complexity_factor': complexity_factor
            }
            
        except Exception as e:
            logger.error(f"Erro ao calcular métricas do job: {e}")
            return {
                'estimated_time': 3600,
                'estimated_cost': Decimal('2.50'),
                'energy_consumption': 0.3,
                'carbon_footprint': 0.12,
                'complexity_factor': 1.0
            }
    
    async def _schedule_job(self, db: Session, job: RenderJob):
        """Agendar job para processamento"""
        try:
            # Marcar job como pronto para processamento
            job.status = 'queued'
            job.queued_at = datetime.utcnow()
            
            # Buscar cluster disponível
            cluster = db.query(GPUCluster).filter(
                and_(
                    GPUCluster.id == job.gpu_cluster_id,
                    GPUCluster.status == 'available'
                )
            ).first()
            
            if cluster:
                # Atualizar status do cluster
                cluster.status = 'busy'
                job.status = 'preparing'
            
            db.commit()
            
        except Exception as e:
            logger.error(f"Erro ao agendar job: {e}")
            raise
    
    async def _calculate_remaining_time(self, job: RenderJob) -> int:
        """Calcular tempo restante estimado em segundos"""
        if job.status == 'completed':
            return 0
        
        if job.tempo_estimado_segundos and job.frames_total and job.frames_completados:
            progress = job.frames_completados / job.frames_total
            if progress > 0:
                remaining_time = job.tempo_estimado_segundos * (1 - progress)
                return int(remaining_time)
        
        return job.tempo_estimado_segundos or 3600  # 1 hora padrão
    
    async def _release_cluster_resources(self, db: Session, cluster_id: UUID):
        """Liberar recursos do cluster"""
        try:
            cluster = db.query(GPUCluster).filter(GPUCluster.id == cluster_id).first()
            if cluster:
                cluster.status = 'available'
                cluster.last_health_check = datetime.utcnow()
                db.commit()
        except Exception as e:
            logger.error(f"Erro ao liberar recursos do cluster: {e}")
    
    async def _process_batch_render(self, db: Session, batch_config: BatchRenderConfig):
        """Processar renderização em lote"""
        try:
            batch_config.status = 'processing'
            batch_config.started_at = datetime.utcnow()
            
            # Buscar jobs do lote
            batch_jobs = db.query(RenderJob).filter(
                RenderJob.batch_config_id == batch_config.id
            ).all()
            
            # Iniciar processamento dos jobs
            for job in batch_jobs:
                job.status = 'queued'
            
            db.commit()
            
            logger.info(f"Lote de renderização iniciado: {batch_config.id}")
            
        except Exception as e:
            logger.error(f"Erro ao processar lote: {e}")
            raise
    
    async def _calculate_gpu_requirements(self, job_config: Dict[str, Any]) -> Dict[str, Any]:
        """Calcular requisitos de GPU para o job"""
        resolution = job_config.get('resolution', {'width': 1920, 'height': 1080})
        quality = job_config.get('quality', 'standard')
        engine = job_config.get('render_engine', 'cycles')
        
        # Calcular requisitos baseados na resolução
        area = resolution['width'] * resolution['height']
        
        # Requisitos base (em GB)
        base_memory = max(2.0, area / (1920 * 1080) * 4.0)
        
        # Multiplicador de qualidade
        quality_multipliers = {
            'draft': 0.5,
            'standard': 1.0,
            'high': 2.0,
            'ultra': 4.0,
            'cinema': 8.0
        }
        
        memory_required = base_memory * quality_multipliers.get(quality, 1.0)
        
        # CPU cores necessários
        cpu_cores = max(4, int(area / (1920 * 1080) * 8))
        
        return {
            'gpu_memory_gb': memory_required,
            'cpu_cores': cpu_cores,
            'storage_gb': 10.0,  # Espaço para arquivos temporários
            'priority': job_config.get('priority', 'normal')
        }
    
    async def _find_suitable_cluster(
        self,
        db: Session,
        requirements: Dict[str, Any]
    ) -> Optional[GPUCluster]:
        """Encontrar cluster adequado para os requisitos"""
        clusters = db.query(GPUCluster).filter(
            and_(
                GPUCluster.status == 'available',
                GPUCluster.cpu_memory_gb >= requirements['cpu_cores'],
                GPUCluster.storage_gb >= requirements['storage_gb']
            )
        ).all()
        
        # Filtrar clusters GPU se necessário
        suitable_clusters = []
        if requirements['gpu_memory_gb'] > 0:
            for cluster in clusters:
                if (cluster.gpu_count and cluster.gpu_count > 0 and 
                    cluster.gpu_memory_gb and cluster.gpu_memory_gb >= requirements['gpu_memory_gb']):
                    suitable_clusters.append(cluster)
        else:
            suitable_clusters = clusters
        
        # Ordenar por throughput score
        suitable_clusters.sort(key=lambda c: c.throughput_score or 0, reverse=True)
        
        return suitable_clusters[0] if suitable_clusters else None
    
    async def _get_alternative_clusters(
        self,
        db: Session,
        requirements: Dict[str, Any],
        exclude_id: UUID
    ) -> List[GPUCluster]:
        """Obter clusters alternativos"""
        clusters = db.query(GPUCluster).filter(
            and_(
                GPUCluster.id != exclude_id,
                GPUCluster.status == 'available'
            )
        ).order_by(desc(GPUCluster.throughput_score)).limit(10).all()
        
        return clusters
    
    async def _calculate_cost_breakdown(
        self,
        job_config: Dict[str, Any],
        cluster: GPUCluster
    ) -> Dict[str, Any]:
        """Calcular breakdown detalhado de custos"""
        # Tempo estimado baseado na complexidade
        base_time_hours = job_config.get('estimated_hours', 2.0)
        complexity_factor = job_config.get('complexity_factor', 1.0)
        estimated_time_hours = base_time_hours * complexity_factor
        
        # Custo de computação
        compute_cost = float(cluster.custo_para_hora) * estimated_time_hours
        
        # Custo de armazenamento (arquivos de saída)
        storage_gb = job_config.get('output_size_gb', 1.0)
        storage_cost = storage_gb * 0.023  # $0.023 per GB-month (prorated)
        
        # Custo de transferência
        transfer_gb = job_config.get('transfer_gb', 0.1)
        transfer_cost = transfer_gb * 0.09  # $0.09 per GB
        
        total_cost = compute_cost + storage_cost + transfer_cost
        
        # Aplicar desconto se houver
        discount_percentage = job_config.get('discount_percentage', 0)
        discount_amount = total_cost * (discount_percentage / 100)
        final_cost = total_cost - discount_amount
        
        return {
            'estimated_time_hours': estimated_time_hours,
            'compute_cost': compute_cost,
            'storage_cost': storage_cost,
            'transfer_cost': transfer_cost,
            'total_cost': total_cost,
            'discount_amount': discount_amount,
            'final_cost': final_cost
        }
    
    # =============================================================================
    # ESTATÍSTICAS E RELATÓRIOS
    # =============================================================================
    
    async def get_rendering_statistics(
        self,
        db: Session,
        user_id: Optional[UUID] = None,
        time_period: str = '30d'
    ) -> Dict[str, Any]:
        """Obter estatísticas de renderização"""
        try:
            base_query = db.query(RenderJob)
            
            if user_id:
                base_query = base_query.filter(RenderJob.user_id == user_id)
            
            # Filtro de período
            time_delta = {
                '7d': timedelta(days=7),
                '30d': timedelta(days=30),
                '90d': timedelta(days=90),
                '1y': timedelta(days=365)
            }.get(time_period, timedelta(days=30))
            
            cutoff_date = datetime.utcnow() - time_delta
            base_query = base_query.filter(RenderJob.created_at >= cutoff_date)
            
            # Estatísticas básicas
            total_jobs = base_query.count()
            completed_jobs = base_query.filter(RenderJob.status == 'completed').count()
            failed_jobs = base_query.filter(RenderJob.status == 'failed').count()
            active_jobs = base_query.filter(
                RenderJob.status.in_(['queued', 'preparing', 'rendering', 'post_processing'])
            ).count()
            
            # Custos
            total_cost = base_query.with_entities(
                func.sum(RenderJob.custo_real)
            ).filter(RenderJob.custo_real.isnot(None)).scalar() or 0
            
            # Tempo de processamento
            total_processing_time = base_query.with_entities(
                func.sum(RenderJob.tempo_real_segundos)
            ).filter(RenderJob.tempo_real_segundos.isnot(None)).scalar() or 0
            
            # Engines mais usados
            engine_stats = base_query.query(
                RenderJob.render_engine,
                func.count(RenderJob.id).label('count')
            ).group_by(RenderJob.render_engine).all()
            
            # Clusters mais utilizados
            cluster_stats = base_query.query(
                GPUCluster.nome,
                func.count(RenderJob.id).label('count')
            ).join(GPUCluster).group_by(GPUCluster.nome).all()
            
            return {
                'period': time_period,
                'total_jobs': total_jobs,
                'completed_jobs': completed_jobs,
                'failed_jobs': failed_jobs,
                'active_jobs': active_jobs,
                'success_rate': (completed_jobs / total_jobs * 100) if total_jobs > 0 else 0,
                'total_cost': float(total_cost),
                'total_processing_time_hours': total_processing_time / 3600,
                'average_job_cost': float(total_cost / completed_jobs) if completed_jobs > 0 else 0,
                'engines_used': [{'engine': stat[0], 'count': stat[1]} for stat in engine_stats],
                'clusters_used': [{'cluster': stat[0], 'count': stat[1]} for stat in cluster_stats]
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {e}")
            raise