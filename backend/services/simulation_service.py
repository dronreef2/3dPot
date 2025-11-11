"""
Serviço de Simulação Física - PyBullet
Testes de queda, stress, movimento e fluidos
"""

import json
import logging
import os
import time
import tempfile
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union
from uuid import UUID
from datetime import datetime

import numpy as np
import pybullet as p
import trimesh
from sqlalchemy.orm import Session
import redis
import pickle

from ..core.config import MODELS_STORAGE_PATH, TEMP_STORAGE_PATH, REDIS_URL
from ..models import Simulation, Model3D
from ..schemas import SimulationCreate

logger = logging.getLogger(__name__)

class SimulationService:
    """Serviço para simulação física com PyBullet"""
    
    def __init__(self):
        self.storage_path = MODELS_STORAGE_PATH
        self.temp_path = TEMP_STORAGE_PATH
        self.redis_client = None
        
        # Garantir que os diretórios existam
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.temp_path.mkdir(parents=True, exist_ok=True)
        
        # Inicializar Redis
        self._initialize_redis()
        
        # Configurações de simulação
        self.simulation_configs = {
            "drop_test": {
                "default_height": 1.0,
                "max_height": 5.0,
                "default_drops": 5,
                "max_drops": 20,
                "gravity": -9.8,
                "max_time": 10.0
            },
            "stress_test": {
                "default_max_force": 1000,
                "max_force": 10000,
                "default_increment": 100,
                "max_increment": 1000
            },
            "motion_test": {
                "default_duration": 10.0,
                "max_duration": 60.0,
                "default_velocity": 1.0,
                "max_velocity": 10.0,
                "trajectory_types": ["circular", "linear", "figure_8"]
            },
            "fluid_test": {
                "default_density": 1.2,  # kg/m³ (ar)
                "max_density": 1000.0,  # kg/m³ (água)
                "default_coefficient": 0.47,
                "max_coefficient": 1.2
            }
        }
    
    def _initialize_redis(self):
        """Inicializar cliente Redis para cache"""
        try:
            self.redis_client = redis.from_url(REDIS_URL, decode_responses=False)
            # Teste de conexão
            self.redis_client.ping()
            logger.info("Redis conectado com sucesso")
        except Exception as e:
            logger.warning(f"Redis não disponível: {e}. Cache desabilitado.")
            self.redis_client = None
    
    def _get_cache_key(self, model_path: str, simulation_type: str, parameters: Dict) -> str:
        """Gerar chave de cache para simulação"""
        param_str = json.dumps(parameters, sort_keys=True)
        content_hash = hashlib.md5(f"{model_path}{param_str}".encode()).hexdigest()
        return f"simulation:{simulation_type}:{content_hash}"
    
    def _cache_result(self, cache_key: str, result: Dict[str, Any], ttl: int = 3600):
        """Cachear resultado da simulação"""
        if self.redis_client:
            try:
                serialized_result = pickle.dumps(result)
                self.redis_client.setex(cache_key, ttl, serialized_result)
                logger.debug(f"Resultado cacheado: {cache_key}")
            except Exception as e:
                logger.warning(f"Erro ao cachear resultado: {e}")
    
    def _get_cached_result(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Recuperar resultado do cache"""
        if self.redis_client:
            try:
                cached_data = self.redis_client.get(cache_key)
                if cached_data:
                    result = pickle.loads(cached_data)
                    logger.debug(f"Resultado recuperado do cache: {cache_key}")
                    return result
            except Exception as e:
                logger.warning(f"Erro ao recuperar cache: {e}")
        return None
    
    async def start_simulation(self, db: Session, simulation_data: SimulationCreate) -> Simulation:
        """
        Iniciar nova simulação física
        
        Args:
            db: Sessão do banco de dados
            simulation_data: Dados da simulação
            
        Returns:
            Registro da simulação criada
        """
        try:
            # Verificar se modelo 3D existe
            model_3d = db.query(Model3D).filter(Model3D.id == simulation_data.modelo_3d_id).first()
            if not model_3d:
                raise ValueError("Modelo 3D não encontrado")
            
            # Criar registro da simulação
            simulation = Simulation(
                modelo_3d_id=simulation_data.modelo_3d_id,
                nome=simulation_data.nome,
                tipo_simulacao=simulation_data.tipo_simulacao,
                parametros=simulation_data.parametros,
                condicoes_iniciais=simulation_data.condicoes_iniciais,
                status="pending"
            )
            
            db.add(simulation)
            db.commit()
            db.refresh(simulation)
            
            # Iniciar simulação em background (implementar Celery)
            await self._run_simulation_async(simulation.id, model_3d, simulation_data)
            
            return simulation
            
        except Exception as e:
            logger.error(f"Erro ao iniciar simulação: {e}")
            db.rollback()
            raise
    
    async def _run_simulation_async(self, simulation_id: UUID, model_3d: Model3D, 
                                  simulation_data: SimulationCreate):
        """Executar simulação de forma assíncrona"""
        try:
            # Esta função será executada via Celery em produção
            # Por enquanto, executar sincronamente para demonstração
            
            result = await self._execute_simulation(
                simulation_id, model_3d, simulation_data
            )
            
            # Atualizar resultado (implementar via Celery callback)
            # update_simulation_result.delay(simulation_id, result)
            
        except Exception as e:
            logger.error(f"Erro na simulação {simulation_id}: {e}")
            # update_simulation_status.delay(simulation_id, "failed", str(e))
    
    async def _execute_simulation(self, simulation_id: UUID, model_3d: Model3D, 
                                simulation_data: SimulationCreate) -> Dict[str, Any]:
        """Executar simulação específica"""
        tipo = simulation_data.tipo_simulacao
        
        if tipo == "drop_test":
            return await self._run_drop_test(simulation_id, model_3d, simulation_data)
        elif tipo == "stress_test":
            return await self._run_stress_test(simulation_id, model_3d, simulation_data)
        elif tipo == "motion":
            return await self._run_motion_test(simulation_id, model_3d, simulation_data)
        elif tipo == "fluid":
            return await self._run_fluid_test(simulation_id, model_3d, simulation_data)
        else:
            raise ValueError(f"Tipo de simulação não suportado: {tipo}")
    
    async def _run_drop_test(self, simulation_id: UUID, model_3d: Model3D, 
                           simulation_data: SimulationCreate) -> Dict[str, Any]:
        """Executar teste de queda"""
        try:
            # Inicializar PyBullet
            physics_client = self._initialize_pybullet()
            
            # Carregar modelo 3D
            model_path = Path(model_3d.arquivo_path)
            body_id = self._load_3d_model_to_pybullet(model_path, physics_client)
            
            # Configurar parâmetros do teste
            drop_height = simulation_data.parametros.get("drop_height", 1.0)  # metros
            num_drops = simulation_data.parametros.get("num_drops", 10)
            gravity = -9.8
            
            results = {
                "tipo": "drop_test",
                "testes": [],
                "metricas": {},
                "duracao_total": 0
            }
            
            start_time = time.time()
            
            for drop_num in range(num_drops):
                # Resetar posição do objeto
                p.resetBasePositionAndOrientation(body_id, [0, 0, drop_height], [0, 0, 0, 1])
                p.resetBaseVelocity(body_id, [0, 0, 0], [0, 0, 0])
                
                # Definir gravidade
                p.setGravity(0, 0, gravity)
                
                # Simular queda
                velocities = []
                positions = []
                collision_points = []
                
                simulation_time = 0
                dt = 1/240  # 240 Hz
                
                while simulation_time < 5.0:  # 5 segundos max
                    # Simular física
                    p.stepSimulation()
                    simulation_time += dt
                    
                    # Coletar dados
                    pos, orn = p.getBasePositionAndOrientation(body_id)
                    vel, ang_vel = p.getBaseVelocity(body_id)
                    
                    velocities.append(vel)
                    positions.append(pos)
                    
                    # Detectar contato com solo
                    contact_points = p.getContactPoints(body_id, -1)
                    if contact_points and not collision_points:
                        collision_points.append({
                            "time": simulation_time,
                            "position": pos,
                            "velocity": vel
                        })
                    
                    # Parar se objeto parar de se mover
                    if len(velocities) > 60:  # 1/4 de segundo
                        recent_vel = velocities[-10:]
                        if all(abs(v[2]) < 0.1 for v in recent_vel):  # Velocidade Z baixa
                            break
                
                # Analisar resultado do teste
                teste_resultado = self._analyze_drop_test(
                    drop_num, positions, velocities, collision_points
                )
                results["testes"].append(teste_resultado)
            
            # Calcular métricas gerais
            results["metricas"] = self._calculate_drop_test_metrics(results["testes"])
            results["duracao_total"] = time.time() - start_time
            
            # Limpar
            p.disconnect(physics_client)
            
            return results
            
        except Exception as e:
            logger.error(f"Erro no teste de queda: {e}")
            raise
    
    async def _run_stress_test(self, simulation_id: UUID, model_3d: Model3D, 
                             simulation_data: SimulationCreate) -> Dict[str, Any]:
        """Executar teste de stress/pressão"""
        try:
            physics_client = self._initialize_pybullet()
            
            model_path = Path(model_3d.arquivo_path)
            body_id = self._load_3d_model_to_pybullet(model_path, physics_client)
            
            # Configurar teste
            max_force = simulation_data.parametros.get("max_force", 1000)  # N
            force_direction = simulation_data.parametros.get("force_direction", [0, 0, 1])
            force_increment = simulation_data.parametros.get("force_increment", 100)
            
            results = {
                "tipo": "stress_test",
                "testes_forca": [],
                "metricas": {},
                "ponto_ruptura": None
            }
            
            current_force = 0
            while current_force <= max_force:
                # Resetar posição
                p.resetBasePositionAndOrientation(body_id, [0, 0, 0.5], [0, 0, 0, 1])
                p.resetBaseVelocity(body_id, [0, 0, 0], [0, 0, 0])
                
                # Aplicar força crescente
                force = [f * current_force for f in force_direction]
                p.applyExternalForce(body_id, -1, force, [0, 0, 0], p.LINK_FRAME)
                
                # Simular por um tempo
                for _ in range(240):  # 1 segundo
                    p.stepSimulation()
                
                # Coletar resultado
                pos, orn = p.getBasePositionAndOrientation(body_id)
                vel, ang_vel = p.getBaseVelocity(body_id)
                
                # Verificar se houve ruptura/deformação excessiva
                displacement = np.linalg.norm(np.array(pos))
                
                teste_result = {
                    "forca": current_force,
                    "posicao_final": pos,
                    "velocidade_final": vel,
                    "deslocamento": displacement
                }
                
                results["testes_forca"].append(teste_result)
                
                # Verificar ruptura (deslocamento excessivo)
                if displacement > 0.5:  # 50cm
                    results["ponto_ruptura"] = current_force
                    break
                
                current_force += force_increment
            
            results["metricas"] = self._calculate_stress_test_metrics(results)
            
            p.disconnect(physics_client)
            
            return results
            
        except Exception as e:
            logger.error(f"Erro no teste de stress: {e}")
            raise
    
    async def _run_motion_test(self, simulation_id: UUID, model_3d: Model3D, 
                             simulation_data: SimulationCreate) -> Dict[str, Any]:
        """Executar teste de movimento/dinâmica"""
        try:
            physics_client = self._initialize_pybullet()
            
            model_path = Path(model_3d.arquivo_path)
            body_id = self._load_3d_model_to_pybullet(model_path, physics_client)
            
            # Configurar trajetória
            trajectory_type = simulation_data.parametros.get("trajectory_type", "circular")
            duration = simulation_data.parametros.get("duration", 10.0)  # segundos
            velocity = simulation_data.parametros.get("velocity", 1.0)  # m/s
            
            results = {
                "tipo": "motion_test",
                "trajetoria": [],
                "metricas": {},
                "energia_consumida": 0
            }
            
            # Definir trajetória
            if trajectory_type == "circular":
                radius = 1.0  # metros
                angular_velocity = velocity / radius
                trajectory_points = self._generate_circular_trajectory(
                    radius, angular_velocity, duration
                )
            else:
                # Trajetória linear
                trajectory_points = self._generate_linear_trajectory(
                    velocity, duration
                )
            
            # Simular movimento
            total_energy = 0
            for i, target_pos in enumerate(trajectory_points):
                # Mover objeto para posição alvo
                p.resetBasePositionAndOrientation(body_id, target_pos, [0, 0, 0, 1])
                
                # Calcular energia potencial
                mass = p.getDynamicsInfo(body_id, -1)[0]
                potential_energy = mass * 9.8 * target_pos[2]
                
                total_energy += potential_energy
                
                results["trajetoria"].append({
                    "tempo": i * 0.1,
                    "posicao": target_pos,
                    "energia_potencial": potential_energy
                })
                
                # Simular física por um pequeno intervalo
                for _ in range(24):  # 0.1 segundos a 240 Hz
                    p.stepSimulation()
            
            results["metricas"]["energia_total"] = total_energy
            results["metricas"]["distancia_percorrida"] = self._calculate_distance(trajectory_points)
            results["metricas"]["velocidade_media"] = velocity
            
            p.disconnect(physics_client)
            
            return results
            
        except Exception as e:
            logger.error(f"Erro no teste de movimento: {e}")
            raise
    
    async def _run_fluid_test(self, simulation_id: UUID, model_3d: Model3D, 
                            simulation_data: SimulationCreate) -> Dict[str, Any]:
        """Executar teste de fluido (simplificado)"""
        # Nota: PyBullet tem suporte limitado para fluidos
        # Esta implementação simula efeitos básicos de fluido
        
        try:
            physics_client = self._initialize_pybullet()
            
            model_path = Path(model_3d.arquivo_path)
            body_id = self._load_3d_model_to_pybullet(model_path, physics_client)
            
            # Configurar "fluido" como resistência do ar
            fluid_density = simulation_data.parametros.get("fluid_density", 1.2)  # kg/m³
            drag_coefficient = simulation_data.parametros.get("drag_coefficient", 0.47)
            
            results = {
                "tipo": "fluid_test",
                "resistencia": [],
                "metricas": {}
            }
            
            # Simular queda com resistência do ar
            p.resetBasePositionAndOrientation(body_id, [0, 0, 10], [0, 0, 0, 1])
            p.resetBaseVelocity(body_id, [0, 0, 0], [0, 0, 0])
            
            terminal_velocity = 0
            velocities = []
            
            for _ in range(2400):  # 10 segundos
                p.stepSimulation()
                
                pos, orn = p.getBasePositionAndOrientation(body_id)
                vel, ang_vel = p.getBaseVelocity(body_id)
                velocities.append(vel)
                
                # Calcular resistência do ar
                if vel[2] != 0:
                    force_drag = self._calculate_drag_force(
                        vel, fluid_density, drag_coefficient, body_id
                    )
                    
                    results["resistencia"].append({
                        "velocidade": vel[2],
                        "forca_arrasto": force_drag
                    })
                    
                    # Verificar velocidade terminal
                    if abs(vel[2]) > terminal_velocity:
                        terminal_velocity = abs(vel[2])
            
            results["metricas"]["velocidade_terminal"] = terminal_velocity
            results["metricas"]["coeficiente_arrasto"] = drag_coefficient
            
            p.disconnect(physics_client)
            
            return results
            
        except Exception as e:
            logger.error(f"Erro no teste de fluido: {e}")
            raise
    
    def _initialize_pybullet(self):
        """Inicializar cliente PyBullet"""
        try:
            # Usar DIRECT para simulação sem interface gráfica
            physics_client = p.connect(p.DIRECT)
            p.setGravity(0, 0, -9.8)
            return physics_client
        except Exception as e:
            logger.error(f"Erro ao inicializar PyBullet: {e}")
            raise
    
    def _load_3d_model_to_pybullet(self, model_path: Path, physics_client) -> int:
        """Carregar modelo 3D no PyBullet"""
        try:
            # PyBullet suporta formatos URDF, SDF, MJCF
            # Para STL, precisamos converter ou usar mesh shape
            
            # Usar createMeshShape para carregar STL
            import meshcat
            import trimesh
            
            # Carregar malha
            mesh = trimesh.load(str(model_path))
            
            # Criar shape de colisão
            vertices = mesh.vertices.flatten().tolist()
            faces = mesh.faces.flatten().tolist()
            
            body_id = p.createCollisionShape(
                p.GEOM_MESH,
                vertices=vertices,
                indices=faces
            )
            
            # Criar corpo físico
            mass = 1.0  # massa padrão de 1kg
            body_id = p.createMultiBody(
                baseMass=mass,
                baseCollisionShapeIndex=body_id,
                basePosition=[0, 0, 1],
                baseOrientation=[0, 0, 0, 1]
            )
            
            return body_id
            
        except Exception as e:
            logger.error(f"Erro ao carregar modelo no PyBullet: {e}")
            raise
    
    def _analyze_drop_test(self, drop_num: int, positions: List, velocities: List, 
                          collision_points: List) -> Dict[str, Any]:
        """Analisar resultado de um teste de queda"""
        if not collision_points:
            return {
                "numero_teste": drop_num,
                "altura_queda": positions[0][2],
                "velocidade_impacto": velocities[0][2],
                "rebotes": 0,
                "tempo_ate_repouso": 0
            }
        
        collision = collision_points[0]
        
        # Contar rebotes (simplificado)
        rebotes = 0
        for i, vel in enumerate(velocities):
            if i > len(velocities) // 2 and abs(vel[2]) > 1.0:
                rebotes += 1
        
        return {
            "numero_teste": drop_num,
            "altura_queda": positions[0][2],
            "velocidade_impacto": collision["velocity"][2],
            "tempo_impacto": collision["time"],
            "posicao_impacto": collision["position"],
            "rebotes": rebotes,
            "tempo_ate_repouso": len(velocities) * (1/240)
        }
    
    def _calculate_drop_test_metrics(self, testes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calcular métricas do teste de queda"""
        if not testes:
            return {}
        
        impactos = [t["velocidade_impacto"] for t in testes]
        rebotes = [t["rebotes"] for t in testes]
        
        return {
            "velocidade_impacto_media": np.mean(impactos),
            "velocidade_impacto_max": np.max(impactos),
            "velocidade_impacto_min": np.min(impactos),
            "rebotes_medio": np.mean(rebotes),
            "numero_testes": len(testes)
        }
    
    def _calculate_stress_test_metrics(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Calcular métricas do teste de stress"""
        testes = results["testes_forca"]
        if not testes:
            return {}
        
        forcas = [t["forca"] for t in testes]
        deslocamentos = [t["deslocamento"] for t in testes]
        
        return {
            "forca_maxima": max(forcas),
            "deslocamento_maximo": max(deslocamentos),
            "rigidez_aproximada": forcas[-1] / deslocamentos[-1] if deslocamentos[-1] > 0 else 0,
            "ponto_ruptura": results["ponto_ruptura"]
        }
    
    def _generate_circular_trajectory(self, radius: float, angular_velocity: float, 
                                    duration: float) -> List[List[float]]:
        """Gerar trajetória circular"""
        trajectory = []
        time_points = np.arange(0, duration, 0.1)
        
        for t in time_points:
            x = radius * np.cos(angular_velocity * t)
            y = radius * np.sin(angular_velocity * t)
            z = 1.0  # altura constante
            trajectory.append([x, y, z])
        
        return trajectory
    
    def _generate_linear_trajectory(self, velocity: float, duration: float) -> List[List[float]]:
        """Gerar trajetória linear"""
        trajectory = []
        time_points = np.arange(0, duration, 0.1)
        
        for t in time_points:
            x = velocity * t
            y = 0
            z = 1.0
            trajectory.append([x, y, z])
        
        return trajectory
    
    def _calculate_distance(self, trajectory: List[List[float]]) -> float:
        """Calcular distância total percorrida"""
        distance = 0
        for i in range(1, len(trajectory)):
            prev = np.array(trajectory[i-1])
            curr = np.array(trajectory[i])
            distance += np.linalg.norm(curr - prev)
        return distance
    
    def _calculate_drag_force(self, velocity: List[float], density: float, 
                            drag_coefficient: float, body_id: int) -> float:
        """Calcular força de arrasto do fluido"""
        speed = np.linalg.norm(velocity)
        if speed == 0:
            return 0
        
        # Área da seção transversal simplificada
        mass = p.getDynamicsInfo(body_id, -1)[0]
        cross_sectional_area = mass / 1000  # aproximação
        
        # Força de arrasto: F = 0.5 * ρ * Cd * A * v²
        drag_force = 0.5 * density * drag_coefficient * cross_sectional_area * speed**2
        
        return drag_force
    
    def get_simulation_status(self, db: Session, simulation_id: UUID) -> Optional[Simulation]:
        """Obter status da simulação"""
        return db.query(Simulation).filter(Simulation.id == simulation_id).first()
    
    def get_model_simulations(self, db: Session, model_id: UUID) -> List[Simulation]:
        """Obter todas as simulações de um modelo"""
        return db.query(Simulation).filter(Simulation.modelo_3d_id == model_id).all()
    
    # ========== MÉTODOS PARA CELERY ==========
    
    def execute_simulation_async(self, simulation_id: UUID, model_path: str, 
                               simulation_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executar simulação de forma assíncrona (para Celery)
        """
        try:
            # Verificar cache primeiro
            cache_key = self._get_cache_key(model_path, simulation_data["tipo"], 
                                          simulation_data.get("parametros", {}))
            cached_result = self._get_cached_result(cache_key)
            
            if cached_result:
                logger.info(f"Usando resultado cacheado para simulação {simulation_id}")
                return {"status": "completed", "result": cached_result, "cached": True}
            
            # Executar simulação
            model_3d_mock = type('MockModel', (), {'arquivo_path': model_path})()
            simulation_data_mock = type('MockSimulationData', (), simulation_data)()
            
            result = self._execute_simulation_sync(simulation_id, model_3d_mock, simulation_data_mock)
            
            # Cachear resultado
            if result.get("status") == "completed":
                self._cache_result(cache_key, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Erro na simulação assíncrona {simulation_id}: {e}")
            return {
                "status": "failed", 
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _execute_simulation_sync(self, simulation_id: UUID, model_3d: Any, 
                               simulation_data: Any) -> Dict[str, Any]:
        """Executar simulação síncrona (usado pelo Celery)"""
        tipo = simulation_data.tipo_simulacao if hasattr(simulation_data, 'tipo_simulacao') else simulation_data["tipo"]
        
        if tipo == "drop_test":
            return self._run_drop_test_sync(simulation_id, model_3d, simulation_data)
        elif tipo == "stress_test":
            return self._run_stress_test_sync(simulation_id, model_3d, simulation_data)
        elif tipo == "motion":
            return self._run_motion_test_sync(simulation_id, model_3d, simulation_data)
        elif tipo == "fluid":
            return self._run_fluid_test_sync(simulation_id, model_3d, simulation_data)
        else:
            raise ValueError(f"Tipo de simulação não suportado: {tipo}")
    
    # ========== MÉTODOS SINCRONIZADOS PARA CELERY ==========
    
    def _run_drop_test_sync(self, simulation_id: UUID, model_3d: Any, 
                          simulation_data: Any) -> Dict[str, Any]:
        """Versão síncrona do teste de queda"""
        try:
            # Inicializar PyBullet
            physics_client = self._initialize_pybullet()
            
            # Carregar modelo 3D
            model_path = Path(model_3d.arquivo_path)
            body_id = self._load_3d_model_to_pybullet(model_path, physics_client)
            
            # Configurar parâmetros
            params = simulation_data.parametros if hasattr(simulation_data, 'parametros') else simulation_data.get("parametros", {})
            drop_height = params.get("drop_height", 1.0)
            num_drops = params.get("num_drops", 5)
            gravity = -9.8
            
            results = {
                "tipo": "drop_test",
                "testes": [],
                "metricas": {},
                "status": "completed",
                "timestamp": datetime.now().isoformat()
            }
            
            start_time = time.time()
            
            for drop_num in range(num_drops):
                # Resetar posição
                p.resetBasePositionAndOrientation(body_id, [0, 0, drop_height], [0, 0, 0, 1])
                p.resetBaseVelocity(body_id, [0, 0, 0], [0, 0, 0])
                p.setGravity(0, 0, gravity)
                
                # Simular queda
                velocities = []
                positions = []
                collision_points = []
                
                simulation_time = 0
                dt = 1/240
                
                while simulation_time < 5.0:
                    p.stepSimulation()
                    simulation_time += dt
                    
                    pos, orn = p.getBasePositionAndOrientation(body_id)
                    vel, ang_vel = p.getBaseVelocity(body_id)
                    
                    velocities.append(vel)
                    positions.append(pos)
                    
                    # Detectar contato
                    contact_points = p.getContactPoints(body_id, -1)
                    if contact_points and not collision_points:
                        collision_points.append({
                            "time": simulation_time,
                            "position": pos,
                            "velocity": vel
                        })
                    
                    # Parar se objeto parar
                    if len(velocities) > 60:
                        recent_vel = velocities[-10:]
                        if all(abs(v[2]) < 0.1 for v in recent_vel):
                            break
                
                # Analisar resultado
                teste_resultado = self._analyze_drop_test(
                    drop_num, positions, velocities, collision_points
                )
                results["testes"].append(teste_resultado)
            
            results["metricas"] = self._calculate_drop_test_metrics(results["testes"])
            results["duracao_total"] = time.time() - start_time
            
            p.disconnect(physics_client)
            
            return results
            
        except Exception as e:
            logger.error(f"Erro no teste de queda síncrono: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _run_stress_test_sync(self, simulation_id: UUID, model_3d: Any, 
                            simulation_data: Any) -> Dict[str, Any]:
        """Versão síncrona do teste de stress"""
        try:
            physics_client = self._initialize_pybullet()
            
            model_path = Path(model_3d.arquivo_path)
            body_id = self._load_3d_model_to_pybullet(model_path, physics_client)
            
            params = simulation_data.parametros if hasattr(simulation_data, 'parametros') else simulation_data.get("parametros", {})
            max_force = params.get("max_force", 1000)
            force_direction = params.get("force_direction", [0, 0, 1])
            force_increment = params.get("force_increment", 100)
            
            results = {
                "tipo": "stress_test",
                "testes_forca": [],
                "metricas": {},
                "ponto_ruptura": None,
                "status": "completed",
                "timestamp": datetime.now().isoformat()
            }
            
            current_force = 0
            while current_force <= max_force:
                p.resetBasePositionAndOrientation(body_id, [0, 0, 0.5], [0, 0, 0, 1])
                p.resetBaseVelocity(body_id, [0, 0, 0], [0, 0, 0])
                
                force = [f * current_force for f in force_direction]
                p.applyExternalForce(body_id, -1, force, [0, 0, 0], p.LINK_FRAME)
                
                for _ in range(240):
                    p.stepSimulation()
                
                pos, orn = p.getBasePositionAndOrientation(body_id)
                vel, ang_vel = p.getBaseVelocity(body_id)
                displacement = np.linalg.norm(np.array(pos))
                
                teste_result = {
                    "forca": current_force,
                    "posicao_final": pos,
                    "velocidade_final": vel,
                    "deslocamento": displacement
                }
                
                results["testes_forca"].append(teste_result)
                
                if displacement > 0.5:
                    results["ponto_ruptura"] = current_force
                    break
                
                current_force += force_increment
            
            results["metricas"] = self._calculate_stress_test_metrics(results)
            
            p.disconnect(physics_client)
            
            return results
            
        except Exception as e:
            logger.error(f"Erro no teste de stress síncrono: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _run_motion_test_sync(self, simulation_id: UUID, model_3d: Any, 
                            simulation_data: Any) -> Dict[str, Any]:
        """Versão síncrona do teste de movimento"""
        # Implementação similar para movimento e fluido
        return {"status": "not_implemented", "message": "Motion test sync not implemented yet"}
    
    def _run_fluid_test_sync(self, simulation_id: UUID, model_3d: Any, 
                           simulation_data: Any) -> Dict[str, Any]:
        """Versão síncrona do teste de fluido"""
        # Implementação similar para fluido
        return {"status": "not_implemented", "message": "Fluid test sync not implemented yet"}
    
    # ========== UTILITÁRIOS E VALIDAÇÃO ==========
    
    def validate_simulation_parameters(self, simulation_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Validar parâmetros de simulação"""
        config = self.simulation_configs.get(simulation_type, {})
        errors = []
        warnings = []
        
        if simulation_type == "drop_test":
            height = parameters.get("drop_height", 1.0)
            if height > config.get("max_height", 5.0):
                errors.append(f"Altura máxima permitida: {config['max_height']}m")
            
            drops = parameters.get("num_drops", 5)
            if drops > config.get("max_drops", 20):
                warnings.append(f"Many drops may slow simulation (max: {config['max_drops']})")
        
        elif simulation_type == "stress_test":
            max_force = parameters.get("max_force", 1000)
            if max_force > config.get("max_force", 10000):
                errors.append(f"Força máxima permitida: {config['max_force']}N")
            
            increment = parameters.get("force_increment", 100)
            if increment > config.get("max_increment", 1000):
                errors.append(f"Incremento máximo: {config['max_increment']}N")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "suggested_parameters": self._suggest_parameters(simulation_type, parameters)
        }
    
    def _suggest_parameters(self, simulation_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Sugerir parâmetros otimizados"""
        config = self.simulation_configs.get(simulation_type, {})
        suggested = parameters.copy()
        
        if simulation_type == "drop_test":
            suggested["drop_height"] = min(
                parameters.get("drop_height", config["default_height"]),
                config["max_height"]
            )
            suggested["num_drops"] = min(
                parameters.get("num_drops", config["default_drops"]),
                config["max_drops"]
            )
        
        return suggested