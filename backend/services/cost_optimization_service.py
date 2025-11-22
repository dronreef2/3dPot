"""
Serviço de Otimização de Custos - Sprint 10-11
Motor inteligente de otimização baseado em dados de produção e orçamento
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from uuid import UUID
from datetime import datetime, timedelta
from enum import Enum
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc

from backend.models import IntelligentBudget as Budget, Project
from backend.models.production_models import (
    ProductionOrder, ProductionType, ProductionStatus, QualityStatus,
    ProductionMetrics, ProductionOptimization
)
from backend.schemas.budgeting import IntelligentBudgetResponse
from backend.schemas.production_schemas import OptimizationRequest

logger = logging.getLogger(__name__)

class OptimizationType(Enum):
    """Tipos de otimização disponíveis"""
    MATERIAL_OPTIMIZATION = "material_optimization"
    SUPPLIER_CONSOLIDATION = "supplier_consolidation"
    BATCH_SIZE_OPTIMIZATION = "batch_size_optimization"
    PRODUCTION_EFFICIENCY = "production_efficiency"
    QUALITY_COST_BALANCE = "quality_cost_balance"
    WORKFLOW_OPTIMIZATION = "workflow_optimization"
    ENERGY_OPTIMIZATION = "energy_optimization"
    LABOR_OPTIMIZATION = "labor_optimization"

class CostOptimizationService:
    """
    Serviço para otimização inteligente de custos
    Analisa dados históricos e atuais para identificar oportunidades de redução de custos
    """
    
    def __init__(self):
        # Configurações de otimização
        self.material_cost_thresholds = {
            "savings_threshold": 5.0,  # 5% mínimo de economia
            "volume_threshold": 1000.0,  # R$ 1000 em volume
            "frequency_threshold": 5  # Mínimo 5 ocorrências
        }
        
        # Multiplicadores de custo por tipo de produção
        self.production_efficiency_multipliers = {
            ProductionType.PROTOTYPE: 1.5,
            ProductionType.BATCH_SMALL: 1.2,
            ProductionType.BATCH_MEDIUM: 1.0,
            ProductionType.BATCH_LARGE: 0.8,
            ProductionType.CUSTOM: 1.3,
            ProductionType.SERIES: 0.7
        }
        
        # Benchmarks da indústria (2025)
        self.industry_benchmarks = {
            "material_cost_percentage": 35.0,  # 35% do custo total
            "labor_cost_percentage": 25.0,   # 25% do custo total
            "equipment_cost_percentage": 20.0,  # 20% do custo total
            "quality_cost_percentage": 10.0,   # 10% do custo total
            "overhead_percentage": 10.0        # 10% overhead
        }
    
    async def analyze_cost_optimization_opportunities(
        self,
        db: Session,
        user_id: UUID,
        optimization_request: OptimizationRequest = None
    ) -> Dict[str, Any]:
        """
        Analisar oportunidades de otimização de custos
        
        Args:
            db: Sessão do banco de dados
            user_id: ID do usuário
            optimization_request: Parâmetros de otimização
            
        Returns:
            Análise completa de oportunidades de otimização
        """
        try:
            if optimization_request is None:
                optimization_request = OptimizationRequest()
            
            # 1. Coletar dados históricos
            historical_data = await self._collect_historical_data(db, user_id)
            
            # 2. Analisar cada tipo de otimização
            optimization_results = {}
            
            for opt_type in optimization_request.optimization_types:
                try:
                    if opt_type == "material_optimization":
                        optimization_results[opt_type] = await self._analyze_material_optimization(
                            db, historical_data, optimization_request.target_improvements
                        )
                    elif opt_type == "supplier_consolidation":
                        optimization_results[opt_type] = await self._analyze_supplier_consolidation(
                            db, historical_data
                        )
                    elif opt_type == "batch_size_optimization":
                        optimization_results[opt_type] = await self._analyze_batch_size_optimization(
                            db, historical_data
                        )
                    elif opt_type == "production_efficiency":
                        optimization_results[opt_type] = await self._analyze_production_efficiency(
                            db, historical_data
                        )
                    elif opt_type == "quality_cost_balance":
                        optimization_results[opt_type] = await self._analyze_quality_cost_balance(
                            db, historical_data
                        )
                    elif opt_type == "workflow_optimization":
                        optimization_results[opt_type] = await self._analyze_workflow_optimization(
                            db, historical_data
                        )
                    elif opt_type == "energy_optimization":
                        optimization_results[opt_type] = await self._analyze_energy_optimization(
                            db, historical_data
                        )
                    elif opt_type == "labor_optimization":
                        optimization_results[opt_type] = await self._analyze_labor_optimization(
                            db, historical_data
                        )
                except Exception as e:
                    logger.error(f"Erro na análise de {opt_type}: {e}")
                    optimization_results[opt_type] = {"error": str(e)}
            
            # 3. Consolidar recomendações
            consolidated_recommendations = self._consolidate_recommendations(optimization_results)
            
            # 4. Calcular impacto total
            total_impact = self._calculate_total_impact(optimization_results)
            
            # 5. Priorizar por ROI
            prioritized_recommendations = self._prioritize_by_roi(consolidated_recommendations)
            
            return {
                "analysis_date": datetime.utcnow().isoformat(),
                "data_period_days": 90,  # Últimos 90 dias
                "optimization_results": optimization_results,
                "consolidated_recommendations": prioritized_recommendations,
                "total_impact": total_impact,
                "implementation_roadmap": self._create_implementation_roadmap(prioritized_recommendations)
            }
            
        except Exception as e:
            logger.error(f"Erro na análise de otimização: {e}")
            raise
    
    async def _collect_historical_data(self, db: Session, user_id: UUID) -> Dict[str, Any]:
        """Coletar dados históricos para análise"""
        
        # Buscar projetos do usuário
        projects = db.query(Project).filter(Project.owner_id == user_id).all()
        project_ids = [p.id for p in projects]
        
        if not project_ids:
            return {"budgets": [], "production_orders": [], "metrics": []}
        
        # Buscar orçamentos
        budgets = db.query(Budget).filter(
            Budget.projeto_id.in_(project_ids)
        ).all()
        
        # Buscar ordens de produção
        production_orders = db.query(ProductionOrder).filter(
            ProductionOrder.project_id.in_(project_ids)
        ).all()
        
        # Buscar métricas de produção
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=90)
        
        production_metrics = db.query(ProductionMetrics).filter(
            and_(
                ProductionMetrics.period_start >= start_date,
                ProductionMetrics.period_end <= end_date
            )
        ).all()
        
        return {
            "budgets": budgets,
            "production_orders": production_orders,
            "metrics": production_metrics,
            "projects": projects
        }
    
    async def _analyze_material_optimization(
        self,
        db: Session,
        historical_data: Dict[str, Any],
        target_improvements: Dict[str, float]
    ) -> Dict[str, Any]:
        """Analisar oportunidades de otimização de materiais"""
        
        budgets = historical_data["budgets"]
        production_orders = historical_data["production_orders"]
        
        # Extrair dados de materiais
        material_analysis = {}
        material_usage = {}
        material_costs = {}
        
        for budget in budgets:
            if budget.itens_detalhados:
                for item in budget.itens_detalhados:
                    material_name = item.get("descricao", "").lower()
                    if "material" in material_name or "filamento" in material_name:
                        material_key = self._extract_material_name(material_name)
                        
                        # Acumular uso e custos
                        if material_key not in material_usage:
                            material_usage[material_key] = {
                                "total_quantity": 0,
                                "total_cost": 0,
                                "usage_count": 0,
                                "suppliers": []
                            }
                        
                        material_usage[material_key]["total_quantity"] += float(item.get("preco_total", 0))
                        material_usage[material_key]["total_cost"] += float(item.get("preco_total", 0))
                        material_usage[material_key]["usage_count"] += 1
                        
                        supplier = item.get("fornecedor", "Unknown")
                        if supplier not in material_usage[material_key]["suppliers"]:
                            material_usage[material_key]["suppliers"].append(supplier)
        
        # Analisar oportunidades
        optimization_opportunities = []
        
        for material, data in material_usage.items():
            # 1. Verificar consolidação de fornecedores
            if len(data["suppliers"]) > 2:
                savings_potential = data["total_cost"] * 0.05  # 5% economia estimada
                optimization_opportunities.append({
                    "type": "supplier_consolidation",
                    "material": material,
                    "current_suppliers": len(data["suppliers"]),
                    "recommendation": f"Consolidar para 1-2 fornecedores principais",
                    "estimated_savings": savings_potential,
                    "implementation_effort": "medium",
                    "risk_level": "low"
                })
            
            # 2. Verificar oportunidades de bulk purchasing
            if data["usage_count"] >= 10:
                bulk_savings = data["total_cost"] * 0.08  # 8% economia estimada
                optimization_opportunities.append({
                    "type": "bulk_purchasing",
                    "material": material,
                    "current_usage_frequency": data["usage_count"],
                    "recommendation": "Implementar compras em lote",
                    "estimated_savings": bulk_savings,
                    "implementation_effort": "easy",
                    "risk_level": "low"
                })
        
        # 3. Análise de preços por material
        price_analysis = self._analyze_material_prices(material_usage)
        
        return {
            "analysis_type": "material_optimization",
            "materials_analyzed": len(material_usage),
            "total_material_cost": sum(data["total_cost"] for data in material_usage.values()),
            "optimization_opportunities": optimization_opportunities,
            "price_analysis": price_analysis,
            "priority_recommendations": optimization_opportunities[:3] if optimization_opportunities else []
        }
    
    def _extract_material_name(self, material_description: str) -> str:
        """Extrair nome do material da descrição"""
        materials = ["pla", "abs", "petg", "nylon", "metal", "composite", "resin", "tpu"]
        
        for material in materials:
            if material in material_description:
                return material.upper()
        
        return "UNKNOWN"
    
    def _analyze_material_prices(self, material_usage: Dict[str, Any]) -> Dict[str, Any]:
        """Analisar preços de materiais para identificar outliers"""
        
        price_variations = {}
        
        for material, data in material_usage.items():
            # Calcular preço médio por uso
            avg_price_per_use = data["total_cost"] / max(data["usage_count"], 1)
            
            price_variations[material] = {
                "average_price_per_use": avg_price_per_use,
                "supplier_count": len(data["suppliers"]),
                "price_stability": "high" if len(data["suppliers"]) <= 2 else "medium"
            }
        
        # Identificar materiais com alta variabilidade de preço
        high_variability_materials = [
            material for material, data in price_variations.items()
            if data["price_stability"] == "medium"
        ]
        
        return {
            "price_variations": price_variations,
            "high_variability_materials": high_variability_materials,
            "stabilization_recommendations": [
                f"Negociar preços fixos com fornecedores para {', '.join(high_variability_materials)}"
            ] if high_variability_materials else []
        }
    
    async def _analyze_supplier_consolidation(
        self,
        db: Session,
        historical_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analisar consolidação de fornecedores"""
        
        budgets = historical_data["budgets"]
        supplier_analysis = {}
        
        # Coletar dados de fornecedores
        for budget in budgets:
            if budget.fornecedores:
                for supplier_data in budget.fornecedores:
                    supplier_name = supplier_data.get("nome", "Unknown")
                    
                    if supplier_name not in supplier_analysis:
                        supplier_analysis[supplier_name] = {
                            "total_orders": 0,
                            "total_value": 0.0,
                            "reliability_score": supplier_data.get("confiabilidade", 0.8),
                            "avg_delivery_time": 5,  # Default
                            "quality_rating": 4.0  # Default
                        }
                    
                    supplier_analysis[supplier_name]["total_orders"] += 1
                    supplier_analysis[supplier_name]["total_value"] += float(budget.preco_final or 0)
        
        # Identificar fornecedores principais
        primary_suppliers = sorted(
            supplier_analysis.items(),
            key=lambda x: x[1]["total_value"],
            reverse=True
        )[:3]
        
        # Calcular potencial de consolidação
        total_spend = sum(data["total_value"] for data in supplier_analysis.values())
        consolidated_potential = total_spend * 0.03  # 3% economia estimada
        
        recommendations = []
        
        # Recomendar consolidação
        if len(supplier_analysis) > 5:
            recommendations.append({
                "type": "supplier_reduction",
                "current_supplier_count": len(supplier_analysis),
                "recommended_supplier_count": 3,
                "estimated_savings": consolidated_potential,
                "rationale": "Reduzir complexidade da cadeia de suprimentos",
                "implementation_timeline": "2-3 meses"
            })
        
        return {
            "analysis_type": "supplier_consolidation",
            "current_supplier_count": len(supplier_analysis),
            "primary_suppliers": [
                {
                    "name": name,
                    "total_value": data["total_value"],
                    "reliability_score": data["reliability_score"]
                }
                for name, data in primary_suppliers
            ],
            "total_spend": total_spend,
            "consolidation_potential": consolidated_potential,
            "recommendations": recommendations
        }
    
    async def _analyze_batch_size_optimization(
        self,
        db: Session,
        historical_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analisar otimização de tamanho de lote"""
        
        production_orders = historical_data["production_orders"]
        
        # Agrupar por tipo de produção
        batch_analysis = {}
        
        for order in production_orders:
            prod_type = order.production_type
            
            if prod_type not in batch_analysis:
                batch_analysis[prod_type] = {
                    "orders": [],
                    "avg_quantity": 0,
                    "total_cost": 0,
                    "avg_efficiency": 0
                }
            
            batch_analysis[prod_type]["orders"].append(order)
            batch_analysis[prod_type]["total_cost"] += float(order.estimated_cost or 0)
        
        # Calcular estatísticas para cada tipo
        for prod_type, data in batch_analysis.items():
            quantities = [order.quantity for order in data["orders"]]
            costs = [float(order.estimated_cost or 0) for order in data["orders"]]
            
            data["avg_quantity"] = np.mean(quantities) if quantities else 0
            data["quantity_std"] = np.std(quantities) if quantities else 0
            data["avg_cost_per_unit"] = np.mean([c/q for c, q in zip(costs, quantities) if q > 0]) if costs and quantities else 0
        
        # Identificar oportunidades
        optimization_opportunities = []
        
        for prod_type, data in batch_analysis.items():
            if data["quantity_std"] > data["avg_quantity"] * 0.5:  # Alta variabilidade
                optimal_batch_size = self._calculate_optimal_batch_size(data)
                
                optimization_opportunities.append({
                    "production_type": prod_type,
                    "current_avg_quantity": round(data["avg_quantity"], 2),
                    "recommended_quantity": optimal_batch_size,
                    "estimated_savings": data["total_cost"] * 0.07,  # 7% economia estimada
                    "rationale": "Padronizar tamanhos de lote para melhor eficiência"
                })
        
        return {
            "analysis_type": "batch_size_optimization",
            "production_types_analyzed": len(batch_analysis),
            "optimization_opportunities": optimization_opportunities,
            "total_savings_potential": sum(opt["estimated_savings"] for opt in optimization_opportunities)
        }
    
    def _calculate_optimal_batch_size(self, batch_data: Dict[str, Any]) -> float:
        """Calcular tamanho de lote ótimo baseado em dados históricos"""
        
        # Simplificação: usar média com ajuste para padrão da indústria
        current_avg = batch_data["avg_quantity"]
        
        # Ajustes baseados no tipo de produção
        if "small" in str(batch_data.get("production_type", "")):
            return max(1, int(current_avg * 0.8))  # Reduzir 20%
        elif "large" in str(batch_data.get("production_type", "")):
            return int(current_avg * 1.2)  # Aumentar 20%
        else:
            return int(current_avg)  # Manter
    
    async def _analyze_production_efficiency(
        self,
        db: Session,
        historical_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analisar eficiência de produção"""
        
        production_orders = historical_data["production_orders"]
        metrics = historical_data["metrics"]
        
        # Calcular métricas de eficiência
        completed_orders = [o for o in production_orders if o.status == ProductionStatus.COMPLETED]
        
        if not completed_orders:
            return {"analysis_type": "production_efficiency", "message": "Nenhuma ordem completada para análise"}
        
        # Calcular eficiência por tipo de produção
        efficiency_by_type = {}
        
        for order in completed_orders:
            prod_type = order.production_type
            
            if prod_type not in efficiency_by_type:
                efficiency_by_type[prod_type] = {
                    "orders": [],
                    "avg_cost_variance": 0,
                    "avg_time_variance": 0,
                    "success_rate": 0
                }
            
            efficiency_by_type[prod_type]["orders"].append(order)
        
        # Calcular métricas para cada tipo
        for prod_type, data in efficiency_by_type.items():
            orders = data["orders"]
            
            # Variância de custo
            cost_variances = [
                abs(float(o.cost_variance or 0)) for o in orders
                if o.cost_variance is not None
            ]
            data["avg_cost_variance"] = np.mean(cost_variances) if cost_variances else 0
            
            # Taxa de sucesso (pedidos entregue no prazo)
            on_time_deliveries = sum(
                1 for o in orders
                if o.actual_end and o.scheduled_end and o.actual_end <= o.scheduled_end
            )
            data["success_rate"] = (on_time_deliveries / len(orders) * 100) if orders else 0
        
        # Identificar ineficiências
        efficiency_issues = []
        
        for prod_type, data in efficiency_by_type.items():
            if data["avg_cost_variance"] > 100:  # Alta variância de custo
                efficiency_issues.append({
                    "issue_type": "high_cost_variance",
                    "production_type": prod_type,
                    "severity": "high" if data["avg_cost_variance"] > 200 else "medium",
                    "current_variance": round(data["avg_cost_variance"], 2),
                    "recommendation": "Padronizar processos e controles de custo"
                })
            
            if data["success_rate"] < 90:  # Taxa de sucesso baixa
                efficiency_issues.append({
                    "issue_type": "low_success_rate",
                    "production_type": prod_type,
                    "severity": "high" if data["success_rate"] < 70 else "medium",
                    "current_rate": round(data["success_rate"], 2),
                    "recommendation": "Melhorar planejamento e execução"
                })
        
        return {
            "analysis_type": "production_efficiency",
            "efficiency_metrics": efficiency_by_type,
            "efficiency_issues": efficiency_issues,
            "total_orders_analyzed": len(completed_orders),
            "improvement_potential": len(efficiency_issues) * 0.05  # 5% por issue
        }
    
    async def _analyze_quality_cost_balance(
        self,
        db: Session,
        historical_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analisar balanceamento qualidade-custo"""
        
        budgets = historical_data["budgets"]
        production_orders = historical_data["production_orders"]
        
        # Análise de qualidade vs custo por orçamento
        quality_cost_analysis = []
        
        for budget in budgets:
            quality_score = getattr(budget, 'quality_score', 50.0)
            total_cost = float(budget.preco_final or 0)
            complexity_score = getattr(budget, 'complexidade_score', 0.5)
            
            quality_cost_analysis.append({
                "budget_id": str(budget.id),
                "quality_score": quality_score,
                "total_cost": total_cost,
                "complexity_score": complexity_score,
                "cost_per_quality_point": total_cost / max(quality_score, 1)
            })
        
        # Calcular benchmarks
        if quality_cost_analysis:
            avg_cost_per_quality = np.mean([item["cost_per_quality_point"] for item in quality_cost_analysis])
            quality_cost_ratio = np.mean([item["quality_score"] / item["total_cost"] * 1000 for item in quality_cost_analysis])
        else:
            avg_cost_per_quality = 0
            quality_cost_ratio = 0
        
        # Identificar oportunidades de melhoria
        improvement_opportunities = []
        
        for item in quality_cost_analysis:
            if item["cost_per_quality_point"] > avg_cost_per_quality * 1.2:
                improvement_opportunities.append({
                    "budget_id": item["budget_id"],
                    "issue": "high_cost_per_quality",
                    "current_cost_per_quality": round(item["cost_per_quality_point"], 2),
                    "benchmark_cost_per_quality": round(avg_cost_per_quality, 2),
                    "potential_savings": (item["cost_per_quality_point"] - avg_cost_per_quality) * item["quality_score"] * 0.1,
                    "recommendation": "Otimizar processo para melhor relação qualidade-custo"
                })
        
        return {
            "analysis_type": "quality_cost_balance",
            "budgets_analyzed": len(quality_cost_analysis),
            "benchmark_metrics": {
                "avg_cost_per_quality_point": round(avg_cost_per_quality, 2),
                "quality_cost_ratio": round(quality_cost_ratio, 4)
            },
            "improvement_opportunities": improvement_opportunities,
            "optimization_potential": len(improvement_opportunities) * 0.08  # 8% por oportunidade
        }
    
    async def _analyze_workflow_optimization(
        self,
        db: Session,
        historical_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analisar otimização de fluxo de trabalho"""
        
        production_orders = historical_data["production_orders"]
        
        # Analisar tempos de ciclo por tipo de produção
        cycle_time_analysis = {}
        
        for order in production_orders:
            if order.actual_start and order.actual_end:
                cycle_time = (order.actual_end - order.actual_start).total_seconds() / 3600
                prod_type = order.production_type
                
                if prod_type not in cycle_time_analysis:
                    cycle_time_analysis[prod_type] = []
                
                cycle_time_analysis[prod_type].append(cycle_time)
        
        # Calcular estatísticas de tempo de ciclo
        cycle_stats = {}
        for prod_type, times in cycle_time_analysis.items():
            cycle_stats[prod_type] = {
                "avg_cycle_time": np.mean(times),
                "min_cycle_time": np.min(times),
                "max_cycle_time": np.max(times),
                "std_cycle_time": np.std(times)
            }
        
        # Identificar gargalos
        bottlenecks = []
        for prod_type, stats in cycle_stats.items():
            if stats["std_cycle_time"] > stats["avg_cycle_time"] * 0.5:
                bottlenecks.append({
                    "production_type": prod_type,
                    "issue": "high_cycle_time_variability",
                    "avg_cycle_time": round(stats["avg_cycle_time"], 2),
                    "variability": round(stats["std_cycle_time"], 2),
                    "recommendation": "Padronizar processo para reduzir variabilidade"
                })
        
        return {
            "analysis_type": "workflow_optimization",
            "cycle_time_analysis": {k: {key: round(val, 2) for key, val in v.items()} for k, v in cycle_stats.items()},
            "bottlenecks_identified": bottlenecks,
            "optimization_opportunities": len(bottlenecks) * 0.06  # 6% por gargalo
        }
    
    async def _analyze_energy_optimization(
        self,
        db: Session,
        historical_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analisar otimização de energia"""
        
        # Implementação simplificada - seria mais complexa com dados reais
        return {
            "analysis_type": "energy_optimization",
            "current_energy_consumption": "estimated_24_kwh_per_order",
            "optimization_opportunities": [
                {
                    "type": "equipment_scheduling",
                    "description": "Otimizar agendamento de equipamentos para reduzir consumo em horários de pico",
                    "estimated_savings": "15% redução no custo de energia"
                },
                {
                    "type": "equipment_maintenance",
                    "description": "Manutenção preventiva para manter eficiência energética",
                    "estimated_savings": "10% redução no consumo"
                }
            ],
            "potential_monthly_savings": 150.0
        }
    
    async def _analyze_labor_optimization(
        self,
        db: Session,
        historical_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analisar otimização de mão de obra"""
        
        production_orders = historical_data["production_orders"]
        
        # Analisar eficiência de mão de obra
        labor_efficiency = {}
        
        for order in production_orders:
            if order.labor_hours_estimated and order.actual_cost:
                hours = float(order.labor_hours_estimated)
                cost = float(order.actual_cost)
                
                # Calcular custo por hora
                if hours > 0:
                    cost_per_hour = cost / hours
                    
                    if order.production_type not in labor_efficiency:
                        labor_efficiency[order.production_type] = []
                    
                    labor_efficiency[order.production_type].append({
                        "cost_per_hour": cost_per_hour,
                        "hours": hours,
                        "efficiency": cost_per_hour / 50  # Benchmark R$ 50/hora
                    })
        
        # Calcular métricas de eficiência
        efficiency_metrics = {}
        for prod_type, data in labor_efficiency.items():
            costs_per_hour = [item["cost_per_hour"] for item in data]
            efficiency_scores = [item["efficiency"] for item in data]
            
            efficiency_metrics[prod_type] = {
                "avg_cost_per_hour": np.mean(costs_per_hour),
                "avg_efficiency_score": np.mean(efficiency_scores),
                "efficiency_variance": np.std(efficiency_scores)
            }
        
        return {
            "analysis_type": "labor_optimization",
            "efficiency_metrics": efficiency_metrics,
            "optimization_opportunities": [
                {
                    "type": "skill_standardization",
                    "description": "Padronizar habilidades necessárias por tipo de produção",
                    "potential_improvement": "12% na eficiência de mão de obra"
                },
                {
                    "type": "cross_training",
                    "description": "Treinar funcionários em múltiplas operações",
                    "potential_improvement": "8% na flexibilidade operacional"
                }
            ]
        }
    
    def _consolidate_recommendations(self, optimization_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Consolidar recomendações de múltiplas análises"""
        
        consolidated = []
        
        for analysis_type, results in optimization_results.items():
            if "recommendations" in results:
                for rec in results["recommendations"]:
                    rec["analysis_source"] = analysis_type
                    rec["priority_score"] = self._calculate_priority_score(rec, results)
                    consolidated.append(rec)
            
            elif "optimization_opportunities" in results:
                for opportunity in results["optimization_opportunities"]:
                    opportunity["analysis_source"] = analysis_type
                    opportunity["priority_score"] = self._calculate_priority_score(opportunity, results)
                    consolidated.append(opportunity)
        
        return consolidated
    
    def _calculate_priority_score(self, recommendation: Dict[str, Any], analysis_results: Dict[str, Any]) -> float:
        """Calcular score de prioridade para recomendação"""
        
        score = 0.0
        
        # Base score por tipo de análise
        type_scores = {
            "material_optimization": 8.0,
            "supplier_consolidation": 7.0,
            "batch_size_optimization": 6.0,
            "production_efficiency": 9.0,
            "quality_cost_balance": 5.0,
            "workflow_optimization": 7.0,
            "energy_optimization": 4.0,
            "labor_optimization": 6.0
        }
        
        source_type = recommendation.get("analysis_source", "")
        score += type_scores.get(source_type, 5.0)
        
        # Ajustar por savings potential
        savings = recommendation.get("estimated_savings", recommendation.get("potential_savings", 0))
        if savings > 1000:
            score += 3.0
        elif savings > 500:
            score += 2.0
        elif savings > 100:
            score += 1.0
        
        # Ajustar por esforço de implementação
        effort = recommendation.get("implementation_effort", recommendation.get("implementation_timeline", "medium"))
        if "easy" in str(effort).lower():
            score += 2.0
        elif "hard" in str(effort).lower():
            score -= 1.0
        
        # Ajustar por risco
        risk = recommendation.get("risk_level", "medium")
        if "low" in str(risk).lower():
            score += 1.0
        elif "high" in str(risk).lower():
            score -= 1.0
        
        return round(score, 2)
    
    def _calculate_total_impact(self, optimization_results: Dict[str, Any]) -> Dict[str, float]:
        """Calcular impacto total das otimizações"""
        
        total_savings = 0.0
        total_improvements = 0.0
        analysis_count = 0
        
        for results in optimization_results.values():
            # Extrair savings
            if "estimated_savings" in results:
                total_savings += results["estimated_savings"]
            elif "total_savings_potential" in results:
                total_savings += results["total_savings_potential"]
            
            # Extrair improvements
            if "optimization_potential" in results:
                total_improvements += results["optimization_potential"]
            elif "improvement_potential" in results:
                total_improvements += results["improvement_potential"]
            
            analysis_count += 1
        
        return {
            "total_estimated_savings": round(total_savings, 2),
            "total_improvement_percentage": round(total_improvements * 100, 2),
            "analyses_completed": analysis_count,
            "average_improvement_per_analysis": round((total_improvements / max(analysis_count, 1)) * 100, 2)
        }
    
    def _prioritize_by_roi(self, recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Priorizar recomendações por ROI"""
        
        # Calcular ROI para cada recomendação
        for rec in recommendations:
            savings = rec.get("estimated_savings", rec.get("potential_savings", 0))
            implementation_cost = rec.get("implementation_cost", savings * 0.1)  # 10% do savings
            
            if implementation_cost > 0:
                rec["roi_percentage"] = ((savings - implementation_cost) / implementation_cost) * 100
            else:
                rec["roi_percentage"] = 0
            
            # Score combinado (priority + ROI)
            priority_score = rec.get("priority_score", 5.0)
            roi_score = min(rec["roi_percentage"] / 10, 10)  # Normalizar ROI
            rec["combined_score"] = priority_score + roi_score
        
        # Ordenar por score combinado
        return sorted(recommendations, key=lambda x: x["combined_score"], reverse=True)
    
    def _create_implementation_roadmap(self, recommendations: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Criar roadmap de implementação baseado em prioridade"""
        
        roadmap = {
            "immediate": [],  # 0-30 dias
            "short_term": [],  # 1-3 meses
            "medium_term": [],  # 3-6 meses
            "long_term": []  # 6+ meses
        }
        
        for rec in recommendations:
            priority_score = rec.get("combined_score", 5.0)
            effort = rec.get("implementation_effort", "medium").lower()
            
            if priority_score >= 8 and "easy" in effort:
                roadmap["immediate"].append(rec)
            elif priority_score >= 6:
                roadmap["short_term"].append(rec)
            elif priority_score >= 4:
                roadmap["medium_term"].append(rec)
            else:
                roadmap["long_term"].append(rec)
        
        return roadmap