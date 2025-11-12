"""
3dPot Platform - Budget Service
Criado em: 2025-11-12 22:42:43
Autor: MiniMax Agent

Serviço para cálculo automático de orçamentos usando Octopart API
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import httpx
import redis.asyncio as redis
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update

# Import local modules
from models.database_models import Project, Budget, Material
from database.database import get_database
from utils.logger import get_logger

logger = get_logger("budget.service")

class OctopartClient:
    """Cliente para integração com Octopart API"""
    
    def __init__(self):
        self.api_key = os.getenv("OCTOPART_API_KEY")
        self.base_url = "https://octopart.com/api/v3"
        
    async def get_component_pricing(self, query: str) -> List[Dict[str, Any]]:
        """
        Busca preços de componentes usando Octopart
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/search/urls",
                    params={
                        "q": query,
                        "apikey": self.api_key,
                        "limit": 5
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Buscar detalhes dos primeiros resultados
                    results = []
                    for item in data.get("items", []):
                        part_response = await client.get(
                            f"{self.base_url}/parts/{item['mpn']}",
                            headers={"Authorization": f"Bearer {self.api_key}"}
                        )
                        
                        if part_response.status_code == 200:
                            part_data = part_response.json()
                            results.append({
                                "mpn": part_data.get("mpn"),
                                "manufacturer": part_data.get("manufacturer", {}).get("name"),
                                "description": part_data.get("short_description"),
                                "pricing": self._extract_pricing(part_data),
                                "availability": part_data.get("availability", "Unknown"),
                                "supplier": "Octopart"
                            })
                    
                    return results
                else:
                    logger.error(f"Erro na API Octopart: {response.status_code}")
                    return []
                    
        except Exception as e:
            logger.error(f"Erro na busca Octopart: {e}")
            return []
    
    def _extract_pricing(self, part_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extrai informações de preços"""
        pricing = []
        
        for offer in part_data.get("offers", []):
            if offer.get("prices"):
                for currency, price in offer["prices"].items():
                    if isinstance(price, list) and price:
                        pricing.append({
                            "price": float(price[0]["price"]),
                            "currency": currency,
                            "supplier": offer.get("supplier", {}).get("name"),
                            "quantity": price[0].get("quantity", 1)
                        })
        
        return pricing

class CostCalculator:
    """Calculadora de custos para orçamentos"""
    
    def calculate_budget(
        self, 
        specifications: Dict[str, Any], 
        components: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Calcula orçamento baseado em especificações e componentes
        """
        try:
            # Cálculo de material
            material_cost = self._calculate_material_cost(specifications)
            
            # Cálculo de hardware/componentes
            hardware_cost = self._calculate_hardware_cost(components)
            
            # Cálculo de mão de obra
            labor_cost = self._calculate_labor_cost(specifications)
            
            # Custo total
            total_cost = material_cost + hardware_cost + labor_cost
            
            # Markup (margem de lucro)
            markup_percentage = 20.0  # Configurável
            final_price = total_cost * (1 + markup_percentage / 100)
            
            return {
                "material_cost": material_cost,
                "hardware_cost": hardware_cost,
                "labor_cost": labor_cost,
                "total_cost": total_cost,
                "markup_percentage": markup_percentage,
                "final_price": final_price,
                "breakdown": {
                    "material": material_cost / total_cost * 100 if total_cost > 0 else 0,
                    "hardware": hardware_cost / total_cost * 100 if total_cost > 0 else 0,
                    "labor": labor_cost / total_cost * 100 if total_cost > 0 else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Erro no cálculo de orçamento: {e}")
            raise
    
    def _calculate_material_cost(self, specs: Dict[str, Any]) -> float:
        """Calcula custo de material baseado em especificações"""
        try:
            material = specs.get("material", "ABS")
            dimensions = specs.get("dimensions", {})
            
            # Cálculo aproximado baseado em volume
            width = dimensions.get("width", 50)  # mm
            height = dimensions.get("height", 20)  # mm
            depth = dimensions.get("depth", 30)  # mm
            
            # Volume em cm³
            volume_cm3 = (width * height * depth) / 1000
            
            # Preços por kg (USD)
            material_prices = {
                "PLA": 25.0,
                "ABS": 30.0,
                "PETG": 35.0,
                "Nylon": 45.0,
                "Resina": 120.0,
                "Metal": 150.0,
                "Alumínio": 80.0,
                "Aço": 50.0
            }
            
            price_per_kg = material_prices.get(material, 30.0)
            
            # Densidade aproximada (g/cm³)
            densities = {
                "PLA": 1.24,
                "ABS": 1.05,
                "PETG": 1.27,
                "Nylon": 1.15,
                "Resina": 1.20,
                "Metal": 7.80,
                "Alumínio": 2.70,
                "Aço": 7.85
            }
            
            density = densities.get(material, 1.0)
            
            # Peso em kg
            weight_kg = (volume_cm3 * density) / 1000
            
            # Custo do material
            material_cost = weight_kg * price_per_kg
            
            # Fator de eficiência (considera perda de material)
            efficiency_factor = 1.3  # 30% de perda
            material_cost *= efficiency_factor
            
            return round(material_cost, 2)
            
        except Exception as e:
            logger.error(f"Erro no cálculo de material: {e}")
            return 0.0
    
    def _calculate_hardware_cost(self, components: List[Dict[str, Any]] = None) -> float:
        """Calcula custo de hardware/componentes"""
        if not components:
            return 0.0
        
        total_cost = 0.0
        
        for component in components:
            # Se tem preço, usar o preço especificado
            if "pricing" in component and component["pricing"]:
                # Usar menor preço disponível
                prices = component["pricing"]
                min_price = min(price["price"] for price in prices)
                total_cost += min_price
            else:
                # Preço estimado baseado no tipo
                cost = self._estimate_component_cost(component)
                total_cost += cost
        
        return round(total_cost, 2)
    
    def _estimate_component_cost(self, component: Dict[str, Any]) -> float:
        """Estima custo de componente individual"""
        part_type = component.get("type", "").lower()
        
        cost_estimates = {
            "sensor": 15.0,
            "motor": 50.0,
            "sensor_ir": 8.0,
            "sensor_weight": 12.0,
            "motor_stepper": 45.0,
            "camera": 80.0,
            "led": 2.0,
            "resistor": 0.5,
            "capacitor": 1.0,
            "connector": 3.0
        }
        
        for key, cost in cost_estimates.items():
            if key in part_type:
                return cost
        
        return 10.0  # Custo padrão
    
    def _calculate_labor_cost(self, specs: Dict[str, Any]) -> float:
        """Calcula custo de mão de obra"""
        try:
            complexity = specs.get("complexity", "Médio")
            
            # Taxa horária (USD/hour)
            hourly_rate = 25.0  # Ajustável por região
            
            # Tempo estimado baseado na complexidade (horas)
            complexity_hours = {
                "Baixo": 2,
                "Médio": 6,
                "Alto": 12
            }
            
            hours = complexity_hours.get(complexity, 6)
            
            # Ajustes adicionais
            dimensions = specs.get("dimensions", {})
            if dimensions:
                volume = (dimensions.get("width", 50) * 
                         dimensions.get("height", 20) * 
                         dimensions.get("depth", 30)) / 1000
                
                # Ajustar tempo baseado no tamanho
                if volume > 1000:  # > 1 litro
                    hours *= 1.5
                elif volume > 500:  # > 0.5 litros
                    hours *= 1.2
            
            labor_cost = hours * hourly_rate
            
            return round(labor_cost, 2)
            
        except Exception as e:
            logger.error(f"Erro no cálculo de mão de obra: {e}")
            return 0.0

class BudgetService:
    """
    Serviço principal de orçamentos
    """
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.octopart_client = OctopartClient()
        self.cost_calculator = CostCalculator()
        self.router = APIRouter()
        
        # Registrar rotas
        self._register_routes()
    
    async def generate_budget(
        self,
        project_id: int,
        specifications: Dict[str, Any],
        components: List[Dict[str, Any]] = None,
        custom_markup: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Gera orçamento completo para um projeto
        """
        try:
            logger.info(f"💰 Gerando orçamento para projeto {project_id}")
            
            # Buscar componentes via Octopart se não fornecidos
            if not components and specifications.get("material") != "Metal":
                components = await self._search_components(specifications)
            
            # Calcular orçamento
            budget_result = self.cost_calculator.calculate_budget(specifications, components)
            
            # Aplicar markup customizado se especificado
            if custom_markup is not None:
                budget_result["markup_percentage"] = custom_markup
                budget_result["final_price"] = budget_result["total_cost"] * (1 + custom_markup / 100)
            
            # Salvar no database
            budget_data = {
                "project_id": project_id,
                "title": f"Orçamento - {datetime.now().strftime('%d/%m/%Y')}",
                "material_cost": budget_result["material_cost"],
                "hardware_cost": budget_result["hardware_cost"],
                "labor_cost": budget_result["labor_cost"],
                "total_cost": budget_result["total_cost"],
                "markup_percentage": budget_result["markup_percentage"],
                "final_price": budget_result["final_price"],
                "valid_until": datetime.utcnow() + timedelta(days=30),
                "status": "draft"
            }
            
            logger.info(f"✅ Orçamento gerado: ${budget_result['final_price']:.2f}")
            
            return {
                "budget": budget_result,
                "components": components or [],
                "specifications": specifications
            }
            
        except Exception as e:
            logger.error(f"❌ Erro na geração de orçamento: {e}")
            raise
    
    async def _search_components(self, specifications: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Busca componentes relacionados via Octopart"""
        try:
            # Construir query de busca
            components = []
            
            # Buscar por tipo de material/funcionalidade
            if specifications.get("functionality") == "Fixação":
                # Buscar parafusos e porcas
                query = "m3 screws nuts fasteners"
                component_data = await self.octopart_client.get_component_pricing(query)
                components.extend(component_data)
            
            # Adicionar outros tipos de busca baseado nas especificações
            
            return components
            
        except Exception as e:
            logger.error(f"Erro na busca de componentes: {e}")
            return []
    
    def _register_routes(self):
        """Registra rotas REST"""
        
        @self.router.post("/generate")
        async def generate_budget_endpoint(request: Dict[str, Any], db: AsyncSession = Depends(get_database)):
            """Endpoint para geração de orçamentos"""
            try:
                project_id = request["project_id"]
                specifications = request["specifications"]
                components = request.get("components")
                custom_markup = request.get("custom_markup")
                
                # Verificar se projeto existe
                project_result = await db.execute(select(Project).where(Project.id == project_id))
                project = project_result.scalar_one_or_none()
                
                if not project:
                    raise HTTPException(status_code=404, detail="Projeto não encontrado")
                
                # Gerar orçamento
                budget_result = await self.generate_budget(
                    project_id, specifications, components, custom_markup
                )
                
                return budget_result
                
            except Exception as e:
                logger.error(f"❌ Erro na geração de orçamento: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.get("/projects/{project_id}/budgets")
        async def get_project_budgets(project_id: int, db: AsyncSession = Depends(get_database)):
            """Lista orçamentos de um projeto"""
            try:
                result = await db.execute(
                    select(Budget)
                    .where(Budget.project_id == project_id)
                    .order_by(Budget.created_at.desc())
                )
                budgets = result.scalars().all()
                
                return {
                    "project_id": project_id,
                    "budgets": [
                        {
                            "id": b.id,
                            "title": b.title,
                            "total_cost": str(b.total_cost),
                            "final_price": str(b.final_price),
                            "status": b.status,
                            "valid_until": b.valid_until.isoformat() if b.valid_until else None,
                            "created_at": b.created_at.isoformat()
                        }
                        for b in budgets
                    ]
                }
                
            except Exception as e:
                logger.error(f"❌ Erro ao buscar orçamentos: {e}")
                raise HTTPException(status_code=500, detail=str(e))

# Instância global (será inicializada no main.py)
budget_service = None