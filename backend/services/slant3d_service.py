"""
Serviço de Integração Slant3D API - Sprint 5
Integração com API externa para cotações reais de impressão 3D
"""

import json
import logging
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from uuid import UUID
from datetime import datetime, timedelta
import base64
import hashlib

import httpx
from sqlalchemy.orm import Session

from backend.core.config import SLANT3D_API_KEY
from models.budgeting import Slant3DQuote, IntelligentBudget
from schemas.budgeting import Slant3DQuoteRequest, Slant3DQuote as Slant3DQuoteSchema

logger = logging.getLogger(__name__)

class Slant3DService:
    """
    Serviço para integração com API Slant3D
    Busca cotações reais de impressão 3D
    """
    
    def __init__(self):
        self.base_url = "https://api.slant3d.com/v1"
        self.api_key = SLANT3D_API_KEY
        
        if not self.api_key:
            logger.warning("SLANT3D_API_KEY não configurado. Serviços limitados.")
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}" if self.api_key else "",
            "Content-Type": "application/json",
            "User-Agent": "3dPot-Intelligent-Budgeting/1.0"
        }
        
        # Cache para cotações
        self._quote_cache = {}
        self._cache_ttl = 3600  # 1 hora
        
        # Configurações de material
        self.material_config = {
            "PLA": {
                "base_price_multiplier": 1.0,
                "available_colors": ["white", "black", "blue", "red", "green", "yellow"],
                "finish_types": ["standard", "matte", "glossy"],
                "layer_height_range": [0.1, 0.2, 0.3],
                "infill_range": [10, 100]
            },
            "ABS": {
                "base_price_multiplier": 1.3,
                "available_colors": ["white", "black", "blue", "red"],
                "finish_types": ["standard", "matte"],
                "layer_height_range": [0.15, 0.25, 0.35],
                "infill_range": [15, 100]
            },
            "PETG": {
                "base_price_multiplier": 1.5,
                "available_colors": ["white", "black", "blue", "red", "clear"],
                "finish_types": ["standard", "glossy"],
                "layer_height_range": [0.1, 0.2, 0.3],
                "infill_range": [15, 100]
            },
            "Nylon": {
                "base_price_multiplier": 2.0,
                "available_colors": ["white", "black"],
                "finish_types": ["standard"],
                "layer_height_range": [0.15, 0.25],
                "infill_range": [20, 100]
            }
        }
        
    async def get_quote(
        self,
        db: Session,
        budget_id: UUID,
        quote_request: Slant3DQuoteRequest
    ) -> Slant3DQuoteSchema:
        """
        Obter cotação do Slant3D
        
        Args:
            db: Sessão do banco
            budget_id: ID do orçamento
            quote_request: Dados da cotação
            
        Returns:
            Cotação do Slant3D
        """
        try:
            # Verificar cache primeiro
            cache_key = self._generate_cache_key(quote_request)
            cached_quote = self._get_cached_quote(cache_key)
            if cached_quote:
                logger.info("Cotação Slant3D recuperada do cache")
                return cached_quote
            
            # Obter orçamento para contexto
            budget = db.query(IntelligentBudget).filter(
                IntelligentBudget.id == budget_id
            ).first()
            
            if not budget:
                raise ValueError("Orçamento não encontrado")
            
            # Fazer requisição para Slant3D
            quote_data = await self._request_slant3d_quote(quote_request, budget)
            
            # Processar resposta
            processed_quote = self._process_quote_response(quote_data, budget_id, quote_request)
            
            # Salvar no cache
            self._cache_quote(cache_key, processed_quote)
            
            # Salvar no banco
            db_quote = self._save_quote_to_db(db, budget_id, processed_quote)
            
            logger.info(f"Cotação Slant3D obtida: {processed_quote.quote_id}")
            return processed_quote
            
        except Exception as e:
            logger.error(f"Erro ao obter cotação Slant3D: {e}")
            # Retornar cotação estimada como fallback
            return await self._generate_estimated_quote(quote_request, budget_id)
    
    async def _request_slant3d_quote(
        self,
        quote_request: Slant3DQuoteRequest,
        budget: IntelligentBudget
    ) -> Dict[str, Any]:
        """Fazer requisição para API Slant3D"""
        
        if not self.api_key:
            # Retornar dados simulados se não há API key
            return self._generate_mock_response(quote_request, budget)
        
        try:
            async with httpx.AsyncClient() as client:
                # Preparar dados da requisição
                request_data = self._prepare_request_data(quote_request, budget)
                
                # Fazer requisição
                response = await client.post(
                    f"{self.base_url}/quotes",
                    headers=self.headers,
                    json=request_data,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 401:
                    logger.warning("API Slant3D: Unauthorized - usando estimativa")
                    return self._generate_mock_response(quote_request, budget)
                else:
                    logger.warning(f"API Slant3D: Status {response.status_code}")
                    return self._generate_mock_response(quote_request, budget)
                    
        except httpx.TimeoutException:
            logger.warning("Timeout na API Slant3D - usando estimativa")
            return self._generate_mock_response(quote_request, budget)
        except Exception as e:
            logger.error(f"Erro na API Slant3D: {e}")
            return self._generate_mock_response(quote_request, budget)
    
    def _prepare_request_data(
        self,
        quote_request: Slant3DQuoteRequest,
        budget: IntelligentBudget
    ) -> Dict[str, Any]:
        """Preparar dados para requisição Slant3D"""
        
        # Obter informações do modelo 3D do orçamento
        model_info = self._get_model_info_from_budget(budget)
        
        return {
            "model_url": quote_request.model_id,  # URL do modelo
            "material": quote_request.material.value if hasattr(quote_request.material, 'value') else quote_request.material,
            "quantity": quote_request.quantidade,
            "color": quote_request.color or "white",
            "finish_type": quote_request.finish_type or "standard",
            "layer_height": 0.2,  # Altura padrão
            "infill": 20,  # Infill padrão
            "support": True,
            "adhensive": True,
            "priority": "normal",
            "shipping": {
                "country": "BR",
                "state": "SP",
                "city": "São Paulo",
                "postal_code": "01310-100"
            },
            "model_info": model_info
        }
    
    def _get_model_info_from_budget(self, budget: IntelligentBudget) -> Dict[str, Any]:
        """Extrair informações do modelo 3D do orçamento"""
        # Implementar baseado na estrutura do orçamento
        return {
            "volume_cm3": budget.tempo_impressao_horas * 20,  # Estimativa
            "dimensions": "100x100x100",  # Estimativa
            "file_size_kb": 5000,  # Estimativa
            "complexity": "medium"
        }
    
    def _process_quote_response(
        self,
        quote_data: Dict[str, Any],
        budget_id: UUID,
        quote_request: Slant3DQuoteRequest
    ) -> Slant3DQuoteSchema:
        """Processar resposta da API Slant3D"""
        
        # Se é resposta simulada
        if quote_data.get("mock", False):
            return self._create_mock_quote_schema(quote_request, budget_id)
        
        # Processar resposta real da API
        return Slant3DQuoteSchema(
            quote_id=quote_data.get("quote_id", f"SLANT3D-{budget_id}"),
            total_price=float(quote_data.get("total_price", 0)),
            unit_price=float(quote_data.get("unit_price", 0)),
            quantity=quote_request.quantidade,
            material=quote_request.material.value if hasattr(quote_request.material, 'value') else quote_request.material,
            estimated_delivery=quote_data.get("delivery_days", 7),
            shipping_cost=float(quote_data.get("shipping_cost", 0)),
            availability=quote_data.get("available", True),
            processing_time=quote_data.get("processing_days", 3)
        )
    
    def _create_mock_quote_schema(
        self,
        quote_request: Slant3DQuoteRequest,
        budget_id: UUID
    ) -> Slant3DQuoteSchema:
        """Criar schema de cotação simulada"""
        
        # Calcular preço baseado no material e quantidade
        material_config = self.material_config.get(
            quote_request.material.value if hasattr(quote_request.material, 'value') else quote_request.material,
            self.material_config["PLA"]
        )
        
        # Preço base por grama (em dólares)
        base_price_per_gram = {
            "PLA": 0.05,
            "ABS": 0.065,
            "PETG": 0.075,
            "Nylon": 0.10
        }
        
        material_name = quote_request.material.value if hasattr(quote_request.material, 'value') else quote_request.material
        base_price = base_price_per_gram.get(material_name, 0.05)
        
        # Ajustar por quantidade (desconto por volume)
        quantity_multiplier = 1.0
        if quote_request.quantidade >= 10:
            quantity_multiplier = 0.85
        elif quote_request.quantidade >= 5:
            quantity_multiplier = 0.90
        elif quote_request.quantidade >= 2:
            quantity_multiplier = 0.95
        
        # Preço unitário
        unit_price = base_price * material_config["base_price_multiplier"] * quantity_multiplier
        total_price = unit_price * quote_request.quantidade
        
        # Tempo de processamento baseado na complexidade
        processing_days = 3
        if quote_request.quantidade > 5:
            processing_days = 5
        
        return Slant3DQuoteSchema(
            quote_id=f"MOCK-SLANT3D-{budget_id}",
            total_price=round(total_price, 2),
            unit_price=round(unit_price, 2),
            quantity=quote_request.quantidade,
            material=material_name,
            estimated_delivery=processing_days + 2,  # +2 dias de frete
            shipping_cost=15.0,  # Frete fixo simulado
            availability=True,
            processing_time=processing_days
        )
    
    def _generate_mock_response(
        self,
        quote_request: Slant3DQuoteRequest,
        budget: IntelligentBudget
    ) -> Dict[str, Any]:
        """Gerar resposta simulada da API"""
        
        return {
            "mock": True,
            "quote_id": f"MOCK-{budget.id}",
            "total_price": 50.0,  # Simulado
            "unit_price": 50.0,
            "available": True,
            "delivery_days": 7,
            "processing_days": 3,
            "shipping_cost": 15.0,
            "note": "Cotação simulada - API key não configurada"
        }
    
    async def _generate_estimated_quote(
        self,
        quote_request: Slant3DQuoteRequest,
        budget_id: UUID
    ) -> Slant3DQuoteSchema:
        """Gerar cotação estimada como fallback"""
        
        # Usar método simulado
        return self._create_mock_quote_schema(quote_request, budget_id)
    
    def _save_quote_to_db(
        self,
        db: Session,
        budget_id: UUID,
        quote: Slant3DQuoteSchema
    ) -> Slant3DQuote:
        """Salvar cotação no banco de dados"""
        
        db_quote = Slant3DQuote(
            budget_id=budget_id,
            slant3d_quote_id=quote.quote_id,
            model_url="",  # Implementar conforme necessário
            material=quote.material,
            quantidade=quote.quantity,
            color=None,  # Implementar conforme necessário
            finish_type=None,
            preco_unitario=quote.unit_price,
            preco_total=quote.total_price,
            processing_days=quote.processing_time,
            estimated_delivery=quote.estimated_delivery,
            shipping_cost=quote.shipping_cost,
            disponivel=quote.availability,
            active=True,
            quoted_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=30)
        )
        
        db.add(db_quote)
        db.commit()
        db.refresh(db_quote)
        
        return db_quote
    
    def _generate_cache_key(self, quote_request: Slant3DQuoteRequest) -> str:
        """Gerar chave de cache para a cotação"""
        
        data = f"{quote_request.model_id}_{quote_request.material.value}_{quote_request.quantidade}_{quote_request.color}_{quote_request.finish_type}"
        return hashlib.md5(data.encode()).hexdigest()
    
    def _get_cached_quote(self, cache_key: str) -> Optional[Slant3DQuoteSchema]:
        """Recuperar cotação do cache"""
        
        if cache_key in self._quote_cache:
            cached_data = self._quote_cache[cache_key]
            if datetime.utcnow() < cached_data["expires_at"]:
                return cached_data["quote"]
            else:
                del self._quote_cache[cache_key]
        
        return None
    
    def _cache_quote(self, cache_key: str, quote: Slant3DQuoteSchema):
        """Salvar cotação no cache"""
        
        self._quote_cache[cache_key] = {
            "quote": quote,
            "expires_at": datetime.utcnow() + timedelta(seconds=self._cache_ttl)
        }
    
    async def compare_materials(
        self,
        db: Session,
        budget_id: UUID,
        model_info: Dict[str, Any],
        quantity: int = 1
    ) -> List[Slant3DQuoteSchema]:
        """Comparar preços entre materiais no Slant3D"""
        
        materials = ["PLA", "ABS", "PETG", "Nylon"]
        quotes = []
        
        for material in materials:
            try:
                quote_request = Slant3DQuoteRequest(
                    model_id="test-model",
                    material=material,  # Usar string diretamente
                    quantity=quantity
                )
                
                quote = await self.get_quote(db, budget_id, quote_request)
                quotes.append(quote)
                
            except Exception as e:
                logger.warning(f"Erro ao cotar {material}: {e}")
                continue
        
        return quotes
    
    async def check_availability(
        self,
        material: str,
        color: str = "white",
        finish_type: str = "standard"
    ) -> Dict[str, Any]:
        """Verificar disponibilidade de material/cor/acabamento"""
        
        material_config = self.material_config.get(material, self.material_config["PLA"])
        
        return {
            "material_available": material in self.material_config,
            "color_available": color in material_config["available_colors"],
            "finish_available": finish_type in material_config["finish_types"],
            "layer_heights": material_config["layer_height_range"],
            "infill_options": material_config["infill_range"]
        }
    
    async def estimate_shipping(
        self,
        destination_country: str = "BR",
        destination_state: str = "SP",
        destination_city: str = "São Paulo",
        postal_code: str = "01310-100",
        weight_kg: float = 0.5
    ) -> Dict[str, Any]:
        """Estimar custo de frete"""
        
        # Cálculo simples de frete
        base_shipping = 15.0
        weight_multiplier = max(1.0, weight_kg / 0.5)  # Base 0.5kg
        
        # Multiplicadores por região (simplificado)
        region_multipliers = {
            "BR": {
                "SP": 1.0, "RJ": 1.2, "MG": 1.3, "RS": 1.5,
                "default": 1.4
            },
            "default": 2.5
        }
        
        country_mult = region_multipliers.get(destination_country, region_multipliers["default"])
        state_mult = region_multipliers.get(destination_country, {}).get(
            destination_state, 
            region_multipliers.get(destination_country, {}).get("default", 1.4)
        )
        
        estimated_cost = base_shipping * weight_multiplier * country_mult * state_mult
        
        return {
            "estimated_cost": round(estimated_cost, 2),
            "delivery_days": 3 if destination_state == "SP" else 7,
            "carrier": "Correios",
            "service": "PAC",
            "tracking_available": True
        }
    
    def get_material_info(self, material: str) -> Dict[str, Any]:
        """Obter informações detalhadas do material"""
        
        return self.material_config.get(material, self.material_config["PLA"])
    
    def calculate_price_estimate(
        self,
        material: str,
        quantity: int,
        weight_grams: float,
        complexity: str = "medium"
    ) -> Dict[str, Any]:
        """Calcular estimativa de preço"""
        
        material_config = self.material_config.get(material, self.material_config["PLA"])
        
        # Preços base por grama (USD)
        base_prices = {
            "PLA": 0.05,
            "ABS": 0.065,
            "PETG": 0.075,
            "Nylon": 0.10
        }
        
        base_price_per_gram = base_prices.get(material, 0.05)
        
        # Multiplicadores
        complexity_multipliers = {
            "simple": 1.0,
            "medium": 1.2,
            "complex": 1.5
        }
        
        complexity_mult = complexity_multipliers.get(complexity, 1.2)
        
        # Quantidade (desconto por volume)
        quantity_mult = 1.0
        if quantity >= 10:
            quantity_mult = 0.8
        elif quantity >= 5:
            quantity_mult = 0.85
        elif quantity >= 2:
            quantity_mult = 0.95
        
        # Cálculo final
        material_cost = weight_grams * base_price_per_gram
        processing_cost = material_cost * 0.5  # 50% do custo do material
        total_cost = (material_cost + processing_cost) * complexity_mult * quantity_mult
        
        return {
            "material_cost": round(material_cost, 2),
            "processing_cost": round(processing_cost, 2),
            "total_cost": round(total_cost, 2),
            "cost_per_unit": round(total_cost / quantity, 2),
            "quantity_discount": round((1 - quantity_mult) * 100, 1),
            "complexity_multiplier": complexity_mult
        }