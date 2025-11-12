"""
Serviço de Comparação de Fornecedores - Sprint 5
Sistema inteligente para comparar fornecedores e otimizar custos
"""

import json
import logging
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from uuid import UUID
from datetime import datetime, timedelta
from enum import Enum
import numpy as np

import httpx
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from ..models.budgeting import (
    BudgetSupplier, SupplierQuote, IntelligentBudget
)
from ..schemas.budgeting import (
    SupplierComparisonRequest, SupplierQuote as SupplierQuoteSchema, 
    SupplierComparison as SupplierComparisonSchema
)

logger = logging.getLogger(__name__)

class SupplierType(Enum):
    """Tipos de fornecedores"""
    PRINT_SERVICE = "print_service"  # Serviços de impressão 3D
    MATERIALS = "materials"          # Fornecedores de materiais
    ELECTRONICS = "electronics"      # Componentes eletrônicos
    ASSEMBLY = "assembly"            # Serviços de montagem
    INTEGRATED = "integrated"        # Fornecedores integrados

class ComparisonCriteria(Enum):
    """Critérios de comparação"""
    PRICE = "price"
    QUALITY = "quality"
    DELIVERY_TIME = "delivery_time"
    RELIABILITY = "reliability"
    SHIPPING_COST = "shipping_cost"
    OVERALL = "overall"

class SuppliersService:
    """
    Serviço para comparação inteligente de fornecedores
    Analisa preços, qualidade, confiabilidade e recomendação automática
    """
    
    def __init__(self):
        # Configurações de ponderação para recomendação
        self.criteria_weights = {
            ComparisonCriteria.PRICE: 0.35,
            ComparisonCriteria.QUALITY: 0.25,
            ComparisonCriteria.DELIVERY_TIME: 0.20,
            ComparisonCriteria.RELIABILITY: 0.15,
            ComparisonCriteria.SHIPPING_COST: 0.05
        }
        
        # Base de dados de fornecedores (pode ser expandida)
        self.supplier_database = self._initialize_supplier_database()
        
        # Cache para otimização
        self._price_cache = {}
        self._cache_ttl = 1800  # 30 minutos
        
    def _initialize_supplier_database(self) -> List[Dict[str, Any]]:
        """Inicializar base de dados de fornecedores"""
        return [
            # Serviços de Impressão 3D
            {
                "nome": "Slant3D",
                "tipo": SupplierType.PRINT_SERVICE.value,
                "url": "https://slant3d.com",
                "pais": "Brasil",
                "estado": "SP",
                "cidade": "São Paulo",
                "confiabilidade": 0.95,
                "rating": 4.8,
                "qualidade_material": 0.9,
                "materiais_suportados": ["PLA", "ABS", "PETG", "Nylon"],
                "formatos_suportados": ["STL", "OBJ", "3MF"],
                "servicos_adicionais": ["Acabamento", "Pintura", "Montagem"],
                "tempo_entrega_padrao": 5,
                "custo_frete_padrao": 15.0
            },
            {
                "nome": "Impressora 3D Express",
                "tipo": SupplierType.PRINT_SERVICE.value,
                "url": "https://impressora3dexpress.com.br",
                "pais": "Brasil",
                "estado": "RJ",
                "cidade": "Rio de Janeiro",
                "confiabilidade": 0.88,
                "rating": 4.5,
                "qualidade_material": 0.85,
                "materiais_suportados": ["PLA", "ABS", "PETG"],
                "formatos_suportados": ["STL", "OBJ"],
                "servicos_adicionais": ["Suporte", "Consultoria"],
                "tempo_entrega_padrao": 7,
                "custo_frete_padrao": 20.0
            },
            {
                "nome": "TechPrint 3D",
                "tipo": SupplierType.PRINT_SERVICE.value,
                "url": "https://techprint3d.com.br",
                "pais": "Brasil",
                "estado": "MG",
                "cidade": "Belo Horizonte",
                "confiabilidade": 0.90,
                "rating": 4.6,
                "qualidade_material": 0.88,
                "materiais_suportados": ["PLA", "ABS", "PETG", "Nylon", "Resin"],
                "formatos_suportados": ["STL", "OBJ", "3MF", "PLY"],
                "servicos_adicionais": ["Design", "Otimização", "Prototipagem"],
                "tempo_entrega_padrao": 6,
                "custo_frete_padrao": 18.0
            },
            
            # Fornecedores de Materiais
            {
                "nome": "3D Filamentos",
                "tipo": SupplierType.MATERIALS.value,
                "url": "https://3dfilamentos.com.br",
                "pais": "Brasil",
                "estado": "SP",
                "cidade": "São Paulo",
                "confiabilidade": 0.92,
                "rating": 4.7,
                "qualidade_material": 0.95,
                "materiais_suportados": ["PLA", "ABS", "PETG", "Nylon", "TPU"],
                "formatos_suportados": [],
                "servicos_adicionais": ["Consultoria", "Suporte Técnico"],
                "tempo_entrega_padrao": 3,
                "custo_frete_padrao": 12.0
            },
            {
                "nome": "Brasil 3D",
                "tipo": SupplierType.MATERIALS.value,
                "url": "https://brasil3d.com.br",
                "pais": "Brasil",
                "estado": "PR",
                "cidade": "Curitiba",
                "confiabilidade": 0.85,
                "rating": 4.3,
                "qualidade_material": 0.82,
                "materiais_suportados": ["PLA", "ABS", "PETG"],
                "formatos_suportados": [],
                "servicos_adicionais": [],
                "tempo_entrega_padrao": 5,
                "custo_frete_padrao": 15.0
            },
            
            # Componentes Eletrônicos
            {
                "nome": "EletronicShop",
                "tipo": SupplierType.ELECTRONICS.value,
                "url": "https://electronicshop.com.br",
                "pais": "Brasil",
                "estado": "SP",
                "cidade": "São Paulo",
                "confiabilidade": 0.94,
                "rating": 4.8,
                "qualidade_material": 0.90,
                "materiais_suportados": [],
                "formatos_suportados": [],
                "servicos_adicionais": ["Suporte", "Consultoria", "Garantia Estendida"],
                "tempo_entrega_padrao": 2,
                "custo_frete_padrao": 10.0
            },
            {
                "nome": "ChipMania",
                "tipo": SupplierType.ELECTRONICS.value,
                "url": "https://chipmania.com.br",
                "pais": "Brasil",
                "estado": "SC",
                "cidade": "Florianópolis",
                "confiabilidade": 0.87,
                "rating": 4.4,
                "qualidade_material": 0.85,
                "materiais_suportados": [],
                "formatos_suportados": [],
                "servicos_adicionais": ["Desenvolvimento", "PCB"],
                "tempo_entrega_padrao": 4,
                "custo_frete_padrao": 14.0
            }
        ]
    
    async def compare_suppliers(
        self,
        db: Session,
        budget_id: UUID,
        request: SupplierComparisonRequest
    ) -> SupplierComparisonSchema:
        """
        Comparar fornecedores para um orçamento
        
        Args:
            db: Sessão do banco
            budget_id: ID do orçamento
            request: Parâmetros da comparação
            
        Returns:
            Comparação detalhada de fornecedores
        """
        try:
            # Obter orçamento
            budget = db.query(IntelligentBudget).filter(
                IntelligentBudget.id == budget_id
            ).first()
            
            if not budget:
                raise ValueError("Orçamento não encontrado")
            
            # Obter dados do projeto
            budget_data = await self._extract_budget_data(budget)
            
            # Buscar cotações de fornecedores
            supplier_quotes = await self._get_supplier_quotes(
                budget_data, request, budget
            )
            
            # Calcular scores de comparação
            comparison_scores = self._calculate_comparison_scores(supplier_quotes)
            
            # Determinar fornecedor recomendado
            recommended_supplier = self._determine_recommended_supplier(
                supplier_quotes, comparison_scores
            )
            
            # Gerar análise comparativa
            analysis = self._generate_comparison_analysis(
                supplier_quotes, comparison_scores, budget_data
            )
            
            # Criar schema de resposta
            comparison = SupplierComparisonSchema(
                budget_id=budget_id,
                quotes=[self._quote_to_schema(q) for q in supplier_quotes],
                recommended_supplier=self._quote_to_schema(recommended_supplier),
                comparison_criteria=comparison_scores,
                reasoning=analysis["reasoning"]
            )
            
            # Salvar fornecedores no orçamento
            await self._save_supplier_comparison(db, budget_id, supplier_quotes)
            
            logger.info(f"Comparação de fornecedores concluída para orçamento {budget_id}")
            return comparison
            
        except Exception as e:
            logger.error(f"Erro na comparação de fornecedores: {e}")
            raise
    
    async def _extract_budget_data(self, budget: IntelligentBudget) -> Dict[str, Any]:
        """Extrair dados relevantes do orçamento"""
        
        return {
            "material_recomendado": budget.material_recomendado,
            "custo_material": budget.custo_material,
            "custo_componentes": budget.custo_componentes,
            "custo_impressao": budget.custo_impressao,
            "custo_mao_obra": budget.custo_mao_obra,
            "qualidade_score": budget.quality_score,
            "complexidade_score": budget.complexidade_score,
            "tempo_entrega_estimado": budget.tempo_entrega_estimado,
            "itens_detalhados": budget.itens_detalhados or []
        }
    
    async def _get_supplier_quotes(
        self,
        budget_data: Dict[str, Any],
        request: SupplierComparisonRequest,
        budget: IntelligentBudget
    ) -> List[SupplierQuote]:
        """Obter cotações de múltiplos fornecedores"""
        
        # Determinar tipos de fornecedores necessários
        supplier_types = self._determine_required_suppliers(budget_data)
        
        all_quotes = []
        
        for supplier_type in supplier_types:
            # Buscar fornecedores deste tipo
            type_suppliers = [
                s for s in self.supplier_database 
                if s["tipo"] == supplier_type.value
            ]
            
            # Limitar número de fornecedores
            if len(type_suppliers) > request.max_suppliers:
                type_suppliers = type_suppliers[:request.max_suppliers]
            
            # Gerar cotações para cada fornecedor
            for supplier_info in type_suppliers:
                try:
                    quote = await self._generate_supplier_quote(
                        supplier_info, budget_data, request, budget
                    )
                    if quote:
                        all_quotes.append(quote)
                        
                except Exception as e:
                    logger.warning(f"Erro ao gerar cotação para {supplier_info['nome']}: {e}")
                    continue
        
        # Ordenar por score geral
        all_quotes.sort(key=lambda x: x.custo_beneficio_score or 0, reverse=True)
        
        return all_quotes
    
    def _determine_required_suppliers(self, budget_data: Dict[str, Any]) -> List[SupplierType]:
        """Determinar quais tipos de fornecedores são necessários"""
        
        required_types = []
        
        # Sempre precisamos de impressão 3D se há material
        if budget_data["custo_material"] > 0:
            required_types.append(SupplierType.PRINT_SERVICE)
        
        # Precisa de materiais se não há serviço integrado
        if budget_data["custo_componentes"] > 0:
            required_types.append(SupplierType.ELECTRONICS)
        
        # Se não há serviços de impressão, precisamos de materiais
        if SupplierType.PRINT_SERVICE not in required_types:
            required_types.append(SupplierType.MATERIALS)
        
        # Adicionar montagem se há mão de obra significativa
        if budget_data["custo_mao_obra"] > budget_data["custo_material"] * 0.5:
            required_types.append(SupplierType.ASSEMBLY)
        
        return required_types
    
    async def _generate_supplier_quote(
        self,
        supplier_info: Dict[str, Any],
        budget_data: Dict[str, Any],
        request: SupplierComparisonRequest,
        budget: IntelligentBudget
    ) -> Optional[SupplierQuote]:
        """Gerar cotação para um fornecedor específico"""
        
        supplier_type = supplier_info["tipo"]
        
        if supplier_type == SupplierType.PRINT_SERVICE.value:
            return await self._generate_print_service_quote(
                supplier_info, budget_data, budget
            )
        elif supplier_type == SupplierType.MATERIALS.value:
            return await self._generate_materials_quote(
                supplier_info, budget_data
            )
        elif supplier_type == SupplierType.ELECTRONICS.value:
            return await self._generate_electronics_quote(
                supplier_info, budget_data
            )
        else:
            return await self._generate_generic_quote(
                supplier_info, budget_data
            )
    
    async def _generate_print_service_quote(
        self,
        supplier_info: Dict[str, Any],
        budget_data: Dict[str, Any],
        budget: IntelligentBudget
    ) -> SupplierQuote:
        """Gerar cotação para serviço de impressão"""
        
        # Calcular preço baseado no orçamento
        base_cost = (
            budget_data["custo_material"] + 
            budget_data["custo_impressao"]
        )
        
        # Ajustar por qualidade do fornecedor
        quality_multiplier = supplier_info["qualidade_material"]
        cost_multiplier = 1.0 / quality_multiplier  # Melhor qualidade = menor preço
        
        # Ajuste por localização
        location_multiplier = self._calculate_location_multiplier(supplier_info)
        
        # Preço final
        final_cost = base_cost * cost_multiplier * location_multiplier
        
        # Frete
        shipping_cost = self._calculate_shipping_cost(
            supplier_info, budget_data, budget_data.get('include_shipping', True)
        )
        
        # Tempo de entrega
        delivery_time = supplier_info["tempo_entrega_padrao"]
        if budget_data["qualidade_score"] > 80:
            delivery_time += 1  # Mais tempo para alta qualidade
        
        return SupplierQuote(
            supplier_id=f"PRINT-{supplier_info['nome'].replace(' ', '_')}",
            supplier_name=supplier_info["nome"],
            total_cost=final_cost + shipping_cost,
            unit_cost=final_cost,
            delivery_time=delivery_time,
            quality_rating=supplier_info["rating"],
            reliability_score=supplier_info["confiabilidade"],
            shipping_cost=shipping_cost if budget_data.get('include_shipping', True) else 0
        )
    
    async def _generate_materials_quote(
        self,
        supplier_info: Dict[str, Any],
        budget_data: Dict[str, Any]
    ) -> SupplierQuote:
        """Gerar cotação para fornecedor de materiais"""
        
        # Usar custo do material como base
        base_cost = budget_data["custo_material"]
        
        # Ajuste por qualidade do fornecedor
        quality_adjustment = 1.0 - (supplier_info["qualidade_material"] - 0.8) * 0.5
        
        final_cost = base_cost * quality_adjustment
        
        return SupplierQuote(
            supplier_id=f"MAT-{supplier_info['nome'].replace(' ', '_')}",
            supplier_name=supplier_info["nome"],
            total_cost=final_cost,
            unit_cost=final_cost,
            delivery_time=supplier_info["tempo_entrega_padrao"],
            quality_rating=supplier_info["rating"],
            reliability_score=supplier_info["confiabilidade"],
            shipping_cost=12.0  # Frete padrão para materiais
        )
    
    async def _generate_electronics_quote(
        self,
        supplier_info: Dict[str, Any],
        budget_data: Dict[str, Any]
    ) -> SupplierQuote:
        """Gerar cotação para componentes eletrônicos"""
        
        # Usar custo de componentes como base
        base_cost = budget_data["custo_componentes"]
        
        # Ajuste por confiabilidade
        reliability_adjustment = supplier_info["confiabilidade"]
        
        final_cost = base_cost / reliability_adjustment
        
        return SupplierQuote(
            supplier_id=f"ELE-{supplier_info['nome'].replace(' ', '_')}",
            supplier_name=supplier_info["nome"],
            total_cost=final_cost,
            unit_cost=final_cost,
            delivery_time=supplier_info["tempo_entrega_padrao"],
            quality_rating=supplier_info["rating"],
            reliability_score=supplier_info["confiabilidade"],
            shipping_cost=10.0
        )
    
    async def _generate_generic_quote(
        self,
        supplier_info: Dict[str, Any],
        budget_data: Dict[str, Any]
    ) -> SupplierQuote:
        """Gerar cotação genérica"""
        
        total_cost = budget_data["custo_material"] + budget_data["custo_componentes"]
        
        return SupplierQuote(
            supplier_id=f"GEN-{supplier_info['nome'].replace(' ', '_')}",
            supplier_name=supplier_info["nome"],
            total_cost=total_cost,
            unit_cost=total_cost,
            delivery_time=supplier_info["tempo_entrega_padrao"],
            quality_rating=supplier_info["rating"],
            reliability_score=supplier_info["confiabilidade"],
            shipping_cost=15.0
        )
    
    def _calculate_location_multiplier(self, supplier_info: Dict[str, Any]) -> float:
        """Calcular multiplicador de preço por localização"""
        
        # Multiplicadores por estado (exemplo)
        location_multipliers = {
            "SP": 1.0,
            "RJ": 1.1,
            "MG": 1.15,
            "PR": 1.2,
            "SC": 1.25,
            "RS": 1.3,
            "default": 1.4
        }
        
        estado = supplier_info.get("estado", "SP")
        return location_multipliers.get(estado, location_multipliers["default"])
    
    def _calculate_shipping_cost(
        self,
        supplier_info: Dict[str, Any],
        budget_data: Dict[str, Any],
        include_shipping: bool
    ) -> float:
        """Calcular custo de frete"""
        
        if not include_shipping:
            return 0.0
        
        base_shipping = supplier_info["custo_frete_padrao"]
        
        # Ajustar por peso estimado
        weight_factor = max(1.0, budget_data["custo_material"] / 50)  # Base 50 BRL
        
        return base_shipping * weight_factor
    
    def _calculate_comparison_scores(
        self,
        quotes: List[SupplierQuote]
    ) -> Dict[str, float]:
        """Calcular scores de comparação entre fornecedores"""
        
        if not quotes:
            return {}
        
        # Extrair métricas
        costs = [q.total_cost for q in quotes]
        quality_ratings = [q.quality_rating for q in quotes]
        delivery_times = [q.delivery_time for q in quotes]
        reliability_scores = [q.reliability_score for q in quotes]
        shipping_costs = [q.shipping_cost for q in quotes]
        
        # Normalizar métricas (0-1)
        def normalize(values):
            if not values or len(values) == 1:
                return [0.5] * len(values)
            min_val, max_val = min(values), max(values)
            if min_val == max_val:
                return [0.5] * len(values)
            return [(v - min_val) / (max_val - min_val) for v in values]
        
        cost_scores = normalize(costs)  # Menor custo = maior score
        quality_scores = normalize(quality_ratings)  # Maior rating = maior score
        delivery_scores = [1 - normalize(delivery_times)[i] for i in range(len(delivery_times))]  # Menor tempo = maior score
        reliability_scores_norm = normalize(reliability_scores)
        shipping_scores = normalize(shipping_costs)  # Menor frete = maior score
        
        # Calcular scores ponderados
        final_scores = []
        for i in range(len(quotes)):
            score = (
                (1 - cost_scores[i]) * self.criteria_weights[ComparisonCriteria.PRICE] +
                quality_scores[i] * self.criteria_weights[ComparisonCriteria.QUALITY] +
                delivery_scores[i] * self.criteria_weights[ComparisonCriteria.DELIVERY_TIME] +
                reliability_scores_norm[i] * self.criteria_weights[ComparisonCriteria.RELIABILITY] +
                (1 - shipping_scores[i]) * self.criteria_weights[ComparisonCriteria.SHIPPING_COST]
            )
            final_scores.append(score)
        
        # Atribuir scores aos quotes
        for i, quote in enumerate(quotes):
            quote.custo_beneficio_score = round(final_scores[i], 3)
        
        return {
            "price_weight": self.criteria_weights[ComparisonCriteria.PRICE],
            "quality_weight": self.criteria_weights[ComparisonCriteria.QUALITY],
            "delivery_weight": self.criteria_weights[ComparisonCriteria.DELIVERY_TIME],
            "reliability_weight": self.criteria_weights[ComparisonCriteria.RELIABILITY],
            "shipping_weight": self.criteria_weights[ComparisonCriteria.SHIPPING_COST]
        }
    
    def _determine_recommended_supplier(
        self,
        quotes: List[SupplierQuote],
        comparison_scores: Dict[str, float]
    ) -> SupplierQuote:
        """Determinar fornecedor recomendado baseado nos scores"""
        
        if not quotes:
            raise ValueError("Nenhuma cotação disponível")
        
        # Encontrar fornecedor com maior score
        best_quote = max(quotes, key=lambda x: x.custo_beneficio_score or 0)
        
        # Marcar como recomendado
        # best_quote.recommended = True  # Isso seria um campo no modelo
        
        return best_quote
    
    def _generate_comparison_analysis(
        self,
        quotes: List[SupplierQuote],
        comparison_scores: Dict[str, float],
        budget_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Gerar análise detalhada da comparação"""
        
        if not quotes:
            return {"reasoning": "Nenhum fornecedor disponível para análise"}
        
        best_quote = max(quotes, key=lambda x: x.custo_beneficio_score or 0)
        worst_quote = min(quotes, key=lambda x: x.custo_beneficio_score or 0)
        
        # Calcular diferenças
        cost_difference = best_quote.total_cost - worst_quote.total_cost
        quality_difference = best_quote.quality_rating - worst_quote.quality_rating
        time_difference = worst_quote.delivery_time - best_quote.delivery_time
        
        reasoning = f"""
        Análise baseada em {len(quotes)} fornecedores:
        
        FORNECEDOR RECOMENDADO: {best_quote.supplier_name}
        - Preço: R$ {best_quote.total_cost:.2f}
        - Qualidade: {best_quote.quality_rating}/5.0
        - Prazo: {best_quote.delivery_time} dias
        
        DIFERENÇAS PRINCIPAIS:
        - Economia: R$ {abs(cost_difference):.2f} vs pior opção
        - Qualidade: +{quality_difference:.1f} pontos vs pior opção  
        - Prazo: {time_difference} dias mais rápido
        
        CRITÉRIOS UTILIZADOS:
        - Preço (35%): Impacto significativo no custo total
        - Qualidade (25%): Avaliação baseada em rating e confiabilidade
        - Prazo (20%): Importante para projetos com cronograma
        - Confiabilidade (15%): Reduz riscos de atraso/falha
        - Frete (5%): Custo adicional de entrega
        """
        
        return {
            "reasoning": reasoning.strip(),
            "best_option": best_quote.supplier_name,
            "worst_option": worst_quote.supplier_name,
            "price_savings": abs(cost_difference),
            "quality_improvement": quality_difference,
            "time_improvement": time_difference
        }
    
    def _quote_to_schema(self, quote: SupplierQuote) -> SupplierQuoteSchema:
        """Converter modelo para schema"""
        return SupplierQuoteSchema(**quote.__dict__)
    
    async def _save_supplier_comparison(
        self,
        db: Session,
        budget_id: UUID,
        quotes: List[SupplierQuote]
    ):
        """Salvar comparação de fornecedores no banco"""
        
        for quote in quotes:
            # Verificar se fornecedor já existe
            supplier = db.query(BudgetSupplier).filter(
                BudgetSupplier.budget_id == budget_id,
                BudgetSupplier.nome == quote.supplier_name
            ).first()
            
            if not supplier:
                # Criar novo fornecedor
                supplier = BudgetSupplier(
                    budget_id=budget_id,
                    nome=quote.supplier_name,
                    tipo="print_service",  # Determinar baseado no tipo real
                    preco_total=quote.total_cost,
                    preco_unitario=quote.unit_cost,
                    custo_frete=quote.shipping_cost,
                    tempo_entrega=quote.delivery_time,
                    confiabilidade=quote.reliability_score,
                    rating=quote.quality_rating,
                    qualidade_material=quote.quality_rating / 5.0,
                    recomendado=quote.custo_beneficio_score == max(q.custo_beneficio_score or 0 for q in quotes)
                )
                db.add(supplier)
            
            # Atualizar dados
            supplier.preco_total = quote.total_cost
            supplier.preco_unitario = quote.unit_cost
            supplier.custo_frete = quote.shipping_cost
            supplier.tempo_entrega = quote.delivery_time
            supplier.confiabilidade = quote.reliability_score
            supplier.rating = quote.quality_rating
        
        db.commit()
    
    async def get_supplier_recommendations(
        self,
        budget_data: Dict[str, Any],
        criteria: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Obter recomendações de fornecedores baseadas em critérios"""
        
        # Filtrar fornecedores por critérios
        suitable_suppliers = self.supplier_database.copy()
        
        if criteria:
            # Aplicar filtros específicos
            for criterion in criteria:
                if "high_quality" in criterion:
                    suitable_suppliers = [
                        s for s in suitable_suppliers 
                        if s["rating"] >= 4.5
                    ]
                elif "fast_delivery" in criterion:
                    suitable_suppliers = [
                        s for s in suitable_suppliers 
                        if s["tempo_entrega_padrao"] <= 5
                    ]
                elif "low_cost" in criterion:
                    suitable_suppliers = [
                        s for s in suitable_suppliers 
                        if s["custo_frete_padrao"] <= 15
                    ]
        
        # Ordenar por score composto
        def calculate_composite_score(supplier):
            return (
                supplier["rating"] * 0.3 +
                (5 - supplier["tempo_entrega_padrao"]) * 0.2 +
                supplier["qualidade_material"] * 0.3 +
                (20 - supplier["custo_frete_padrao"]) * 0.1 +
                supplier["confiabilidade"] * 0.1
            )
        
        suitable_suppliers.sort(key=calculate_composite_score, reverse=True)
        
        return suitable_suppliers[:5]  # Top 5
    
    async def analyze_market_trends(
        self,
        material_type: str,
        region: str = "Brasil"
    ) -> Dict[str, Any]:
        """Analisar tendências de mercado para um material"""
        
        # Simular análise de tendências
        trends = {
            "material": material_type,
            "region": region,
            "average_price_trend": "stable",  # stable, increasing, decreasing
            "supply_availability": "good",    # good, limited, scarce
            "quality_improvements": True,
            "new_suppliers": 2,
            "price_volatility": "low",        # low, medium, high
            "seasonal_factors": {
                "high_demand_periods": ["Q1", "Q4"],
                "low_demand_periods": ["Q2"],
                "price_increase_expected": False
            },
            "recommendations": [
                "Considere contratos de longo prazo para estabilidade",
                "Monitore novos fornecedores para oportunidades",
                "Avalie materiais alternativos para reduzir custos"
            ]
        }
        
        return trends