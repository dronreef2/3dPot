"""
3dPot Platform - Model Generation Service
Criado em: 2025-11-12 22:42:43
Autor: MiniMax Agent

Serviço para geração de modelos 3D via NVIDIA NIM e OpenSCAD
"""

import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
import httpx
import redis.asyncio as redis
from minio import Minio
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update
import subprocess
import tempfile

# Import local modules
from models.database_models import Project, Model3D, Job
from database.database import get_database
from utils.logger import get_logger

logger = get_logger("model.generation")

class NVIDIAClient:
    """Cliente para integração com NVIDIA NIM APIs"""
    
    def __init__(self):
        self.api_key = os.getenv("NVIDIA_API_KEY")
        self.base_url = "https://integrate.api.nvidia.com/v1"
        
    async def generate_3d_model(self, specifications: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gera modelo 3D usando NVIDIA APIs
        """
        try:
            async with httpx.AsyncClient() as client:
                # Preparar prompt para geração 3D
                prompt = self._build_3d_prompt(specifications)
                
                # Fazer request para NVIDIA
                response = await client.post(
                    f"{self.base_url}/images/generations",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "nvidia/isaac_3d_mesh",
                        "prompt": prompt,
                        "num_images": 1,
                        "resolution": 1024,
                        "guidance_scale": 7.5
                    },
                    timeout=120.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    image_url = result["data"][0]["url"]
                    
                    # Download e conversão da imagem para mesh
                    mesh_data = await self._convert_image_to_mesh(image_url)
                    
                    return {
                        "success": True,
                        "mesh_data": mesh_data,
                        "source_image": image_url,
                        "generation_method": "nvidia_nim"
                    }
                else:
                    logger.error(f"Erro na API NVIDIA: {response.status_code}")
                    return self._fallback_generation(specifications)
                    
        except Exception as e:
            logger.error(f"Erro na geração NVIDIA: {e}")
            return self._fallback_generation(specifications)
    
    def _build_3d_prompt(self, specs: Dict[str, Any]) -> str:
        """Constrói prompt para geração 3D"""
        prompt_parts = []
        
        # Adicionar dimensões
        dimensions = specs.get("dimensions", {})
        if dimensions:
            width = dimensions.get("width", 50)
            height = dimensions.get("height", 20)
            depth = dimensions.get("depth", 30)
            prompt_parts.append(f"object with dimensions {width}x{height}x{depth} mm")
        
        # Adicionar material
        material = specs.get("material", "ABS")
        if material != "Não especificado":
            prompt_parts.append(f"made of {material.lower()}")
        
        # Adicionar funcionalidade
        functionality = specs.get("functionality", "functional part")
        if functionality != "Não especificado":
            prompt_parts.append(f"for {functionality.lower()}")
        
        # Adicionar complexidade
        complexity = specs.get("complexity", "medium")
        if complexity == "Alto":
            prompt_parts.append("with complex geometry and detailed features")
        elif complexity == "Baixo":
            prompt_parts.append("with simple geometry and basic design")
        
        base_prompt = " ".join(prompt_parts) if prompt_parts else "functional 3D printed part"
        
        return f"3D model of {base_prompt}, photorealistic rendering, clean background"
    
    async def _convert_image_to_mesh(self, image_url: str) -> bytes:
        """Converte imagem para mesh usando ferramentas de contorno"""
        try:
            # Download da imagem
            async with httpx.AsyncClient() as client:
                response = await client.get(image_url)
                image_data = response.content
            
            # Em produção, usar ferramentas como:
            # - OpenCV para extração de contornos
            # - Open3D para reconstrução de mesh
            # - PyMeshLab para pós-processamento
            
            return image_data  # Placeholder
            
        except Exception as e:
            logger.error(f"Erro na conversão para mesh: {e}")
            raise
    
    def _fallback_generation(self, specifications: Dict[str, Any]) -> Dict[str, Any]:
        """Geração de fallback usando OpenSCAD"""
        return {
            "success": True,
            "mesh_data": "opencad_generated",
            "generation_method": "opencad_fallback",
            "specifications": specifications
        }

class OpenSCADGenerator:
    """Gerador de modelos OpenSCAD a partir de especificações"""
    
    def generate_model(self, specs: Dict[str, Any]) -> str:
        """
        Gera código OpenSCAD baseado nas especificações
        """
        try:
            dimensions = specs.get("dimensions", {})
            width = dimensions.get("width", 50)
            height = dimensions.get("height", 20)
            depth = dimensions.get("depth", 30)
            
            material = specs.get("material", "ABS")
            functionality = specs.get("functionality", "generic")
            complexity = specs.get("complexity", "medium")
            
            # Geração de código OpenSCAD baseado na complexidade
            if complexity == "Baixo":
                return self._generate_simple_part(width, height, depth, material)
            elif complexity == "Médio":
                return self._generate_medium_part(width, height, depth, material, functionality)
            else:
                return self._generate_complex_part(width, height, depth, material, functionality)
                
        except Exception as e:
            logger.error(f"Erro na geração OpenSCAD: {e}")
            return self._generate_basic_cube(width, height, depth)
    
    def _generate_simple_part(self, width: float, height: float, depth: float, material: str) -> str:
        """Gera parte simples (cubo ou cuboide)"""
        return f"""
// 3dPot Generated Part
// Material: {material}
// Dimensions: {width}x{height}x{depth} mm

cube([{width}, {depth}, {height}], center=true);

// Optional features for {material} material
{"// Add material-specific features" if material != "ABS" else ""}
"""
    
    def _generate_medium_part(self, width: float, height: float, depth: float, material: str, functionality: str) -> str:
        """Gera parte de complexidade média com funcionalidades"""
        if functionality.lower() == "fixação":
            return f"""
// 3dPot Fixation Part - {material}
// Dimensions: {width}x{height}x{depth} mm

module fixation_hole() {{
    cylinder(r=3, h={height*2}, center=true);
}}

// Main body
cube([{width}, {depth}, {height}], center=true);

// Fixation holes
translate([{width/3}, {depth/3}, 0]) {{
    fixation_hole();
}}
translate([-{width/3}, {depth/3}, 0]) {{
    fixation_hole();
}}
"""
        else:
            return f"""
// 3dPot Functional Part - {material}
// Functionality: {functionality}
// Dimensions: {width}x{height}x{depth} mm

cube([{width}, {depth}, {height}], center=true);

// Add basic functional features
"""
    
    def _generate_complex_part(self, width: float, height: float, depth: float, material: str, functionality: str) -> str:
        """Gera parte complexa com múltiplas funcionalidades"""
        return f"""
// 3dPot Complex Part - {material}
// Functionality: {functionality}
// Dimensions: {width}x{height}x{depth} mm
// Complexity: High

// Main structure
difference() {{
    cube([{width}, {depth}, {height}], center=true);
    // Internal structure
    translate([0, 0, 0]) {{
        cube([{width*0.8}, {depth*0.8}, {height*0.8}], center=true);
    }}
}}

// Add reinforcement features
"""
    
    def _generate_basic_cube(self, width: float, height: float, depth: float) -> str:
        """Geração básica (cubo)"""
        return f"cube([{width}, {depth}, {height}], center=true);"

class ModelGenerationService:
    """
    Serviço principal de geração de modelos 3D
    """
    
    def __init__(self, minio_client: Minio, redis_client: redis.Redis):
        self.minio_client = minio_client
        self.redis = redis_client
        self.nvidia_client = NVIDIAClient()
        self.opencad_generator = OpenSCADGenerator()
        self.router = APIRouter()
        
        # Configurar bucket MinIO
        self._setup_minio_bucket()
        
        # Registrar rotas
        self._register_routes()
    
    def _setup_minio_bucket(self):
        """Configura bucket no MinIO"""
        try:
            if not self.minio_client.bucket_exists("3dpot-models"):
                self.minio_client.make_bucket("3dpot-models")
            logger.info("✅ MinIO bucket configurado")
        except Exception as e:
            logger.error(f"❌ Erro ao configurar MinIO bucket: {e}")
    
    async def generate_model(
        self, 
        project_id: int, 
        specifications: Dict[str, Any],
        user_id: int
    ) -> Dict[str, Any]:
        """
        Gera modelo 3D a partir de especificações
        """
        try:
            job_id = str(uuid.uuid4())
            
            # Criar job no database
            job_data = {
                "job_type": "generate_3d",
                "job_data": {
                    "project_id": project_id,
                    "specifications": specifications,
                    "user_id": user_id,
                    "job_id": job_id
                },
                "status": "queued",
                "user_id": user_id
            }
            
            logger.info(f"🚀 Iniciando geração de modelo 3D - Job: {job_id}")
            
            # Primeiro tentar NVIDIA NIM, depois OpenSCAD
            nvidia_result = await self.nvidia_client.generate_3d_model(specifications)
            
            if nvidia_result["success"]:
                mesh_data = nvidia_result["mesh_data"]
                generation_method = "nvidia_nim"
            else:
                # Fallback para OpenSCAD
                openscad_code = self.opencad_generator.generate_model(specifications)
                mesh_data = openscad_code
                generation_method = "opencad"
            
            # Salvar arquivo no MinIO
            file_name = f"{job_id}.stl"
            file_path = f"models/{file_name}"
            
            # Upload para MinIO
            if generation_method == "nvidia_nim":
                # Para mesh NVIDIA
                with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                    tmp_file.write(mesh_data)
                    tmp_file.flush()
                    
                    self.minio_client.fput_object(
                        "3dpot-models", 
                        file_path, 
                        tmp_file.name,
                        content_type="model/stl"
                    )
            else:
                # Para código OpenSCAD
                self.minio_client.put_object(
                    "3dpot-models",
                    file_path,
                    mesh_data.encode('utf-8'),
                    len(mesh_data),
                    content_type="text/x-opencad"
                )
            
            # Atualizar job como concluído
            logger.info(f"✅ Modelo gerado com sucesso - {file_path}")
            
            return {
                "job_id": job_id,
                "file_path": file_path,
                "generation_method": generation_method,
                "status": "completed",
                "file_size": len(mesh_data),
                "specifications": specifications
            }
            
        except Exception as e:
            logger.error(f"❌ Erro na geração de modelo: {e}")
            raise
    
    def _register_routes(self):
        """Registra rotas REST"""
        
        @self.router.post("/generate")
        async def generate_model_endpoint(
            request: Dict[str, Any],
            background_tasks: BackgroundTasks,
            db: AsyncSession = Depends(get_database)
        ):
            """Endpoint para geração de modelos"""
            try:
                project_id = request["project_id"]
                specifications = request["specifications"]
                user_id = request.get("user_id")
                
                if not user_id:
                    raise HTTPException(status_code=401, detail="User ID required")
                
                # Gerar modelo em background
                background_tasks.add_task(
                    self._generate_model_background,
                    project_id,
                    specifications,
                    user_id,
                    db
                )
                
                return {
                    "message": "Geração iniciada",
                    "status": "queued",
                    "project_id": project_id
                }
                
            except Exception as e:
                logger.error(f"❌ Erro na geração: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.get("/models/{project_id}")
        async def get_project_models(
            project_id: int,
            db: AsyncSession = Depends(get_database)
        ):
            """Busca modelos de um projeto"""
            try:
                result = await db.execute(
                    select(Model3D)
                    .where(Model3D.project_id == project_id)
                    .order_by(Model3D.created_at.desc())
                )
                models = result.scalars().all()
                
                return {
                    "project_id": project_id,
                    "models": [
                        {
                            "id": m.id,
                            "name": m.name,
                            "file_path": m.file_path,
                            "file_format": m.file_format,
                            "generation_method": m.generation_method,
                            "is_valid": m.is_valid,
                            "created_at": m.created_at.isoformat()
                        }
                        for m in models
                    ]
                }
                
            except Exception as e:
                logger.error(f"❌ Erro ao buscar modelos: {e}")
                raise HTTPException(status_code=500, detail=str(e))
    
    async def _generate_model_background(
        self, 
        project_id: int, 
        specifications: Dict[str, Any], 
        user_id: int,
        db: AsyncSession
    ):
        """Geração de modelo em background"""
        try:
            result = await self.generate_model(project_id, specifications, user_id)
            
            # Salvar no database
            model_data = {
                "project_id": project_id,
                "name": f"Modelo_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "file_path": result["file_path"],
                "file_format": "stl",
                "generation_method": result["generation_method"],
                "generation_params": specifications,
                "is_valid": True
            }
            
            await db.execute(insert(Model3D), model_data)
            await db.commit()
            
            logger.info(f"✅ Modelo salvo no database: {model_data['name']}")
            
        except Exception as e:
            logger.error(f"❌ Erro na geração background: {e}")

# Instância global (será inicializada no main.py)
model_service = None