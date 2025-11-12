"""
Routers FastAPI - 3D Printing Suite (Sprint 6+)
=============================================

Rotas para gerenciamento de impressão 3D, incluindo:
- Gestão de impressoras (Printer)
- Controle de materiais (Material)
- Jobs de impressão (PrintJob)
- Fila de impressão (PrintQueue)

Autor: MiniMax Agent
Data: 2025-11-13
Versão: 2.0.0 - Sprint 6+
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from ..database import get_db
from ..core.config import settings
from ..services.print3d_service import Print3DService
from ..schemas import (
    PrinterCreate, PrinterUpdate, MaterialCreate, PrintJobCreate,
    PrintSettingsCreate, PrintJobUpdate, PrintJobStatus
)
from ..middleware.auth import get_current_user
from ..models import User

router = APIRouter()

# Instância do serviço
print3d_service = Print3DService()

# =============================================================================
# ROTAS DE IMPRESSORAS
# =============================================================================

@router.post("/printers/", response_model=dict)
async def create_printer(
    printer_data: PrinterCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Criar nova impressora"""
    try:
        printer = await print3d_service.create_printer(db, current_user.id, printer_data)
        return {
            "success": True,
            "message": "Impressora criada com sucesso",
            "data": {
                "id": str(printer.id),
                "nome": printer.nome,
                "marca": printer.marca,
                "modelo": printer.modelo,
                "tipo_impressora": printer.tipo_impressora,
                "status": printer.status
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/printers/", response_model=dict)
async def list_printers(
    include_inactive: bool = Query(False, description="Incluir impressoras inativas"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Listar impressoras do usuário"""
    try:
        printers = await print3d_service.list_printers(db, current_user.id, include_inactive)
        return {
            "success": True,
            "data": {
                "printers": [
                    {
                        "id": str(p.id),
                        "nome": p.nome,
                        "marca": p.marca,
                        "modelo": p.modelo,
                        "tipo_impressora": p.tipo_impressora,
                        "status": p.status,
                        "esta_conectado": p.esta_conectado,
                        "volume_impressao": {
                            "x": p.volume_impressao_x,
                            "y": p.volume_impressao_y,
                            "z": p.volume_impressao_z
                        },
                        "ultima_atividade": p.ultimo_sinal_vida.isoformat() if p.ultimo_sinal_vida else None
                    }
                    for p in printers
                ],
                "total": len(printers)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/printers/{printer_id}", response_model=dict)
async def get_printer(
    printer_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter detalhes da impressora"""
    try:
        printers = await print3d_service.list_printers(db, current_user.id)
        printer = next((p for p in printers if p.id == printer_id), None)
        
        if not printer:
            raise HTTPException(status_code=404, detail="Impressora não encontrada")
        
        return {
            "success": True,
            "data": {
                "id": str(printer.id),
                "nome": printer.nome,
                "marca": printer.marca,
                "modelo": printer.modelo,
                "tipo_impressora": printer.tipo_impressora,
                "status": printer.status,
                "esta_conectado": printer.esta_conectado,
                "volume_impressao": {
                    "x": printer.volume_impressao_x,
                    "y": printer.volume_impressao_y,
                    "z": printer.volume_impressao_z
                },
                "configuracoes_tecnicas": {
                    "temperatura_bico": {
                        "min": printer.temperatura_bico_min,
                        "max": printer.temperatura_bico_max
                    },
                    "temperatura_mesa": {
                        "min": printer.temperatura_mesa_min,
                        "max": printer.temperatura_mesa_max
                    },
                    "resolucao_camada_padrao": printer.resolucao_camada_padrao,
                    "velocidade_impressao_padrao": printer.velocidade_impressao_padrao
                },
                "criado_em": printer.created_at.isoformat()
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/printers/{printer_id}", response_model=dict)
async def update_printer(
    printer_id: UUID,
    printer_data: PrinterUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Atualizar configurações da impressora"""
    try:
        printer = await print3d_service.update_printer(db, printer_id, current_user.id, printer_data)
        return {
            "success": True,
            "message": "Impressora atualizada com sucesso",
            "data": {
                "id": str(printer.id),
                "nome": printer.nome,
                "status": printer.status
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/printers/{printer_id}", response_model=dict)
async def delete_printer(
    printer_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Excluir impressora"""
    try:
        success = await print3d_service.delete_printer(db, printer_id, current_user.id)
        return {
            "success": success,
            "message": "Impressora excluída com sucesso"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# =============================================================================
# ROTAS DE MATERIAIS
# =============================================================================

@router.post("/materials/", response_model=dict)
async def create_material(
    material_data: MaterialCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Criar novo material (apenas administradores)"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    try:
        material = await print3d_service.create_material(db, current_user.id, material_data)
        return {
            "success": True,
            "message": "Material criado com sucesso",
            "data": {
                "id": str(material.id),
                "nome": material.nome,
                "categoria": material.categoria,
                "fabricante": material.fabricante
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/materials/", response_model=dict)
async def get_materials(
    category: Optional[str] = Query(None, description="Filtrar por categoria"),
    active_only: bool = Query(True, description="Apenas materiais ativos"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Listar materiais disponíveis"""
    try:
        materials = await print3d_service.get_materials(db, category, active_only)
        return {
            "success": True,
            "data": {
                "materials": [
                    {
                        "id": str(m.id),
                        "nome": m.nome,
                        "categoria": m.categoria,
                        "fabricante": m.fabricante,
                        "temperatura_bico": m.temperatura_bico_recomendada,
                        "temperatura_mesa": m.temperatura_mesa_recomendada,
                        "densidade": m.densidade,
                        "preco_por_kg": float(m.preco_por_kg),
                        "ativo": m.ativo
                    }
                    for m in materials
                ],
                "total": len(materials)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/materials/search/", response_model=dict)
async def search_materials(
    q: str = Query(..., description="Termo de busca"),
    limit: int = Query(20, description="Limite de resultados"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Buscar materiais"""
    try:
        materials = await print3d_service.search_materials(db, q, limit)
        return {
            "success": True,
            "data": {
                "materials": [
                    {
                        "id": str(m.id),
                        "nome": m.nome,
                        "categoria": m.categoria,
                        "fabricante": m.fabricante,
                        "temperatura_bico": m.temperatura_bico_recomendada
                    }
                    for m in materials
                ],
                "total": len(materials)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# =============================================================================
# ROTAS DE JOBS DE IMPRESSÃO
# =============================================================================

@router.post("/print-jobs/", response_model=dict)
async def create_print_job(
    job_data: PrintJobCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Criar novo job de impressão"""
    try:
        job = await print3d_service.create_print_job(db, current_user.id, job_data)
        return {
            "success": True,
            "message": "Job de impressão criado com sucesso",
            "data": {
                "id": str(job.id),
                "nome": job.nome,
                "status": job.status,
                "tempo_estimado": job.tempo_estimado_segundos,
                "custo_material": float(job.custo_material or 0),
                "fila_posicao": job.fila_posicao
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/print-jobs/", response_model=dict)
async def list_print_jobs(
    status_filter: Optional[str] = Query(None, description="Filtrar por status (separado por vírgula)"),
    printer_id: Optional[UUID] = Query(None, description="Filtrar por impressora"),
    limit: int = Query(50, description="Limite de resultados"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Listar jobs de impressão do usuário"""
    try:
        # Processar filtros de status
        status_list = None
        if status_filter:
            status_list = [s.strip() for s in status_filter.split(',')]
        
        jobs = await print3d_service.list_print_jobs(db, current_user.id, status_list, printer_id, limit)
        
        return {
            "success": True,
            "data": {
                "jobs": [
                    {
                        "id": str(j.id),
                        "nome": j.nome,
                        "status": j.status,
                        "progresso": j.progresso_percentual,
                        "tempo_estimado": j.tempo_estimado_segundos,
                        "tempo_real": j.tempo_real_segundos,
                        "custo_material": float(j.custo_material or 0),
                        "peso_material": j.peso_material_g,
                        "fila_posicao": j.fila_posicao,
                        "printer": {
                            "id": str(j.printer.id),
                            "nome": j.printer.nome
                        } if j.printer else None,
                        "material": {
                            "id": str(j.material.id),
                            "nome": j.material.nome,
                            "categoria": j.material.categoria
                        } if j.material else None,
                        "criado_em": j.created_at.isoformat(),
                        "started_at": j.started_at.isoformat() if j.started_at else None,
                        "completed_at": j.completed_at.isoformat() if j.completed_at else None
                    }
                    for j in jobs
                ],
                "total": len(jobs)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/print-jobs/{job_id}", response_model=dict)
async def get_print_job(
    job_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter detalhes do job de impressão"""
    try:
        jobs = await print3d_service.list_print_jobs(db, current_user.id, limit=1)
        job = next((j for j in jobs if j.id == job_id), None)
        
        if not job:
            raise HTTPException(status_code=404, detail="Job não encontrado")
        
        return {
            "success": True,
            "data": {
                "id": str(job.id),
                "nome": job.nome,
                "descricao": job.descricao,
                "status": job.status,
                "progresso": job.progresso_percentual,
                "tempo_estimado": job.tempo_estimado_segundos,
                "tempo_real": job.tempo_real_segundos,
                "custo_material": float(job.custo_material or 0),
                "peso_material": job.peso_material_g,
                "dimensoes": {
                    "x": job.dimensao_x,
                    "y": job.dimensao_y,
                    "z": job.dimensao_z
                },
                "configuracoes": {
                    "altura_camada": job.altura_camada,
                    "percentual_preenchimento": job.percentual_preenchimento,
                    "velocidade_impressao": job.velocidade_impressao,
                    "temperatura_bico": job.temperatura_bico,
                    "temperatura_mesa": job.temperatura_mesa
                },
                "fila_posicao": job.fila_posicao,
                "arquivo_gcode": job.arquivo_gcode,
                "erros": job.error_log,
                "warnings": job.warnings,
                "printer": {
                    "id": str(job.printer.id),
                    "nome": job.printer.nome,
                    "status": job.printer.status
                } if job.printer else None,
                "material": {
                    "id": str(job.material.id),
                    "nome": job.material.nome,
                    "categoria": job.material.categoria
                } if job.material else None,
                "timestamps": {
                    "criado": job.created_at.isoformat(),
                    "started": job.started_at.isoformat() if job.started_at else None,
                    "completed": job.completed_at.isoformat() if job.completed_at else None,
                    "failed": job.failed_at.isoformat() if job.failed_at else None
                }
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/print-jobs/{job_id}/status", response_model=dict)
async def update_job_status(
    job_id: UUID,
    status_update: PrintJobStatus,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Atualizar status do job"""
    try:
        job = await print3d_service.update_job_status(db, job_id, current_user.id, status_update)
        return {
            "success": True,
            "message": "Status atualizado com sucesso",
            "data": {
                "id": str(job.id),
                "status": job.status,
                "progresso": job.progresso_percentual
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/print-jobs/{job_id}/generate-gcode", response_model=dict)
async def generate_gcode(
    job_id: UUID,
    slicer_type: str = Query("cura", description="Tipo de slicer a usar"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Gerar G-code para job"""
    try:
        gcode_path = await print3d_service.generate_gcode(db, job_id, current_user.id, slicer_type)
        return {
            "success": True,
            "message": "G-code gerado com sucesso",
            "data": {
                "gcode_path": gcode_path,
                "slicer_type": slicer_type
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/print-jobs/{job_id}/download-gcode", response_model=FileResponse)
async def download_gcode(
    job_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download do G-code gerado"""
    try:
        jobs = await print3d_service.list_print_jobs(db, current_user.id, limit=1)
        job = next((j for j in jobs if j.id == job_id), None)
        
        if not job:
            raise HTTPException(status_code=404, detail="Job não encontrado")
        
        if not job.arquivo_gcode:
            raise HTTPException(status_code=404, detail="G-code não encontrado")
        
        from pathlib import Path
        gcode_file = Path(job.arquivo_gcode)
        if not gcode_file.exists():
            raise HTTPException(status_code=404, detail="Arquivo G-code não existe")
        
        return FileResponse(
            path=str(gcode_file),
            filename=f"{job.nome}.gcode",
            media_type="text/plain"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/print-jobs/{job_id}/logs", response_model=dict)
async def get_job_logs(
    job_id: UUID,
    log_type: Optional[str] = Query(None, description="Filtrar por tipo de log"),
    limit: int = Query(100, description="Limite de logs"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter logs detalhados do job"""
    try:
        logs = await print3d_service.get_job_logs(db, job_id, current_user.id, log_type, limit)
        return {
            "success": True,
            "data": {
                "logs": [
                    {
                        "id": str(log.id),
                        "tipo": log.tipo_log,
                        "message": log.message,
                        "timestamp": log.timestamp.isoformat(),
                        "camada_atual": log.camada_atual,
                        "temperatura_bico": log.temperatura_bico,
                        "temperatura_mesa": log.temperatura_mesa,
                        "posicao_z": log.posicao_z
                    }
                    for log in logs
                ],
                "total": len(logs)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# =============================================================================
# ROTAS DE FILA DE IMPRESSÃO
# =============================================================================

@router.get("/print-queues/{printer_id}/status", response_model=dict)
async def get_queue_status(
    printer_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter status da fila de impressão"""
    try:
        queue_status = await print3d_service.get_queue_status(db, printer_id)
        return {
            "success": True,
            "data": queue_status
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/print-queues/{printer_id}/reorder", response_model=dict)
async def reorder_queue(
    printer_id: UUID,
    job_order: List[UUID],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reordenar jobs na fila"""
    try:
        success = await print3d_service.reorder_queue(db, printer_id, current_user.id, job_order)
        return {
            "success": success,
            "message": "Fila reordenada com sucesso"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# =============================================================================
# ROTAS DE ESTATÍSTICAS
# =============================================================================

@router.get("/statistics/", response_model=dict)
async def get_printing_statistics(
    printer_id: Optional[UUID] = Query(None, description="Filtrar por impressora específica"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter estatísticas de impressão"""
    try:
        stats = await print3d_service.get_printer_statistics(db, current_user.id, printer_id)
        return {
            "success": True,
            "data": stats
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))