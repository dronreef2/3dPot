"""
3dPot v2.0 - Schemas para Modelagem 3D
======================================

Este módulo define os schemas Pydantic para operações de modelagem 3D,
incluindo requisições, respostas e validações.

Autor: MiniMax Agent
Data: 2025-11-11
Versão: 1.0.0 - Sprint 3
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from uuid import UUID
from datetime import datetime
from enum import Enum


class ModelingEngineEnum(str, Enum):
    """Engines de modelagem disponíveis."""
    CADQUERY = "cadquery"
    OPENSCAD = "openscad"


class ModelFormatEnum(str, Enum):
    """Formatos de arquivo suportados."""
    STL = "stl"
    OBJ = "obj"
    STEP = "step"


class ModelCategory(str, Enum):
    """Categorias de projetos."""
    MECANICO = "mecanico"
    ELETRONICO = "eletronico"
    MISTO = "misto"
    ARQUITETURA = "arquitetura"


class MaterialType(str, Enum):
    """Tipos de materiais."""
    PLA = "PLA"
    ABS = "ABS"
    PETG = "PETG"
    NYLON = "nylon"
    METAL = "metal"
    RESINA = "resina"


class ModelSpecs(BaseModel):
    """Especificações para modelagem 3D."""
    category: ModelCategory = Field(..., description="Categoria do projeto")
    material: MaterialType = Field(..., description="Material preferencial")
    dimensions: Dict[str, float] = Field(
        ..., 
        description="Dimensões do modelo (largura, altura, profundidade)",
        example={"largura": 50.0, "altura": 30.0, "profundidade": 20.0}
    )
    additional_specs: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Especificações adicionais específicas do projeto"
    )
    components: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Componentes eletrônicos a serem incluídos"
    )
    features: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Funcionalidades específicas (furos, suportes, etc.)"
    )
    
    @validator('dimensions')
    def validate_dimensions(cls, v):
        """Valida se as dimensões são positivas."""
        required_keys = ['largura', 'altura', 'profundidade']
        
        for key in required_keys:
            if key not in v:
                raise ValueError(f"Dimensão '{key}' é obrigatória")
            
            if v[key] <= 0:
                raise ValueError(f"Dimensão '{key}' deve ser positiva")
        
        return v


class ModelingRequest(BaseModel):
    """Requisição para geração de modelo 3D."""
    specs: ModelSpecs = Field(..., description="Especificações do modelo")
    project_id: Optional[UUID] = Field(None, description="ID do projeto associado")
    engine: Optional[ModelingEngineEnum] = Field(
        default=ModelingEngineEnum.CADQUERY,
        description="Engine de modelagem a usar"
    )
    format: Optional[ModelFormatEnum] = Field(
        default=ModelFormatEnum.STL,
        description="Formato do arquivo de saída"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "specs": {
                    "category": "mecanico",
                    "material": "PLA",
                    "dimensions": {
                        "largura": 100.0,
                        "altura": 50.0,
                        "profundidade": 30.0
                    },
                    "additional_specs": {
                        "temperatura_impressao": 200,
                        "velocidade_impressao": 50
                    },
                    "components": [],
                    "features": [
                        {
                            "nome": "furo_central",
                            "tipo": "furo",
                            "diametro": 10.0,
                            "posicao": {"x": 0, "y": 0}
                        }
                    ]
                },
                "project_id": None,
                "engine": "cadquery",
                "format": "stl"
            }
        }


class PrintabilityReport(BaseModel):
    """Relatório de imprimibilidade do modelo."""
    printable: bool = Field(..., description="Se o modelo é imprimível")
    warnings: List[str] = Field(default_factory=list, description="Avisos sobre a impressão")
    errors: List[str] = Field(default_factory=list, description="Erros que impedem a impressão")
    metrics: Dict[str, Any] = Field(default_factory=dict, description="Métricas do modelo")
    
    class Config:
        schema_extra = {
            "example": {
                "printable": True,
                "warnings": ["Volume muito pequeno - verifique a escala"],
                "errors": [],
                "metrics": {
                    "volume_mm3": 15000.5,
                    "surface_area_mm2": 2500.0,
                    "vertices": 1200,
                    "faces": 800,
                    "file_size_bytes": 2048576,
                    "dimensions_mm": {
                        "x": 100.0,
                        "y": 50.0,
                        "z": 30.0
                    }
                }
            }
        }


class ModelingResponse(BaseModel):
    """Resposta da geração de modelo 3D."""
    success: bool = Field(..., description="Se a geração foi bem-sucedida")
    model_path: Optional[str] = Field(None, description="Caminho do arquivo gerado")
    engine_used: Optional[str] = Field(None, description="Engine utilizado")
    format_used: Optional[str] = Field(None, description="Formato do arquivo")
    message: str = Field(..., description="Mensagem sobre o resultado")
    specs: Optional[Dict[str, Any]] = Field(None, description="Especificações extraídas do modelo")
    validation_passed: bool = Field(False, description="Se passou na validação")
    printability_report: Optional[PrintabilityReport] = Field(None, description="Relatório de imprimibilidade")
    generation_time: float = Field(..., description="Tempo de geração em segundos")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "model_path": "/models/storage/model_1234567890.stl",
                "engine_used": "cadquery",
                "format_used": "stl",
                "message": "Modelo gerado com sucesso",
                "specs": {
                    "volume": 15000.5,
                    "surface_area": 2500.0,
                    "vertices": 1200,
                    "faces": 800,
                    "bbox": [[-50, -25, -15], [50, 25, 15]],
                    "file_size": 2048576,
                    "dimensions": {
                        "largura": 100.0,
                        "altura": 30.0,
                        "profundidade": 50.0
                    }
                },
                "validation_passed": True,
                "printability_report": {
                    "printable": True,
                    "warnings": ["Volume muito pequeno"],
                    "errors": [],
                    "metrics": {
                        "volume_mm3": 15000.5,
                        "surface_area_mm2": 2500.0,
                        "vertices": 1200,
                        "faces": 800
                    }
                },
                "generation_time": 2.45
            }
        }


class ModelingStatus(BaseModel):
    """Status de um modelo 3D."""
    model_id: UUID = Field(..., description="ID do modelo")
    file_exists: bool = Field(..., description="Se o arquivo existe")
    file_path: Optional[str] = Field(None, description="Caminho do arquivo")
    file_size: Optional[int] = Field(None, description="Tamanho do arquivo em bytes")
    validation: Dict[str, Any] = Field(..., description="Resultado da validação")
    specs: Dict[str, Any] = Field(..., description="Especificações do modelo")
    last_modified: float = Field(..., description="Timestamp da última modificação")
    
    @property
    def last_modified_datetime(self) -> datetime:
        """Data/hora da última modificação."""
        return datetime.fromtimestamp(self.last_modified)


class ModelFormatResponse(BaseModel):
    """Resposta com formatos suportados."""
    engine: str = Field(..., description="Engine de modelagem")
    formats: List[str] = Field(..., description="Formatos suportados")


class ModelingTemplate(BaseModel):
    """Template para modelagem 3D."""
    id: str = Field(..., description="ID único do template")
    name: str = Field(..., description="Nome do template")
    description: str = Field(..., description="Descrição do template")
    category: ModelCategory = Field(..., description="Categoria do template")
    default_engine: ModelingEngineEnum = Field(..., description="Engine padrão")
    default_format: ModelFormatEnum = Field(..., description="Formato padrão")
    required_specs: List[str] = Field(..., description="Especificações obrigatórias")
    optional_specs: List[str] = Field(..., description="Especificações opcionais")


class BatchModelingRequest(BaseModel):
    """Requisição para geração em lote."""
    requests: List[ModelingRequest] = Field(..., description="Lista de requisições de modelagem")


class BatchModelingResponse(BaseModel):
    """Resposta da geração em lote."""
    total_requests: int = Field(..., description="Total de requisições")
    successful: int = Field(..., description="Quantidade de sucessos")
    failed: int = Field(..., description="Quantidade de falhas")
    results: List[Dict[str, Any]] = Field(..., description="Resultados individuais")


class ModelInfo(BaseModel):
    """Informações básicas de um modelo."""
    id: UUID = Field(..., description="ID único do modelo")
    name: str = Field(..., description="Nome do modelo")
    category: ModelCategory = Field(..., description="Categoria do modelo")
    material: MaterialType = Field(..., description="Material usado")
    file_path: str = Field(..., description="Caminho do arquivo")
    file_size: int = Field(..., description="Tamanho do arquivo")
    format: ModelFormatEnum = Field(..., description="Formato do arquivo")
    engine: ModelingEngineEnum = Field(..., description="Engine usado")
    created_at: datetime = Field(..., description="Data de criação")
    specs: Dict[str, Any] = Field(..., description="Especificações do modelo")
    printable: bool = Field(..., description="Se é imprimível")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "Suporte Mecânico v1",
                "category": "mecanico",
                "material": "PLA",
                "file_path": "/models/storage/model_123.stl",
                "file_size": 2048576,
                "format": "stl",
                "engine": "cadquery",
                "created_at": "2025-11-11T22:56:21Z",
                "specs": {
                    "volume": 15000.5,
                    "vertices": 1200,
                    "faces": 800
                },
                "printable": True
            }
        }


class ModelValidationResult(BaseModel):
    """Resultado da validação de um modelo."""
    model_id: UUID = Field(..., description="ID do modelo")
    file_path: str = Field(..., description="Caminho do arquivo")
    validation: Dict[str, Any] = Field(..., description="Resultado da validação")
    specs: Dict[str, Any] = Field(..., description="Especificações extraídas")
    printability: Dict[str, Any] = Field(..., description="Relatório de imprimibilidade")
    recommendations: List[str] = Field(default_factory=list, description="Recomendações")