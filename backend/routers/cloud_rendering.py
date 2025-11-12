"""
Routers FastAPI - Cloud Rendering (Sprint 6+)
=============================================

Rotas para renderização em nuvem e processamento GPU distribuído, incluindo:
- Clusters de GPU (GPUCluster)
- Jobs de renderização (RenderJob)
- Configurações de renderização (RenderSettings)
- Templates de qualidade (QualityPreset)
- Renderização em lote (BatchRenderConfig)
- Estimativas de custo (CostEstimate)

Autor: MiniMax Agent
Data: 2025-11-13
Versão: 2.0.0 - Sprint 6+
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from uuid import UUID
import json
import logging

from ..database import get_db
from ..core.config import settings
from ..services.cloud_rendering_service import CloudRenderingService
from ..middleware.auth import get_current_user
from ..models import User

router = APIRouter()

# Instância do serviço
cloud_rendering_service = CloudRenderingService()

# =============================================================================
# ROTAS DE CLUSTERS DE GPU
# =============================================================================

@router.post("/gpu-clusters/", response_model=dict)
async def create_gpu_cluster(
    cluster_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Criar novo cluster de GPU (apenas administradores)"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    try:
        cluster = await cloud_rendering_service.create_gpu_cluster(db, cluster_data)
        return {
            "success": True,
            "message": "Cluster GPU criado com sucesso",
            "data": {
                "id": str(cluster.id),
                "nome": cluster.nome,
                "provider": cluster.provider,
                "region": cluster.region,
                "tipo_cluster": cluster.tipo_cluster,
                "gpu_model": cluster.gpu_model,
                "gpu_count": cluster.gpu_count,
                "cpu_cores": cluster.cpu_cores,
                "custo_por_hora": float(cluster.custo_para_hora),
                "status": cluster.status
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/gpu-clusters/", response_model=dict)
async def list_gpu_clusters(
    status_filter: Optional[str] = Query(None, description="Filtrar por status (separado por vírgula)"),
    provider: Optional[str] = Query(None, description="Filtrar por provider"),
    region: Optional[str] = Query(None, description="Filtrar por região"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Listar clusters de GPU disponíveis"""
    try:
        # Processar filtros de status
        status_list = None
        if status_filter:
            status_list = [s.strip() for s in status_filter.split(',')]
        
        clusters = await cloud_rendering_service.list_gpu_clusters(db, status_list, provider, region)
        
        return {
            "success": True,
            "data": {
                "clusters": [
                    {
                        "id": str(c.id),
                        "nome": c.nome,
                        "provider": c.provider,
                        "region": c.region,
                        "zona": c.zona,
                        "tipo_cluster": c.tipo_cluster,
                        "gpu_model": c.gpu_model,
                        "gpu_count": c.gpu_count,
                        "gpu_memory_gb": c.gpu_memory_gb,
                        "cpu_cores": c.cpu_cores,
                        "cpu_memory_gb": c.cpu_memory_gb,
                        "storage_gb": c.storage_gb,
                        "storage_type": c.storage_type,
                        "status": c.status,
                        "custo_por_hora": float(c.custo_para_hora),
                        "throughput_score": c.throughput_score,
                        "auto_scaling": c.auto_scaling,
                        "created_at": c.created_at.isoformat(),
                        "last_health_check": c.last_health_check.isoformat() if c.last_health_check else None
                    }
                    for c in clusters
                ],
                "total": len(clusters)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/gpu-clusters/{cluster_id}/status", response_model=dict)
async def get_cluster_status(
    cluster_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter status detalhado do cluster"""
    try:
        status_info = await cloud_rendering_service.get_cluster_status(db, cluster_id)
        return {
            "success": True,
            "data": status_info
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# =============================================================================
# ROTAS DE JOBS DE RENDERIZAÇÃO
# =============================================================================

@router.post("/render-jobs/", response_model=dict)
async def create_render_job(
    job_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Criar novo job de renderização"""
    try:
        job = await cloud_rendering_service.create_render_job(db, current_user.id, job_data)
        return {
            "success": True,
            "message": "Job de renderização criado com sucesso",
            "data": {
                "job_id": str(job.id),
                "nome": job.nome,
                "status": job.status,
                "qualidade": job.qualidade,
                "render_engine": job.render_engine,
                "device": job.device,
                "resolution": {
                    "x": job.resolution_x,
                    "y": job.resolution_y
                },
                "tempo_estimado_segundos": job.tempo_estimado_segundos,
                "custo_estimado": float(job.custo_estimado or 0),
                "gpu_cluster": {
                    "id": str(job.gpu_cluster.id),
                    "nome": job.gpu_cluster.nome
                } if job.gpu_cluster else None
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/render-jobs/", response_model=dict)
async def list_render_jobs(
    status_filter: Optional[str] = Query(None, description="Filtrar por status (separado por vírgula)"),
    cluster_id: Optional[UUID] = Query(None, description="Filtrar por cluster"),
    limit: int = Query(50, description="Limite de resultados"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Listar jobs de renderização do usuário"""
    try:
        # Processar filtros de status
        status_list = None
        if status_filter:
            status_list = [s.strip() for s in status_filter.split(',')]
        
        jobs = await cloud_rendering_service.list_render_jobs(db, current_user.id, status_list, cluster_id, limit)
        
        return {
            "success": True,
            "data": {
                "jobs": [
                    {
                        "id": str(j.id),
                        "nome": j.nome,
                        "status": j.status,
                        "progresso": j.progresso_percentual,
                        "frames_completados": j.frames_completados,
                        "frames_total": j.frames_total,
                        "tempo_estimado_segundos": j.tempo_estimado_segundos,
                        "tempo_real_segundos": j.tempo_real_segundos,
                        "custo_estimado": float(j.custo_estimado or 0),
                        "custo_real": float(j.custo_real or 0),
                        "qualidade": j.qualidade,
                        "render_engine": j.render_engine,
                        "device": j.device,
                        "resolution": {
                            "x": j.resolution_x,
                            "y": j.resolution_y
                        },
                        "framerate": j.framerate,
                        "gpu_cluster": {
                            "id": str(j.gpu_cluster.id),
                            "nome": j.gpu_cluster.nome,
                            "provider": j.gpu_cluster.provider
                        } if j.gpu_cluster else None,
                        "project": {
                            "id": str(j.project.id),
                            "nome": j.project.nome
                        } if j.project else None,
                        "timestamps": {
                            "created_at": j.created_at.isoformat(),
                            "queued_at": j.queued_at.isoformat() if j.queued_at else None,
                            "started_at": j.started_at.isoformat() if j.started_at else None,
                            "completed_at": j.completed_at.isoformat() if j.completed_at else None,
                            "failed_at": j.failed_at.isoformat() if j.failed_at else None
                        }
                    }
                    for j in jobs
                ],
                "total": len(jobs)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/render-jobs/{job_id}", response_model=dict)
async def get_render_job(
    job_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter detalhes do job de renderização"""
    try:
        status_info = await cloud_rendering_service.get_job_status(db, job_id, current_user.id)
        return {
            "success": True,
            "data": status_info
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/render-jobs/{job_id}/cancel", response_model=dict)
async def cancel_render_job(
    job_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancelar job de renderização"""
    try:
        success = await cloud_rendering_service.cancel_render_job(db, job_id, current_user.id)
        return {
            "success": success,
            "message": "Job de renderização cancelado com sucesso"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/render-jobs/{job_id}/download-output", response_model=FileResponse)
async def download_render_output(
    job_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download do resultado da renderização"""
    try:
        jobs = await cloud_rendering_service.list_render_jobs(db, current_user.id, limit=1)
        job = next((j for j in jobs if j.id == job_id), None)
        
        if not job:
            raise HTTPException(status_code=404, detail="Job não encontrado")
        
        if job.status != 'completed':
            raise HTTPException(status_code=400, detail="Job ainda não foi concluído")
        
        if not job.arquivo_output_path:
            raise HTTPException(status_code=404, detail="Arquivo de saída não encontrado")
        
        from pathlib import Path
        output_file = Path(job.arquivo_output_path)
        if not output_file.exists():
            raise HTTPException(status_code=404, detail="Arquivo não existe")
        
        return FileResponse(
            path=str(output_file),
            filename=f"{job.nome}.{job.arquivo_output_format or 'mp4'}",
            media_type="application/octet-stream"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# =============================================================================
# ROTAS DE CONFIGURAÇÕES DE RENDERIZAÇÃO
# =============================================================================

@router.post("/render-settings/", response_model=dict)
async def create_render_settings(
    settings_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Criar configurações de renderização"""
    try:
        settings_obj = await cloud_rendering_service.create_render_settings(db, current_user.id, settings_data)
        return {
            "success": True,
            "message": "Configurações de renderização criadas",
            "data": {
                "settings_id": str(settings_obj.id),
                "nome": settings_obj.nome,
                "tipo_configuracao": settings_obj.tipo_configuracao,
                "preset_quality": settings_obj.preset_quality,
                "vezes_usado": settings_obj.vezes_usado
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/render-settings/", response_model=dict)
async def list_render_settings(
    include_templates: bool = Query(False, description="Incluir templates públicos"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Listar configurações de renderização do usuário"""
    try:
        settings_list = await cloud_rendering_service.list_render_settings(db, current_user.id, include_templates)
        return {
            "success": True,
            "data": {
                "settings": [
                    {
                        "id": str(s.id),
                        "nome": s.nome,
                        "descricao": s.descricao,
                        "tipo_configuracao": s.tipo_configuracao,
                        "preset_quality": s.preset_quality,
                        "vezes_usado": s.vezes_usado,
                        "tempo_total_renderizado": s.tempo_total_renderizado,
                        "favoritos": s.favoritos,
                        "ativo": s.ativo,
                        "configuracoes": s.configuracoes,
                        "gpu_requirements": s.gpu_requirements,
                        "created_at": s.created_at.isoformat(),
                        "updated_at": s.updated_at.isoformat()
                    }
                    for s in settings_list
                ],
                "total": len(settings_list)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# =============================================================================
# ROTAS DE PRESETS DE QUALIDADE
# =============================================================================

@router.post("/quality-presets/", response_model=dict)
async def create_quality_preset(
    preset_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Criar preset de qualidade (apenas administradores)"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    try:
        preset = await cloud_rendering_service.create_quality_preset(db, preset_data)
        return {
            "success": True,
            "message": "Preset de qualidade criado com sucesso",
            "data": {
                "preset_id": str(preset.id),
                "nome": preset.nome,
                "categoria": preset.categoria,
                "samples_per_pixel": preset.samples_per_pixel,
                "qualidade_relativa": preset.qualidade_relativa,
                "tempo_relativo": preset.tempo_relativo
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/quality-presets/", response_model=dict)
async def list_quality_presets(
    category: Optional[str] = Query(None, description="Filtrar por categoria"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Listar presets de qualidade"""
    try:
        presets = await cloud_rendering_service.list_quality_presets(db, category)
        return {
            "success": True,
            "data": {
                "presets": [
                    {
                        "id": str(p.id),
                        "nome": p.nome,
                        "descricao": p.descricao,
                        "categoria": p.categoria,
                        "samples_per_pixel": p.samples_per_pixel,
                        "max_bounces": p.max_bounces,
                        "use_denoising": p.use_denoising,
                        "denoise_method": p.denoise_method,
                        "qualidade_relativa": p.qualidade_relativa,
                        "tempo_relativo": p.tempo_relativo,
                        "ativo": p.ativo,
                        "uso_padrao": p.uso_padrao
                    }
                    for p in presets
                ],
                "total": len(presets)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# =============================================================================
# ROTAS DE RENDERIZAÇÃO EM LOTE
# =============================================================================

@router.post("/batch-renders/", response_model=dict)
async def create_batch_render(
    batch_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Criar configuração de renderização em lote"""
    try:
        batch_config = await cloud_rendering_service.create_batch_render(db, current_user.id, batch_data)
        return {
            "success": True,
            "message": "Renderização em lote criada com sucesso",
            "data": {
                "batch_id": str(batch_config.id),
                "nome": batch_config.nome,
                "status": batch_config.status,
                "total_jobs": batch_config.total_jobs,
                "progresso_geral": batch_config.progresso_geral,
                "priority": batch_config.priority
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/batch-renders/{batch_id}", response_model=dict)
async def get_batch_status(
    batch_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter status de renderização em lote"""
    try:
        status_info = await cloud_rendering_service.get_batch_status(db, batch_id, current_user.id)
        return {
            "success": True,
            "data": status_info
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# =============================================================================
# ROTAS DE ESTIMATIVAS DE CUSTO
# =============================================================================

@router.post("/cost-estimates/", response_model=dict)
async def calculate_cost_estimate(
    estimate_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Calcular estimativa de custo de renderização"""
    try:
        estimate = await cloud_rendering_service.calculate_cost_estimate(db, current_user.id, estimate_data)
        return {
            "success": True,
            "message": "Estimativa de custo calculada",
            "data": {
                "estimate_id": str(estimate.id),
                "tempo_estimado_horas": estimate.tempo_estimado_horas,
                "custo_computacao": float(estimate.custo_computacao),
                "custo_armazenamento": float(estimate.custo_armazenamento),
                "custo_tranferencia": float(estimate.custo_tranferencia),
                "custo_total": float(estimate.custo_total),
                "desconto_percentual": estimate.desconto_percentual,
                "valor_desconto": float(estimate.valor_desconto),
                "custo_final": float(estimate.custo_final),
                "moeda": estimate.moeda,
                "valor_em_reais": float(estimate.valor_em_reais),
                "alternativas_cluster": estimate.alternativas_cluster,
                "precisao_estimada": estimate.precisao_estimada,
                "expira_em": estimate.expira_em.isoformat(),
                "gpu_cluster_sugerido": {
                    "id": str(estimate.gpu_cluster.id),
                    "nome": estimate.gpu_cluster.nome,
                    "provider": estimate.gpu_cluster.provider
                } if estimate.gpu_cluster else None
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# =============================================================================
# ROTAS DE ESTATÍSTICAS
# =============================================================================

@router.get("/statistics/", response_model=dict)
async def get_rendering_statistics(
    time_period: str = Query("30d", description="Período de tempo (7d, 30d, 90d, 1y)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter estatísticas de renderização"""
    try:
        stats = await cloud_rendering_service.get_rendering_statistics(db, current_user.id, time_period)
        return {
            "success": True,
            "data": stats
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# =============================================================================
# ROTAS DE ENGEINS E CONFIGURAÇÕES
# =============================================================================

@router.get("/engines/", response_model=dict)
async def get_render_engines(
    current_user: User = Depends(get_current_user)
):
    """Obter lista de engines de renderização suportados"""
    try:
        engines_info = cloud_rendering_service.render_engines
        return {
            "success": True,
            "data": {
                "engines": [
                    {
                        "name": info['name'],
                        "key": key,
                        "description": info['description'],
                        "supports_gpu": info['supports_gpu'],
                        "supports_cpu": info['supports_cpu'],
                        "default_samples": info['default_samples']
                    }
                    for key, info in engines_info.items()
                ]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/quality-presets-info/", response_model=dict)
async def get_quality_presets_info(
    current_user: User = Depends(get_current_user)
):
    """Obter informações dos presets de qualidade padrão"""
    try:
        presets_info = cloud_rendering_service.quality_presets
        return {
            "success": True,
            "data": {
                "presets": {
                    key: {
                        "samples": info['samples'],
                        "max_bounces": info['max_bounces'],
                        "tile_size": info['tile_size'],
                        "time_multiplier": info['time_multiplier'],
                        "quality_score": info['quality_score']
                    }
                    for key, info in presets_info.items()
                }
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))