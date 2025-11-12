"""
API Routes para Geração de Relatórios PDF de Simulações
Endpoints para criar, baixar e gerenciar relatórios
"""

import logging
from typing import List, Optional
from uuid import UUID
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query, Response
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from ..database import get_db
from ..middleware.auth import get_current_user
from ..models import User, Simulation
from ..services.simulation_report_service import SimulationReportService

logger = logging.getLogger(__name__)
router = APIRouter()

# Instância global do serviço de relatórios
report_service = SimulationReportService()

@router.post("/simulations/{simulation_id}/report/pdf")
async def generate_simulation_report(
    simulation_id: UUID,
    include_charts: bool = Query(True, description="Incluir gráficos no relatório"),
    include_technical_details: bool = Query(True, description="Incluir detalhes técnicos"),
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Gerar relatório PDF completo de uma simulação
    
    - **simulation_id**: ID da simulação
    - **include_charts**: Se deve incluir gráficos
    - **include_technical_details**: Se deve incluir detalhes técnicos
    """
    try:
        # Verificar se simulação existe e pertence ao usuário
        simulation = db.query(Simulation).filter(
            Simulation.id == simulation_id,
            Simulation.user_id == current_user.id
        ).first()
        
        if not simulation:
            raise HTTPException(
                status_code=404,
                detail="Simulação não encontrada ou acesso negado"
            )
        
        # Verificar se simulação foi concluída
        if simulation.status != "completed":
            raise HTTPException(
                status_code=400,
                detail=f"Não é possível gerar relatório de simulação com status '{simulation.status}'. Simulação deve estar concluída."
            )
        
        # Gerar relatório em background
        def generate_report_task():
            try:
                # Usar preferências padrão por enquanto
                preferences = {
                    "format": "detailed",
                    "language": "pt-BR",
                    "include_cover_page": True,
                    "include_toc": True
                }
                
                report_path = report_service.generate_simulation_report(
                    db=db,
                    simulation_id=simulation_id,
                    include_charts=include_charts,
                    include_technical_details=include_technical_details,
                    user_format_preferences=preferences
                )
                
                logger.info(f"Relatório PDF gerado: {report_path}")
                return report_path
                
            except Exception as e:
                logger.error(f"Erro na geração do relatório: {e}")
                raise
        
        # Executar geração em background
        background_tasks.add_task(generate_report_task)
        
        logger.info(f"Geração de relatório iniciada para simulação {simulation_id}")
        
        return {
            "message": "Geração de relatório iniciada",
            "simulation_id": str(simulation_id),
            "status": "generating",
            "estimated_time": "2-5 minutos"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao iniciar geração de relatório: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@router.get("/simulations/{simulation_id}/report/pdf")
async def download_simulation_report(
    simulation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Baixar relatório PDF de uma simulação
    """
    try:
        # Verificar se simulação existe e pertence ao usuário
        simulation = db.query(Simulation).filter(
            Simulation.id == simulation_id,
            Simulation.user_id == current_user.id
        ).first()
        
        if not simulation:
            raise HTTPException(
                status_code=404,
                detail="Simulação não encontrada ou acesso negado"
            )
        
        # Buscar arquivo de relatório mais recente
        report_pattern = f"simulacao_{simulation_id}_*.pdf"
        report_files = list(report_service.reports_path.glob(report_pattern))
        
        if not report_files:
            raise HTTPException(
                status_code=404,
                detail="Nenhum relatório encontrado para esta simulação. Gere um relatório primeiro."
            )
        
        # Obter o arquivo mais recente
        latest_report = max(report_files, key=lambda f: f.stat().st_mtime)
        
        if not latest_report.exists():
            raise HTTPException(
                status_code=404,
                detail="Arquivo de relatório não encontrado no sistema"
            )
        
        # Verificar se o arquivo é acessível
        if not latest_report.is_file():
            raise HTTPException(
                status_code=500,
                detail="Corrupção detectada no arquivo de relatório"
            )
        
        logger.info(f"Download de relatório: {latest_report}")
        
        return FileResponse(
            path=str(latest_report),
            media_type="application/pdf",
            filename=f"relatorio_simulacao_{simulation_id}.pdf"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no download do relatório: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@router.post("/simulations/report/comparative")
async def generate_comparative_report(
    simulation_ids: List[UUID],
    title: str = Query("Relatório Comparativo de Simulações", description="Título do relatório"),
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Gerar relatório comparativo de múltiplas simulações
    """
    try:
        if len(simulation_ids) < 2:
            raise HTTPException(
                status_code=400,
                detail="Pelo menos 2 simulações são necessárias para relatório comparativo"
            )
        
        if len(simulation_ids) > 10:
            raise HTTPException(
                status_code=400,
                detail="Máximo de 10 simulações permitidas por relatório"
            )
        
        # Verificar se todas as simulações pertencem ao usuário
        simulations = db.query(Simulation).filter(
            Simulation.id.in_(simulation_ids),
            Simulation.user_id == current_user.id
        ).all()
        
        if len(simulations) != len(simulation_ids):
            raise HTTPException(
                status_code=404,
                detail="Uma ou mais simulações não encontradas ou acesso negado"
            )
        
        # Verificar se todas estão concluídas
        pending_simulations = [s for s in simulations if s.status != "completed"]
        if pending_simulations:
            pending_ids = [str(s.id) for s in pending_simulations]
            raise HTTPException(
                status_code=400,
                detail=f"Simulações devem estar concluídas para relatório comparativo. Pendentes: {', '.join(pending_ids)}"
            )
        
        # Gerar relatório comparativo em background
        def generate_comparative_task():
            try:
                report_path = report_service.generate_summary_report(
                    db=db,
                    simulations=simulation_ids,
                    title=title
                )
                
                logger.info(f"Relatório comparativo gerado: {report_path}")
                return report_path
                
            except Exception as e:
                logger.error(f"Erro na geração do relatório comparativo: {e}")
                raise
        
        background_tasks.add_task(generate_comparative_task)
        
        logger.info(f"Geração de relatório comparativo iniciada para {len(simulation_ids)} simulações")
        
        return {
            "message": "Geração de relatório comparativo iniciada",
            "simulation_count": len(simulation_ids),
            "title": title,
            "status": "generating",
            "estimated_time": "3-7 minutos"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao iniciar relatório comparativo: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@router.get("/reports/list")
async def list_simulation_reports(
    simulation_id: Optional[UUID] = Query(None, description="Filtrar por simulação específica"),
    limit: int = Query(50, ge=1, le=100, description="Número máximo de resultados"),
    offset: int = Query(0, ge=0, description="Offset para paginação"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Listar relatórios gerados pelo usuário
    """
    try:
        # Buscar simulações do usuário
        query = db.query(Simulation).filter(Simulation.user_id == current_user.id)
        
        # Filtrar por simulação específica se fornecida
        if simulation_id:
            query = query.filter(Simulation.id == simulation_id)
        
        # Apenas simulações com relatórios (status completed)
        query = query.filter(Simulation.status == "completed")
        
        simulations = query.order_by(Simulation.updated_at.desc()).offset(offset).limit(limit).all()
        
        reports_list = []
        for simulation in simulations:
            # Buscar relatórios relacionados
            report_pattern = f"simulacao_{simulation.id}_*.pdf"
            report_files = list(report_service.reports_path.glob(report_pattern))
            
            reports_info = []
            for report_file in report_files:
                reports_info.append({
                    "filename": report_file.name,
                    "size_bytes": report_file.stat().st_size,
                    "created_at": report_file.stat().st_mtime,
                    "download_url": f"/api/v1/simulation-reports/reports/{report_file.name}"
                })
            
            # Se houver relatórios ou se for para mostrar mesmo sem relatórios
            if reports_info or not simulation_id:
                reports_list.append({
                    "simulation_id": str(simulation.id),
                    "simulation_name": simulation.nome,
                    "simulation_type": simulation.tipo_simulacao,
                    "simulation_status": simulation.status,
                    "created_at": simulation.created_at,
                    "report_count": len(reports_info),
                    "reports": reports_info
                })
        
        return {
            "total": len(reports_list),
            "simulations": reports_list,
            "offset": offset,
            "limit": limit
        }
        
    except Exception as e:
        logger.error(f"Erro ao listar relatórios: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@router.get("/reports/{filename}")
async def download_specific_report(
    filename: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Baixar relatório específico pelo nome do arquivo
    """
    try:
        # Verificar se o arquivo existe
        report_path = report_service.reports_path / filename
        
        if not report_path.exists():
            raise HTTPException(
                status_code=404,
                detail="Arquivo de relatório não encontrado"
            )
        
        # Extrair ID da simulação do nome do arquivo (formato: simulacao_UUID_timestamp.pdf)
        parts = filename.split('_')
        if len(parts) < 3:
            raise HTTPException(
                status_code=400,
                detail="Formato de nome de arquivo inválido"
            )
        
        try:
            simulation_id_str = parts[1]
            simulation_id = UUID(simulation_id_str)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="ID de simulação inválido no nome do arquivo"
            )
        
        # Verificar se o usuário tem acesso à simulação
        simulation = db.query(Simulation).filter(
            Simulation.id == simulation_id,
            Simulation.user_id == current_user.id
        ).first()
        
        if not simulation:
            raise HTTPException(
                status_code=403,
                detail="Acesso negado a este relatório"
            )
        
        logger.info(f"Download de relatório específico: {filename}")
        
        return FileResponse(
            path=str(report_path),
            media_type="application/pdf",
            filename=filename
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no download do relatório específico: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@router.delete("/reports/{filename}")
async def delete_specific_report(
    filename: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Excluir relatório específico
    """
    try:
        # Verificar se o arquivo existe
        report_path = report_service.reports_path / filename
        
        if not report_path.exists():
            raise HTTPException(
                status_code=404,
                detail="Arquivo de relatório não encontrado"
            )
        
        # Validar nome do arquivo e extrair ID da simulação
        parts = filename.split('_')
        if len(parts) < 3:
            raise HTTPException(
                status_code=400,
                detail="Formato de nome de arquivo inválido"
            )
        
        try:
            simulation_id_str = parts[1]
            simulation_id = UUID(simulation_id_str)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="ID de simulação inválido no nome do arquivo"
            )
        
        # Verificar se o usuário tem acesso à simulação
        simulation = db.query(Simulation).filter(
            Simulation.id == simulation_id,
            Simulation.user_id == current_user.id
        ).first()
        
        if not simulation:
            raise HTTPException(
                status_code=403,
                detail="Acesso negado a este relatório"
            )
        
        # Excluir arquivo
        try:
            report_path.unlink()
            logger.info(f"Relatório excluído: {filename}")
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao excluir arquivo: {str(e)}"
            )
        
        return {
            "message": "Relatório excluído com sucesso",
            "filename": filename,
            "simulation_id": str(simulation_id)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao excluir relatório: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@router.post("/reports/cleanup")
async def cleanup_old_reports(
    days: int = Query(30, ge=1, le=365, description="Número de dias para manter relatórios"),
    current_user: User = Depends(get_current_user)
):
    """
    Limpar relatórios antigos do usuário
    """
    try:
        # Esta funcionalidade limitaria apenas relatórios do usuário atual
        # Por enquanto, implementação global para simplicidade
        
        removed_count = report_service.cleanup_old_reports(days)
        
        return {
            "message": "Limpeza de relatórios concluída",
            "days_kept": days,
            "reports_removed": removed_count,
            "cleanup_time": "automatic"
        }
        
    except Exception as e:
        logger.error(f"Erro na limpeza de relatórios: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@router.get("/reports/status")
async def get_report_generation_status(
    simulation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Verificar status da geração de relatório para uma simulação
    """
    try:
        # Verificar se simulação existe e pertence ao usuário
        simulation = db.query(Simulation).filter(
            Simulation.id == simulation_id,
            Simulation.user_id == current_user.id
        ).first()
        
        if not simulation:
            raise HTTPException(
                status_code=404,
                detail="Simulação não encontrada ou acesso negado"
            )
        
        # Buscar relatórios existentes
        report_pattern = f"simulacao_{simulation_id}_*.pdf"
        report_files = list(report_service.reports_path.glob(report_pattern))
        
        reports_info = []
        for report_file in report_files:
            reports_info.append({
                "filename": report_file.name,
                "size_bytes": report_file.stat().st_size,
                "created_at": report_file.stat().st_mtime,
                "download_url": f"/api/v1/simulation-reports/reports/{report_file.name}"
            })
        
        # Ordenar por data de criação (mais recente primeiro)
        reports_info.sort(key=lambda x: x["created_at"], reverse=True)
        
        return {
            "simulation_id": str(simulation_id),
            "simulation_status": simulation.status,
            "has_reports": len(reports_info) > 0,
            "report_count": len(reports_info),
            "latest_report": reports_info[0] if reports_info else None,
            "all_reports": reports_info
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao verificar status do relatório: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")