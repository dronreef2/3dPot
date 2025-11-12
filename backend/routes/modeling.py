"""
3dPot v2.0 - Rotas de API para Modelagem 3D
===========================================

Este módulo implementa os endpoints REST para operações de modelagem 3D,
incluindo geração de modelos a partir de especificações extraídas.

Autor: MiniMax Agent
Data: 2025-11-11
Versão: 1.0.0 - Sprint 3
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from uuid import UUID, uuid4
from typing import List, Optional, Dict, Any
import os
import logging
from pathlib import Path

from database import get_db
from middleware.auth import get_current_user
from services.modeling_service import (
    get_modeling_service, 
    ModelingEngine, 
    ModelFormat, 
    ModelingSpecs,
    ModelingResult
)
from schemas.modeling import (
    ModelingRequest,
    ModelingResponse,
    ModelSpecs,
    PrintabilityReport,
    ModelingStatus,
    ModelFormatResponse
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["modeling"])


@router.get("/modeling/engines", response_model=List[str])
async def list_modeling_engines():
    """Lista engines de modelagem 3D disponíveis."""
    try:
        service = get_modeling_service()
        engines = service.get_available_engines()
        return engines
    except Exception as e:
        logger.error(f"Erro ao listar engines: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get("/modeling/formats", response_model=ModelFormatResponse)
async def get_supported_formats(engine: str = Query(..., description="Engine de modelagem")):
    """Lista formatos suportados por um engine específico."""
    try:
        service = get_modeling_service()
        formats = service.get_supported_formats(engine)
        return ModelFormatResponse(engine=engine, formats=formats)
    except Exception as e:
        logger.error(f"Erro ao listar formatos: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.post("/modeling/generate", response_model=ModelingResponse)
async def generate_model(
    request: ModelingRequest,
    current_user = Depends(get_current_user),
    background_tasks: BackgroundTasks = None
):
    """
    Gera modelo 3D a partir das especificações extraídas.
    
    Este endpoint recebe as especificações extraídas da conversa e gera
    um modelo 3D usando o engine de modelagem especificado.
    """
    try:
        service = get_modeling_service()
        
        # Converter para formato do serviço
        specs = {
            "categoria": request.specs.category,
            "material": request.specs.material,
            "dimensoes": request.specs.dimensions,
            "especificacoes_adicionais": request.specs.additional_specs or {},
            "componentes": request.specs.components or [],
            "funcionalidades": request.specs.features or []
        }
        
        # Gerar modelo
        result = service.generate_model_from_specs(
            specifications=specs,
            project_id=request.project_id,
            engine=ModelingEngine(request.engine) if request.engine else None,
            format=ModelFormat(request.format) if request.format else None
        )
        
        if not result.success:
            raise HTTPException(
                status_code=400, 
                detail=f"Erro na geração do modelo: {result.message}"
            )
        
        # Preparar resposta
        response = ModelingResponse(
            success=result.success,
            model_path=result.model_path,
            engine_used=result.engine_used.value if result.engine_used else None,
            format_used=result.format_used.value if result.format_used else None,
            message=result.message,
            specs=result.specs,
            validation_passed=result.validation_passed,
            printability_report=PrintabilityReport(**result.printability_report) if result.printability_report else None,
            generation_time=result.generation_time
        )
        
        logger.info(f"Modelo 3D gerado com sucesso: {result.model_path}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro na geração do modelo: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno do servidor na geração do modelo"
        )


@router.get("/modeling/status/{model_id}", response_model=ModelingStatus)
async def get_modeling_status(
    model_id: UUID,
    current_user = Depends(get_current_user)
):
    """Verifica o status de um modelo 3D."""
    try:
        service = get_modeling_service()
        
        # Buscar modelo pelo ID (implementar consulta ao banco)
        # Por enquanto, verificar se o arquivo existe
        
        # Verificar se arquivo existe e obter status
        models_dir = service.storage_path
        model_files = list(models_dir.glob(f"*{model_id}*.stl"))
        
        if not model_files:
            raise HTTPException(
                status_code=404,
                detail="Modelo não encontrado"
            )
        
        model_file = model_files[0]
        
        # Validar modelo
        validation = service._validate_model(str(model_file))
        
        # Extrair especificações
        specs = service._extract_model_specs(str(model_file))
        
        return ModelingStatus(
            model_id=model_id,
            file_exists=True,
            file_path=str(model_file),
            file_size=model_file.stat().st_size,
            validation=validation,
            specs=specs,
            last_modified=model_file.stat().st_mtime
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao verificar status do modelo: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno do servidor"
        )


@router.get("/modeling/download/{model_id}")
async def download_model(
    model_id: UUID,
    format: str = Query(default="stl", description="Formato do arquivo"),
    current_user = Depends(get_current_user)
):
    """
    Baixa modelo 3D gerado.
    
    Este endpoint permite baixar o modelo 3D gerado no formato especificado.
    """
    try:
        service = get_modeling_service()
        
        # Buscar modelo pelo ID
        models_dir = service.storage_path
        
        # Buscar arquivo no formato solicitado
        pattern = f"*{model_id}*.{format.lower()}"
        model_files = list(models_dir.glob(pattern))
        
        if not model_files:
            raise HTTPException(
                status_code=404,
                detail=f"Modelo no formato {format} não encontrado"
            )
        
        model_file = model_files[0]
        
        if not model_file.exists():
            raise HTTPException(
                status_code=404,
                detail="Arquivo do modelo não encontrado"
            )
        
        # Verificar se é arquivo STL
        if format.lower() == "stl":
            media_type = "application/vnd.ms-pki.stl"
        elif format.lower() == "obj":
            media_type = "text/plain"
        elif format.lower() == "step":
            media_type = "application/step"
        else:
            media_type = "application/octet-stream"
        
        # Nome do arquivo para download
        download_name = f"3dpot_model_{model_id}.{format.lower()}"
        
        logger.info(f"Download do modelo 3D: {model_file}")
        
        return FileResponse(
            path=str(model_file),
            media_type=media_type,
            filename=download_name,
            headers={"Content-Disposition": f"attachment; filename={download_name}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no download do modelo: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno do servidor"
        )


@router.delete("/modeling/model/{model_id}")
async def delete_model(
    model_id: UUID,
    current_user = Depends(get_current_user)
):
    """Exclui modelo 3D e seus arquivos associados."""
    try:
        service = get_modeling_service()
        
        # Buscar todos os arquivos do modelo
        models_dir = service.storage_path
        
        # Buscar por padrão de ID
        model_patterns = [f"*{model_id}*.stl", f"*{model_id}*.obj", f"*{model_id}*.step"]
        
        deleted_files = []
        
        for pattern in model_patterns:
            model_files = list(models_dir.glob(pattern))
            for model_file in model_files:
                try:
                    model_file.unlink()
                    deleted_files.append(str(model_file))
                except Exception as e:
                    logger.warning(f"Não foi possível excluir {model_file}: {str(e)}")
        
        if not deleted_files:
            raise HTTPException(
                status_code=404,
                detail="Modelo não encontrado"
            )
        
        logger.info(f"Modelo excluído com sucesso: {deleted_files}")
        
        return {
            "success": True,
            "message": f"Modelo {model_id} excluído com sucesso",
            "deleted_files": deleted_files
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao excluir modelo: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno do servidor"
        )


@router.post("/modeling/validate/{model_id}")
async def validate_model(
    model_id: UUID,
    current_user = Depends(get_current_user)
):
    """Valida modelo 3D gerado para impressão 3D."""
    try:
        service = get_modeling_service()
        
        # Buscar arquivo do modelo
        models_dir = service.storage_path
        model_files = list(models_dir.glob(f"*{model_id}*.stl"))
        
        if not model_files:
            raise HTTPException(
                status_code=404,
                detail="Modelo não encontrado"
            )
        
        model_file = model_files[0]
        
        # Validar modelo
        validation = service._validate_model(str(model_file))
        
        # Extrair especificações
        specs = service._extract_model_specs(str(model_file))
        
        # Preparar relatório completo
        report = {
            "model_id": model_id,
            "file_path": str(model_file),
            "validation": validation,
            "specs": specs,
            "printability": {
                "is_printable": validation.get("printable", False),
                "warnings": validation.get("warnings", []),
                "errors": validation.get("errors", []),
                "recommendations": []
            }
        }
        
        # Adicionar recomendações baseadas nos resultados
        if validation.get("errors"):
            report["printability"]["recommendations"].append(
                "Corrija os erros identificados antes da impressão"
            )
        
        if validation.get("warnings"):
            report["printability"]["recommendations"].append(
                "Revise os avisos para melhorar a qualidade da impressão"
            )
        
        metrics = validation.get("metrics", {})
        if metrics.get("volume_mm3", 0) > 100000:  # > 100 cm³
            report["printability"]["recommendations"].append(
                "Modelo muito grande - considere dividir em partes"
            )
        
        logger.info(f"Modelo validado: {model_id}")
        return report
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro na validação do modelo: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno do servidor"
        )


@router.get("/modeling/templates")
async def get_modeling_templates():
    """Lista templates de modelagem disponíveis."""
    templates = [
        {
            "id": "mecanico_basico",
            "name": "Projeto Mecânico Básico",
            "description": "Modelo mecânico simples com furos de fixação",
            "category": "mecanico",
            "default_engine": "cadquery",
            "default_format": "stl",
            "required_specs": ["dimensoes", "material"],
            "optional_specs": ["furos", "suportes"]
        },
        {
            "id": "eletronico_basico",
            "name": "Projeto Eletrônico Básico",
            "description": "Modelo para projetos eletrônicos com ventilação",
            "category": "eletronico",
            "default_engine": "openscad",
            "default_format": "stl",
            "required_specs": ["dimensoes", "material"],
            "optional_specs": ["ventilacao", "componentes"]
        },
        {
            "id": "arquitetura_basico",
            "name": "Projeto Arquitetônico Básico",
            "description": "Modelo arquitetônico com base reforçada",
            "category": "arquitetura",
            "default_engine": "cadquery",
            "default_format": "stl",
            "required_specs": ["dimensoes", "material"],
            "optional_specs": ["pilares", "vigas"]
        }
    ]
    
    return templates


@router.post("/modeling/batch-generate")
async def batch_generate_models(
    requests: List[ModelingRequest],
    current_user = Depends(get_current_user),
    background_tasks: BackgroundTasks = None
):
    """Gera múltiplos modelos 3D em lote."""
    try:
        service = get_modeling_service()
        results = []
        
        for request in requests:
            try:
                # Converter especificações
                specs = {
                    "categoria": request.specs.category,
                    "material": request.specs.material,
                    "dimensoes": request.specs.dimensions,
                    "especificacoes_adicionais": request.specs.additional_specs or {},
                    "componentes": request.specs.components or [],
                    "funcionalidades": request.specs.features or []
                }
                
                # Gerar modelo
                result = service.generate_model_from_specs(
                    specifications=specs,
                    project_id=request.project_id,
                    engine=ModelingEngine(request.engine) if request.engine else None,
                    format=ModelFormat(request.format) if request.format else None
                )
                
                results.append({
                    "request_id": getattr(request, 'id', None),
                    "success": result.success,
                    "model_path": result.model_path,
                    "message": result.message,
                    "generation_time": result.generation_time
                })
                
            except Exception as e:
                results.append({
                    "request_id": getattr(request, 'id', None),
                    "success": False,
                    "message": str(e),
                    "model_path": None,
                    "generation_time": 0
                })
        
        logger.info(f"Geração em lote concluída: {len([r for r in results if r['success']])}/{len(results)} sucessos")
        
        return {
            "total_requests": len(requests),
            "successful": len([r for r in results if r['success']]),
            "failed": len([r for r in results if not r['success']]),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Erro na geração em lote: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno do servidor na geração em lote"
        )