"""
3dPot v2.0 - Serviço de Modelagem 3D Avançado
=============================================

Este módulo implementa o serviço de modelagem 3D que converte especificações
extraídas em modelos 3D usando diferentes engines de modelagem paramétrica.

Suporta CadQuery e OpenSCAD para geração automatizada de modelos 3D
com validação de imprimibilidade e pós-processamento.

Autor: MiniMax Agent
Data: 2025-11-11
Versão: 2.0.0 - Sprint 3
"""

import os
import json
import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union
from uuid import UUID
from dataclasses import dataclass
from enum import Enum
import time

import cadquery as cq
import trimesh
from sqlalchemy.orm import Session
from trimesh import Trimesh
import numpy as np

from core.config import MODELS_STORAGE_PATH, TEMP_STORAGE_PATH
from models import Model3D, Project
from schemas import Model3DCreate

logger = logging.getLogger(__name__)


class ModelingEngine(Enum):
    """Tipos de engines de modelagem suportados."""
    CADQUERY = "cadquery"
    OPENSCAD = "openscad"


class ModelFormat(Enum):
    """Formatos de arquivo suportados."""
    STL = "stl"
    OBJ = "obj"
    STEP = "step"
    DXF = "dxf"


@dataclass
class ModelingSpecs:
    """Especificações para modelagem 3D."""
    category: str  # mecânico, eletrônico, misto, arquitetura
    material: str  # PLA, ABS, PETG, etc.
    dimensions: Dict[str, float]  # largura, altura, profundidade
    additional_specs: Dict[str, Any]  # especificações adicionais
    components: List[Dict[str, Any]] = None  # componentes eletrônicos
    features: List[Dict[str, Any]] = None   # funcionalidades específicas


@dataclass
class ModelingResult:
    """Resultado da modelagem 3D."""
    success: bool
    model_path: Optional[str] = None
    engine_used: Optional[ModelingEngine] = None
    format_used: Optional[ModelFormat] = None
    message: str = ""
    specs: Optional[Dict[str, Any]] = None
    validation_passed: bool = False
    printability_report: Optional[Dict[str, Any]] = None
    generation_time: float = 0.0

class ModelingService:
    """
    Serviço avançado para modelagem 3D paramétrica.
    
    Este serviço permite a geração de modelos 3D a partir de especificações
    usando diferentes engines de modelagem paramétrica (CadQuery, OpenSCAD)
    com validação de imprimibilidade e pós-processamento.
    """
    
    def __init__(self):
        self.storage_path = MODELS_STORAGE_PATH
        self.temp_path = TEMP_STORAGE_PATH
        
        # Garantir que os diretórios existam
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.temp_path.mkdir(parents=True, exist_ok=True)
        
        # Configurar engines disponíveis
        self._available_engines = self._check_engines()
        
        # Configurações padrão
        self.default_engine = ModelingEngine.CADQUERY
        self.default_format = ModelFormat.STL
        
        logger.info(f"ModelingService inicializado com engines: {list(self._available_engines.keys())}")
    
    def _check_engines(self) -> Dict[ModelingEngine, bool]:
        """Verifica quais engines estão disponíveis."""
        engines = {}
        
        # Verificar CadQuery
        try:
            import cadquery
            engines[ModelingEngine.CADQUERY] = True
            logger.info("Engine CadQuery disponível")
        except ImportError:
            engines[ModelingEngine.CADQUERY] = False
            logger.warning("Engine CadQuery não disponível")
        
        # Verificar OpenSCAD
        try:
            result = subprocess.run(['openscad', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            engines[ModelingEngine.OPENSCAD] = result.returncode == 0
            if engines[ModelingEngine.OPENSCAD]:
                logger.info("Engine OpenSCAD disponível")
            else:
                logger.warning("Engine OpenSCAD não disponível")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            engines[ModelingEngine.OPENSCAD] = False
            logger.warning("Engine OpenSCAD não disponível")
        
        return engines
    
    def generate_model_from_specs(self, specifications: Dict[str, Any], 
                                project_id: Optional[UUID] = None,
                                engine: Optional[ModelingEngine] = None,
                                format: Optional[ModelFormat] = None) -> ModelingResult:
        """
        Gera modelo 3D a partir das especificações extraídas.
        
        Args:
            specifications: Especificações extraídas da conversa
            project_id: ID do projeto para identificação do arquivo
            engine: Engine de modelagem a usar (padrão: CadQuery)
            format: Formato do arquivo de saída (padrão: STL)
            
        Returns:
            ModelingResult com o resultado da modelagem
        """
        start_time = time.time()
        
        try:
            # Configurar parâmetros
            engine = engine or self.default_engine
            format = format or self.default_format
            
            # Verificar disponibilidade
            if not self._available_engines.get(engine, False):
                return ModelingResult(
                    success=False,
                    message=f"Engine {engine.value} não disponível",
                    engine_used=engine,
                    format_used=format,
                    generation_time=time.time() - start_time
                )
            
            # Converter especificações
            specs = self._convert_specifications(specifications)
            
            # Gerar modelo usando o engine selecionado
            model_path = self._generate_model(specs, engine, format, project_id)
            
            # Validar modelo gerado
            validation_result = self._validate_model(model_path)
            
            # Extrair especificações do modelo
            model_specs = self._extract_model_specs(model_path)
            
            generation_time = time.time() - start_time
            
            return ModelingResult(
                success=True,
                model_path=model_path,
                engine_used=engine,
                format_used=format,
                message="Modelo gerado com sucesso",
                specs=model_specs,
                validation_passed=validation_result["printable"],
                printability_report=validation_result,
                generation_time=generation_time
            )
            
        except Exception as e:
            logger.error(f"Erro na modelagem: {str(e)}")
            return ModelingResult(
                success=False,
                message=f"Erro na modelagem: {str(e)}",
                engine_used=engine,
                format_used=format,
                generation_time=time.time() - start_time
            )
    
    def _convert_specifications(self, specifications: Dict[str, Any]) -> ModelingSpecs:
        """Converte especificações do formato extraído para ModelingSpecs."""
        dims = specifications.get("dimensoes", {})
        
        return ModelingSpecs(
            category=specifications.get("categoria", "mecanico"),
            material=specifications.get("material", "PLA"),
            dimensions={
                "largura": float(dims.get("largura", 50.0)),
                "altura": float(dims.get("altura", 50.0)),
                "profundidade": float(dims.get("profundidade", 50.0))
            },
            additional_specs=specifications.get("especificacoes_adicionais", {}),
            components=specifications.get("componentes", []),
            features=specifications.get("funcionalidades", [])
        )
    
    def _generate_model(self, specs: ModelingSpecs, engine: ModelingEngine, 
                      format: ModelFormat, project_id: Optional[UUID] = None) -> str:
        """Gera modelo 3D usando o engine especificado."""
        if engine == ModelingEngine.CADQUERY:
            return self._generate_cadquery_model(specs, format, project_id)
        elif engine == ModelingEngine.OPENSCAD:
            return self._generate_openscad_model(specs, format, project_id)
        else:
            raise ValueError(f"Engine {engine.value} não suportado")
    
    def _generate_cadquery_model(self, specs: ModelingSpecs, format: ModelFormat, 
                               project_id: Optional[UUID] = None) -> str:
        """Gera modelo usando CadQuery."""
        # Converter dimensões (considerando unidade padrão em mm)
        width = specs.dimensions.get('largura', 50.0)
        height = specs.dimensions.get('altura', 50.0)
        depth = specs.dimensions.get('profundidade', 50.0)
        
        # Iniciar criação do modelo
        model = cq.Workplane("XY").box(width, depth, height)
        
        # Aplicar especificações baseado na categoria
        if specs.category == "mecanico":
            model = self._apply_mechanical_specs_cadquery(model, specs)
        elif specs.category == "eletronico":
            model = self._apply_electronic_specs_cadquery(model, specs)
        elif specs.category == "arquitetura":
            model = self._apply_architectural_specs_cadquery(model, specs)
        
        # Aplicar funcionalidades específicas
        if specs.features:
            model = self._apply_features_cadquery(model, specs.features)
        
        # Gerar arquivo de saída
        output_path = self._get_output_path(format, project_id)
        
        # Exportar no formato solicitado
        if format == ModelFormat.STL:
            cq.exporters.export(model, output_path, exportType='STL')
        elif format == ModelFormat.STEP:
            cq.exporters.export(model, output_path, exportType='STEP')
        elif format == ModelFormat.OBJ:
            cq.exporters.export(model, output_path, exportType='OBJ')
        else:
            raise ValueError(f"Formato {format.value} não suportado para CadQuery")
        
        logger.info(f"Modelo CadQuery gerado: {output_path}")
        return output_path
    
    def _generate_openscad_model(self, specs: ModelingSpecs, format: ModelFormat,
                               project_id: Optional[UUID] = None) -> str:
        """Gera modelo usando OpenSCAD."""
        # Converter especificações para código OpenSCAD
        openscad_code = self._generate_openscad_code(specs)
        
        # Escrever código temporário
        temp_scad = os.path.join(self.temp_path, f"temp_{project_id or 'model'}.scad")
        with open(temp_scad, 'w', encoding='utf-8') as f:
            f.write(openscad_code)
        
        # Executar OpenSCAD
        output_path = self._get_output_path(format, project_id)
        command = [
            'openscad',
            '-o', output_path,
            temp_scad
        ]
        
        result = subprocess.run(command, capture_output=True, text=True, timeout=30)
        
        # Limpar arquivo temporário
        if os.path.exists(temp_scad):
            os.remove(temp_scad)
        
        if result.returncode != 0:
            raise RuntimeError(f"Erro do OpenSCAD: {result.stderr}")
        
        logger.info(f"Modelo OpenSCAD gerado: {output_path}")
        return output_path
    
    async def generate_model_from_specs(self, db: Session, project_id: UUID, 
                                      specifications: Dict[str, Any]) -> Model3D:
        """
        Gerar modelo 3D a partir de especificações
        
        Args:
            db: Sessão do banco de dados
            project_id: ID do projeto
            specifications: Especificações extraídas da conversa
            
        Returns:
            Modelo 3D gerado
        """
        try:
            # Determinar engine de modelagem
            engine = self._select_modeling_engine(specifications)
            
            # Gerar arquivo 3D
            file_path, metadata = await self._generate_3d_file(
                engine, specifications, project_id
            )
            
            # Post-processar malha
            processed_mesh = await self._post_process_mesh(file_path, engine)
            
            # Validar imprimibilidade
            validation_result = await self._validate_printability(processed_mesh)
            
            # Criar registro no banco
            model = await self._create_model_record(
                db, project_id, specifications, file_path, metadata, 
                processed_mesh, validation_result, engine
            )
            
            return model
            
        except Exception as e:
            logger.error(f"Erro na geração de modelo: {e}")
            raise
    
    def _select_modeling_engine(self, specifications: Dict[str, Any]) -> str:
        """Selecionar engine de modelagem baseado nas especificações"""
        categoria = specifications.get("categoria", "mecanico")
        
        # Para modelos simples, usar OpenSCAD
        if categoria == "mecanico" and self._is_simple_geometric_shape(specifications):
            return "openscad"
        
        # Para modelos complexos, usar CadQuery
        return "cadquery"
    
    def _is_simple_geometric_shape(self, specs: Dict[str, Any]) -> bool:
        """Verificar se é uma forma geométrica simples"""
        # Lógica para detectar formas simples
        # Por enquanto, assumir formas simples se não há componentes eletrônicos
        return len(specs.get("componentes", [])) == 0
    
    async def _generate_3d_file(self, engine: str, specifications: Dict[str, Any], 
                              project_id: UUID) -> Tuple[Path, Dict[str, Any]]:
        """Gerar arquivo 3D usando engine selecionado"""
        if engine == "openscad":
            return await self._generate_with_openscad(specifications, project_id)
        else:
            return await self._generate_with_cadquery(specifications, project_id)
    
    async def _generate_with_openscad(self, specifications: Dict[str, Any], 
                                    project_id: UUID) -> Tuple[Path, Dict[str, Any]]:
        """Gerar modelo usando OpenSCAD"""
        # Gerar código OpenSCAD
        openscad_code = self._generate_openscad_code(specifications)
        
        # Criar arquivo temporário
        temp_scad = self.temp_path / f"{project_id}.scad"
        temp_scad.write_text(openscad_code, encoding='utf-8')
        
        # Executar OpenSCAD
        output_stl = self.storage_path / f"{project_id}.stl"
        cmd = [
            "openscad", 
            "-o", str(output_stl),
            str(temp_scad)
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            result.check_returncode()
            
            # Limpar arquivo temporário
            temp_scad.unlink()
            
            metadata = {
                "engine": "openscad",
                "source_code": openscad_code,
                "generation_time": 0,  # Implementar medição real
                "parameters": specifications
            }
            
            return output_stl, metadata
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Erro no OpenSCAD: {e.stderr}")
            raise Exception(f"Falha na geração OpenSCAD: {e.stderr}")
    
    async def _generate_with_cadquery(self, specifications: Dict[str, Any], 
                                    project_id: UUID) -> Tuple[Path, Dict[str, Any]]:
        """Gerar modelo usando CadQuery"""
        try:
            # Gerar geometria CadQuery
            geometry = self._generate_cadquery_geometry(specifications)
            
            # Exportar para STL
            output_stl = self.storage_path / f"{project_id}.stl"
            cq.exporters.export(geometry, str(output_stl), "STL")
            
            metadata = {
                "engine": "cadquery",
                "geometry_type": "cadquery_geometry",
                "generation_time": 0,  # Implementar medição real
                "parameters": specifications
            }
            
            return output_stl, metadata
            
        except Exception as e:
            logger.error(f"Erro no CadQuery: {e}")
            raise Exception(f"Falha na geração CadQuery: {e}")
    
    def _generate_openscad_code(self, specifications: Dict[str, Any]) -> str:
        """Gerar código OpenSCAD a partir das especificações"""
        # Código base
        code = "// Modelo gerado automaticamente pelo 3dPot v2.0\n"
        code += f"// Categoria: {specifications.get('categoria', 'mecanico')}\n\n"
        
        # Especificações físicas
        dimensoes = specifications.get("dimensoes", {})
        largura = dimensoes.get("largura", 50)
        altura = dimensoes.get("altura", 50)
        profundidade = dimensoes.get("profundidade", 50)
        
        # Material (para transparência)
        material = specifications.get("material", "PLA")
        transparency = self._get_material_transparency(material)
        
        # Gerar forma básica baseada na categoria
        categoria = specifications.get("categoria", "mecanico")
        
        if categoria == "mecanico":
            code += self._generate_mechanical_openscad(largura, altura, profundidade)
        elif categoria == "eletronico":
            code += self._generate_electronic_openscad(specifications)
        else:
            code += self._generate_generic_openscad(largura, altura, profundidade)
        
        # Adicionar componentes eletrônicos
        componentes = specifications.get("componentes", [])
        for componente in componentes:
            code += self._add_component_openscad(componente)
        
        # Aplicar material
        code += f"\n// Aplicar material\n"
        code += f"color([0.8, 0.2, 0.2, {transparency}]) {{\n"
        code += "    final_model = union();\n"
        code += "}\n"
        
        return code
    
    def _generate_mechanical_openscad(self, largura: float, altura: float, profundidade: float) -> str:
        """Gerar código OpenSCAD para aplicações mecânicas"""
        code = "// Modelo mecânico\n"
        
        # Verificar se há funcionalidades específicas
        funcionalidades = []  # Extrair das especificações
        
        if any("furo" in func.get("nome", "").lower() for func in funcionalidades):
            # Modelo com furos
            code += f"""
// Base com furos
difference() {{
    cube([{largura}, {profundidade}, {altura}]);
    
    // Furo central
    cylinder(h={altura*2}, d={min(largura, profundidade)*0.3}, center=true);
    
    // Furos laterais
    for(i=[-1,1]) {{
        translate([i*{largura*0.3}, 0, 0])
            cylinder(h={altura*2}, d={min(largura, profundidade)*0.15}, center=true);
    }}
}}
"""
        else:
            # Modelo sólido simples
            code += f"""
// Base sólida
cube([{largura}, {profundidade}, {altura}]);
"""
        
        return code
    
    def _generate_electronic_openscad(self, specifications: Dict[str, Any]) -> str:
        """Gerar código OpenSCAD para aplicações eletrônicas"""
        code = "// Modelo eletrônico\n"
        
        # Base para componentes
        dimensoes = specifications.get("dimensoes", {})
        largura = dimensoes.get("largura", 50)
        altura = dimensoes.get("altura", 20)
        profundidade = dimensoes.get("profundidade", 30)
        
        code += f"""
// PCB base
cube([{largura}, {profundidade}, {altura/4}]);

// Componentes eletrônicos (representação genérica)
color("gold") {{
    translate([-{largura/4}, -{profundidade/4}, {altura/4}])
        cube([{largura/2}, {profundidade/2}, {altura/2}]);
}}
"""
        
        return code
    
    def _generate_generic_openscad(self, largura: float, altura: float, profundidade: float) -> str:
        """Gerar código OpenSCAD genérico"""
        return f"""
// Modelo genérico
cube([{largura}, {profundidade}, {altura}]);
"""
    
    def _add_component_openscad(self, componente: Dict[str, Any]) -> str:
        """Adicionar componente ao modelo OpenSCAD"""
        tipo = componente.get("tipo", "generic")
        
        if tipo == "sensor":
            return """
// Sensor
color("blue") {
    cylinder(h=5, d=10);
}
"""
        elif tipo == "display":
            return """
// Display
color("black") {
    cube([20, 3, 15]);
}
"""
        else:
            return """
// Componente genérico
color("gray") {
    cube([10, 10, 5]);
}
"""
    
    def _get_material_transparency(self, material: str) -> float:
        """Obter transparência baseada no material"""
        material_map = {
            "PLA": 0.8,
            "ABS": 0.7,
            "PETG": 0.6,
            "nylon": 0.5,
            "metal": 1.0
        }
        return material_map.get(material.upper(), 0.8)
    
    def _generate_cadquery_geometry(self, specifications: Dict[str, Any]):
        """Gerar geometria CadQuery"""
        categoria = specifications.get("categoria", "mecanico")
        dimensoes = specifications.get("dimensoes", {})
        
        largura = dimensoes.get("largura", 50)
        altura = dimensoes.get("altura", 50)
        profundidade = dimensoes.get("profundidade", 50)
        
        if categoria == "mecanico":
            return self._generate_mechanical_cadquery(largura, altura, profundidade)
        else:
            # Padrão: cubo básico
            return cq.Workplane("XY").box(largura, profundidade, altura)
    
    def _generate_mechanical_cadquery(self, largura: float, altura: float, profundidade: float):
        """Gerar geometria mecânica CadQuery"""
        # Base com furos
        workplane = cq.Workplane("XY")
        
        # Base sólida
        base = workplane.box(largura, profundidade, altura)
        
        # Furo central (se aplicável)
        features = [base]
        
        # Adicionar furo central
        hole = workplane.center(0, 0).circle(min(largura, profundidade) * 0.3).extrude(altura * 2)
        result = base.union().cut(hole)
        
        return result
    
    async def _post_process_mesh(self, file_path: Path, engine: str) -> Trimesh:
        """Processar malha 3D com Trimesh"""
        try:
            # Carregar malha
            mesh = trimesh.load(str(file_path))
            
            if not isinstance(mesh, Trimesh):
                raise ValueError("Arquivo não contém uma malha válida")
            
            # Limpeza da malha
            mesh.remove_duplicate_faces()
            mesh.remove_degenerate_faces()
            mesh.remove_unreferenced_vertices()
            
            # Consertar problemas de manifold
            mesh.remove_small_components()
            
            return mesh
            
        except Exception as e:
            logger.error(f"Erro no pós-processamento da malha: {e}")
            raise
    
    async def _validate_printability(self, mesh: Trimesh) -> Dict[str, Any]:
        """Validar se o modelo é imprimível"""
        validation = {
            " imprimivel": True,
            "warnings": [],
            "errors": [],
            "metrics": {}
        }
        
        try:
            # Verificar se é manifold
            if not mesh.is_watertight:
                validation["errors"].append("Modelo não é manifold (vazios internos)")
                validation[" imprimivel"] = False
            
            # Verificar volume muito pequeno
            volume = mesh.volume
            if volume < 1.0:  # 1 mm³
                validation["warnings"].append("Volume muito pequeno (< 1 mm³)")
            
            # Verificar geometria muito fina
            bounding_box = mesh.bounds
            dimensions = bounding_box[1] - bounding_box[0]
            
            if dimensions[0] < 0.1 or dimensions[1] < 0.1 or dimensions[2] < 0.1:
                validation["warnings"].append("Dimensões muito pequenas (< 0.1mm)")
            
            # Verificar overhang (simplificado)
            if self._check_overhangs(mesh):
                validation["warnings"].append("Possível overhang - verificar ângulos")
            
            # Métricas
            validation["metrics"] = {
                "volume_mm3": volume,
                "surface_area_mm2": mesh.area,
                "vertices": len(mesh.vertices),
                "faces": len(mesh.faces),
                "dimensions_mm": {
                    "x": float(dimensions[0]),
                    "y": float(dimensions[1]),
                    "z": float(dimensions[2])
                }
            }
            
        except Exception as e:
            validation["errors"].append(f"Erro na validação: {str(e)}")
            validation[" imprimivel"] = False
        
        return validation
    
    def _check_overhangs(self, mesh: Trimesh) -> bool:
        """Verificação simplificada de overhangs"""
        # Implementação simplificada - expandir com algoritmo mais robusto
        normals = mesh.face_normals
        upside_down_faces = normals[:, 2] < -0.5  # Faces viradas para baixo
        return upside_down_faces.any()
    
    async def _create_model_record(self, db: Session, project_id: UUID, 
                                 specifications: Dict[str, Any], file_path: Path,
                                 metadata: Dict[str, Any], mesh: Trimesh,
                                 validation: Dict[str, Any], engine: str) -> Model3D:
        """Criar registro do modelo no banco de dados"""
        # Calcular métricas do arquivo
        file_size = file_path.stat().st_size
        
        model = Model3D(
            projeto_id=project_id,
            nome=f"Modelo_{project_id}",
            engine=engine,
            arquivo_path=str(file_path),
            arquivo_tamanho=file_size,
            formato_arquivo=".stl",
            parametros_geracao=metadata.get("parameters", {}),
            numero_vertices=len(mesh.vertices),
            numero_faces=len(mesh.faces),
            volume_calculado=float(mesh.volume),
            area_superficie=float(mesh.area),
            imprimavel=validation[" imprimivel"],
            erros_validacao=validation["errors"],
            warnings=validation["warnings"],
            otimizado=False,
            nvidia_nim_processado=False
        )
        
        db.add(model)
        db.commit()
        db.refresh(model)
        
        return model
    
    # Métodos auxiliares para o serviço de modelagem avançado
    def _apply_mechanical_specs_cadquery(self, model: cq.Workplane, specs: ModelingSpecs) -> cq.Workplane:
        """Aplica especificações para projetos mecânicos."""
        width = specs.dimensions.get('largura', 50.0)
        depth = specs.dimensions.get('profundidade', 50.0)
        height = specs.dimensions.get('altura', 50.0)
        
        # Furos nas bordas para fixação
        hole_radius = min(width, depth) / 20
        hole_positions = [
            (width/2 - hole_radius*2, depth/2 - hole_radius*2),
            (-width/2 + hole_radius*2, depth/2 - hole_radius*2),
            (width/2 - hole_radius*2, -depth/2 + hole_radius*2),
            (-width/2 + hole_radius*2, -depth/2 + hole_radius*2)
        ]
        
        # Adicionar furos
        for pos in hole_positions:
            model = model.faces(">Z").workplane().center(pos[0], pos[1]).circle(hole_radius).cutThruAll()
        
        return model
    
    def _apply_electronic_specs_cadquery(self, model: cq.Workplane, specs: ModelingSpecs) -> cq.Workplane:
        """Aplica especificações para projetos eletrônicos."""
        width = specs.dimensions.get('largura', 50.0)
        depth = specs.dimensions.get('profundidade', 50.0)
        height = specs.dimensions.get('altura', 20.0)
        
        # Grid de furos para ventilação
        grid_spacing = 10.0
        hole_radius = 2.0
        
        for x in range(-int(width/2) + 10, int(width/2) - 10, int(grid_spacing)):
            for z in range(-int(depth/2) + 10, int(depth/2) - 10, int(grid_spacing)):
                model = model.faces(">Y").workplane().center(x, z).circle(hole_radius).cutThruAll()
        
        return model
    
    def _apply_architectural_specs_cadquery(self, model: cq.Workplane, specs: ModelingSpecs) -> cq.Workplane:
        """Aplica especificações para projetos de arquitetura."""
        width = specs.dimensions.get('largura', 100.0)
        depth = specs.dimensions.get('profundidade', 100.0)
        height = specs.dimensions.get('altura', 100.0)
        
        # Adicionar base reforçada
        base_thickness = height / 10
        model = model.faces("<Z").workplane().offset(base_thickness).rect(width, depth).extrude(base_thickness)
        
        return model
    
    def _apply_features_cadquery(self, model: cq.Workplane, features: List[Dict[str, Any]]) -> cq.Workplane:
        """Aplica funcionalidades específicas."""
        for feature in features:
            feature_type = feature.get("tipo", "")
            feature_name = feature.get("nome", "").lower()
            
            if "furo" in feature_name:
                # Adicionar furo específico
                radius = feature.get("diametro", 5.0) / 2
                position = feature.get("posicao", {"x": 0, "y": 0})
                model = model.faces(">Z").workplane().center(
                    position.get("x", 0), position.get("y", 0)
                ).circle(radius).cutThruAll()
            
            elif "suporte" in feature_name:
                # Adicionar suporte
                height = feature.get("altura", 10.0)
                radius = feature.get("raio", 3.0)
                position = feature.get("posicao", {"x": 0, "y": 0})
                model = model.faces("<Z").workplane().center(
                    position.get("x", 0), position.get("y", 0)
                ).circle(radius).extrude(height)
        
        return model
    
    def _generate_feature_openscad(self, feature: Dict[str, Any]) -> str:
        """Gera código para funcionalidades específicas."""
        feature_type = feature.get("tipo", "")
        feature_name = feature.get("nome", "").lower()
        
        if "furo" in feature_name:
            radius = feature.get("diametro", 5.0) / 2
            height = feature.get("altura", 50.0)
            position = feature.get("posicao", {"x": 0, "y": 0})
            return f"""
// Furo específico
translate([{position.get("x", 0)}, {position.get("y", 0)}, 0])
    cylinder(h={height}, r={radius}, center=true);
"""
        
        elif "suporte" in feature_name:
            height = feature.get("altura", 10.0)
            radius = feature.get("raio", 3.0)
            position = feature.get("posicao", {"x": 0, "y": 0})
            return f"""
// Suporte específico
translate([{position.get("x", 0)}, {position.get("y", 0)}, -{height/2}])
    cylinder(h={height}, r={radius});
"""
        
        return f"// Funcionalidade não implementada: {feature.get('nome', 'desconhecida')}\n"
    
    def get_available_engines(self) -> List[str]:
        """Lista engines de modelagem disponíveis."""
        return [engine.value for engine, available in self._available_engines.items() if available]
    
    def get_supported_formats(self, engine: str) -> List[str]:
        """Lista formatos suportados por um engine."""
        engine_enum = ModelingEngine(engine) if engine in [e.value for e in ModelingEngine] else None
        if engine_enum == ModelingEngine.CADQUERY:
            return [fmt.value for fmt in [ModelFormat.STL, ModelFormat.OBJ, ModelFormat.STEP]]
        elif engine_enum == ModelingEngine.OPENSCAD:
            return [ModelFormat.STL.value]
        else:
            return []


# Instância global do serviço
_modeling_service_instance = None


def get_modeling_service() -> ModelingService:
    """Obtém instância global do serviço de modelagem."""
    global _modeling_service_instance
    if _modeling_service_instance is None:
        _modeling_service_instance = ModelingService()
    return _modeling_service_instance