"""
Serviço de Orçamento Automatizado Inteligente - Sprint 5
Integra resultados das simulações físicas para precificação baseada em qualidade
"""

import json
import logging
import asyncio
from typing import Dict, List, Optional, Any, Tuple, Union
from uuid import UUID
from datetime import datetime, timedelta
from enum import Enum
import numpy as np

import httpx
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from backend.core.config import SLANT3D_API_KEY, OCTOPART_API_KEY, DIGIKEY_API_KEY
from backend.models import (
    Model3D, User, Project, Simulation, SimulationResult,
    IntelligentBudget as Budget, BudgetMaterial, BudgetSupplier
)
from backend.schemas.budgeting import (
    IntelligentBudgetCreate, IntelligentBudgetResponse, QualityBasedPricing,
    MaterialRecommendation, SupplierComparison, BudgetTimeline,
    Slant3DQuote, SimulationIntegration
)

logger = logging.getLogger(__name__)

class QualityScore(Enum):
    """Classificação de qualidade baseada em simulações"""
    EXCELLENT = "excellent"      # 90-100
    GOOD = "good"               # 75-89
    ACCEPTABLE = "acceptable"   # 60-74
    POOR = "poor"               # 40-59
    FAILED = "failed"           # 0-39

class PricingMultiplier(Enum):
    """Multiplicadores de preço baseados na qualidade"""
    EXCELLENT = 1.5     # +50% premium por qualidade
    GOOD = 1.2          # +20% por boa qualidade
    ACCEPTABLE = 1.0    # Preço base
    POOR = 0.8          # -20% desconto
    FAILED = 0.6        # -40% desconto por falhas

class IntelligentBudgetingService:
    """
    Serviço para cálculo automatizado de orçamentos baseado em simulações físicas
    Integra com Sprint 4 para precificação inteligente
    """
    
    def __init__(self):
        # Configurações de precificação baseadas na qualidade
        self.quality_multipliers = {
            QualityScore.EXCELLENT: PricingMultiplier.EXCELLENT.value,
            QualityScore.GOOD: PricingMultiplier.GOOD.value,
            QualityScore.ACCEPTABLE: PricingMultiplier.ACCEPTABLE.value,
            QualityScore.POOR: PricingMultiplier.POOR.value,
            QualityScore.FAILED: PricingMultiplier.FAILED.value
        }
        
        # Preços base de materiais por kg (R$) - melhorados para 2025
        self.base_material_prices = {
            "PLA": 45.0,
            "ABS": 55.0,
            "PETG": 65.0,
            "Nylon": 120.0,
            "Metal": 180.0,
            "Composite": 200.0,
            "Resin": 150.0,
            "TPU": 85.0
        }
        
        # Custos de impressão por hora (R$/h) - ajustados por qualidade
        self.base_printing_cost_per_hour = 25.0
        
        # Custos de montagem base (R$/hora)
        self.base_assembly_cost_per_hour = 50.0
        
        # Configuração de APIs
        self.slant3d_base_url = "https://api.slant3d.com/v1"
        self.octopart_base_url = "https://api.octopart.com/v4"
        self.digikey_base_url = "https://api.digikey.com/v1"
        
        # Cache para otimização
        self._material_cache = {}
        self._supplier_cache = {}
        
    async def create_intelligent_budget(
        self, 
        db: Session, 
        budget_data: IntelligentBudgetCreate
    ) -> Budget:
        """
        Criar orçamento automatizado inteligente baseado em simulações
        
        Args:
            db: Sessão do banco de dados
            budget_data: Dados do orçamento com integração de simulação
            
        Returns:
            Orçamento calculado com base na qualidade da simulação
        """
        try:
            # 1. Obter dados do projeto e modelo 3D
            project = db.query(Project).filter(Project.id == budget_data.projeto_id).first()
            if not project:
                raise ValueError("Projeto não encontrado")
            
            model_3d = db.query(Model3D).filter(Model3D.projeto_id == project.id).first()
            if not model_3d:
                raise ValueError("Modelo 3D não encontrado para o projeto")
            
            # 2. Obter resultados da simulação (Sprint 4)
            simulation_results = None
            quality_score = 50.0  # Default se não houver simulação
            
            if budget_data.simulation_id:
                simulation = db.query(Simulation).filter(
                    and_(
                        Simulation.id == budget_data.simulation_id,
                        Simulation.modelo_id == model_3d.id
                    )
                ).first()
                
                if simulation and simulation.resultados:
                    simulation_results = simulation.resultados
                    quality_score = self._extract_quality_score(simulation_results)
            
            # 3. Analisar resultados da simulação para precificação
            quality_analysis = self._analyze_simulation_results(
                simulation_results, quality_score
            )
            
            # 4. Calcular orçamento inteligente
            budget_calculation = await self._calculate_intelligent_budget(
                project, model_3d, quality_analysis, budget_data
            )
            
            # 5. Criar registro no banco
            budget = Budget(
                projeto_id=budget_data.projeto_id,
                simulation_id=budget_data.simulation_id,
                quality_score=quality_score,
                quality_classification=self._classify_quality(quality_score),
                quality_multiplier=self.quality_multipliers[
                    self._classify_quality(quality_score)
                ],
                custo_material=budget_calculation["custo_material"],
                custo_componentes=budget_calculation["custo_componentes"],
                custo_impressao=budget_calculation["custo_impressao"],
                custo_mao_obra=budget_calculation["custo_mao_obra"],
                tempo_impressao_horas=budget_calculation["tempo_impressao_horas"],
                tempo_montagem_horas=budget_calculation["tempo_montagem_horas"],
                itens_detalhados=budget_calculation["itens_detalhados"],
                fornecedores=budget_calculation["fornecedores"],
                margens_lucro=budget_calculation["margens_lucro"],
                preco_final=budget_calculation["preco_final"],
                justificativas=budget_calculation["justificativas"],
                material_recomendado=budget_calculation["material_recomendado"],
                complexidade_score=budget_calculation["complexidade_score"],
                tempo_entrega_estimado=budget_calculation["tempo_entrega_estimado"]
            )
            
            db.add(budget)
            db.commit()
            db.refresh(budget)
            
            # 6. Atualizar projeto
            project.orcamento_id = budget.id
            project.orcamento_gerado = datetime.now()
            db.commit()
            
            # 7. Buscar recomendações de materiais baseadas na simulação
            if simulation_results:
                await self._store_material_recommendations(
                    db, budget.id, quality_analysis
                )
            
            logger.info(f"Orçamento inteligente criado: {budget.id}")
            return budget
            
        except Exception as e:
            logger.error(f"Erro na criação do orçamento inteligente: {e}")
            db.rollback()
            raise
    
    def _extract_quality_score(self, simulation_results: Dict[str, Any]) -> float:
        """
        Extrair score de qualidade dos resultados da simulação
        Combina múltiplos fatores de qualidade
        """
        if not simulation_results:
            return 50.0
        
        quality_factors = []
        
        # 1. Score geral da simulação
        if "quality_score" in simulation_results:
            quality_factors.append(simulation_results["quality_score"])
        
        # 2. Teste de queda (resistência ao impacto)
        if "drop_test" in simulation_results:
            drop_results = simulation_results["drop_test"]
            if drop_results.get("status") == "success":
                # Bom score para baixa velocidade de impacto
                impact_speed = drop_results.get("velocidade_impacto_media", 5.0)
                drop_score = max(0, 100 - (impact_speed * 10))  # Normalizar
                quality_factors.append(drop_score)
            else:
                quality_factors.append(30.0)  # Score baixo para falhas
        
        # 3. Teste de stress (resistência mecânica)
        if "stress_test" in simulation_results:
            stress_results = simulation_results["stress_test"]
            if stress_results.get("status") == "success":
                max_force = stress_results.get("forca_maxima", 0)
                # Score baseado na força máxima suportada
                stress_score = min(100, (max_force / 1000) * 100)
                quality_factors.append(stress_score)
            else:
                quality_factors.append(40.0)
        
        # 4. Teste de movimento (estabilidade)
        if "motion_test" in simulation_results:
            motion_results = simulation_results["motion_test"]
            if motion_results.get("status") == "success":
                quality_factors.append(75.0)  # Score padrão para sucesso
            else:
                quality_factors.append(50.0)
        
        # 5. Teste de fluido (aerodinâmica)
        if "fluid_test" in simulation_results:
            fluid_results = simulation_results["fluid_test"]
            if fluid_results.get("status") == "success":
                drag_coefficient = fluid_results.get("coeficiente_arraste", 1.0)
                # Bom score para baixo arrasto
                fluid_score = max(0, 100 - (drag_coefficient * 50))
                quality_factors.append(fluid_score)
            else:
                quality_factors.append(60.0)
        
        # Calcular score final (média ponderada)
        if quality_factors:
            return round(np.mean(quality_factors), 2)
        
        return 50.0
    
    def _analyze_simulation_results(
        self, 
        simulation_results: Optional[Dict[str, Any]], 
        quality_score: float
    ) -> Dict[str, Any]:
        """
        Analisar resultados da simulação para extrair insights
        """
        analysis = {
            "quality_score": quality_score,
            "quality_classification": self._classify_quality(quality_score),
            "test_completion_rate": 0.0,
            "material_recommendations": [],
            "performance_metrics": {},
            "failure_points": [],
            "optimization_suggestions": []
        }
        
        if not simulation_results:
            analysis["test_completion_rate"] = 0.0
            analysis["material_recommendations"].append({
                "material": "PLA",
                "reason": "Material padrão - simulações não disponíveis",
                "confidence": 0.5
            })
            return analysis
        
        # Calcular taxa de conclusão dos testes
        test_types = ["drop_test", "stress_test", "motion_test", "fluid_test"]
        completed_tests = sum(1 for test in test_types if test in simulation_results)
        analysis["test_completion_rate"] = completed_tests / len(test_types)
        
        # Analisar cada tipo de teste
        for test_type in test_types:
            if test_type in simulation_results:
                result = simulation_results[test_type]
                if result.get("status") == "success":
                    analysis["performance_metrics"][test_type] = {
                        "status": "passed",
                        "metrics": result
                    }
                else:
                    analysis["failure_points"].append(test_type)
                    analysis["performance_metrics"][test_type] = {
                        "status": "failed",
                        "error": result.get("error", "Unknown error")
                    }
        
        # Gerar recomendações baseadas na qualidade
        if quality_score >= 80:
            analysis["material_recommendations"] = [
                {
                    "material": "High-grade PLA",
                    "reason": "Alta qualidade confirmada por simulações",
                    "confidence": 0.9,
                    "premium": True
                },
                {
                    "material": "PETG",
                    "reason": "Boa resistência para aplicações críticas",
                    "confidence": 0.8
                }
            ]
        elif quality_score >= 60:
            analysis["material_recommendations"] = [
                {
                    "material": "Standard PLA",
                    "reason": "Qualidade aceitável confirmada",
                    "confidence": 0.7
                },
                {
                    "material": "ABS",
                    "reason": "Melhor resistência para aplicações gerais",
                    "confidence": 0.6
                }
            ]
        else:
            analysis["material_recommendations"] = [
                {
                    "material": "Standard PLA",
                    "reason": "Qualidade limitada - material padrão recomendado",
                    "confidence": 0.4
                }
            ]
        
        # Sugestões de otimização
        if quality_score < 60:
            analysis["optimization_suggestions"] = [
                "Considere aumentar a densidade do material",
                "Revise a geometria para melhor resistência",
                "Avalie materiais alternativos mais robustos"
            ]
        
        return analysis
    
    def _classify_quality(self, quality_score: float) -> QualityScore:
        """Classificar qualidade baseada no score"""
        if quality_score >= 90:
            return QualityScore.EXCELLENT
        elif quality_score >= 75:
            return QualityScore.GOOD
        elif quality_score >= 60:
            return QualityScore.ACCEPTABLE
        elif quality_score >= 40:
            return QualityScore.POOR
        else:
            return QualityScore.FAILED
    
    async def _calculate_intelligent_budget(
        self,
        project: Project,
        model_3d: Model3D,
        quality_analysis: Dict[str, Any],
        budget_data: IntelligentBudgetCreate
    ) -> Dict[str, Any]:
        """
        Calcular orçamento completo com base na qualidade da simulação
        """
        calculation = {
            "custo_material": 0.0,
            "custo_componentes": 0.0,
            "custo_impressao": 0.0,
            "custo_mao_obra": 0.0,
            "tempo_impressao_horas": 0.0,
            "tempo_montagem_horas": 0.0,
            "itens_detalhados": [],
            "fornecedores": [],
            "margens_lucro": {},
            "preco_final": 0.0,
            "justificativas": [],
            "material_recomendado": "PLA",
            "complexidade_score": 0.0,
            "tempo_entrega_estimado": 0
        }
        
        quality_score = quality_analysis["quality_score"]
        quality_classification = quality_analysis["quality_classification"]
        quality_multiplier = self.quality_multipliers[quality_classification]
        
        # 1. Calcular custo de material baseado na recomendação da simulação
        material_calculation = await self._calculate_smart_material_cost(
            model_3d, quality_analysis, project.material_tipo
        )
        calculation.update(material_calculation)
        
        # 2. Calcular custo de impressão com ajuste por qualidade
        printing_calculation = await self._calculate_quality_adjusted_printing_cost(
            model_3d, quality_analysis, material_calculation["material_recomendado"]
        )
        calculation.update(printing_calculation)
        
        # 3. Calcular custo de componentes eletrônicos
        if project.componentes_eletronicos:
            components_calculation = await self._calculate_components_cost(
                project.componentes_eletronicos
            )
            calculation.update(components_calculation)
        
        # 4. Calcular custo de montagem
        assembly_calculation = await self._calculate_assembly_cost(
            project, project.componentes_eletronicos or [], quality_analysis
        )
        calculation.update(assembly_calculation)
        
        # 5. Aplicar multiplicador de qualidade
        base_cost = (
            calculation["custo_material"] +
            calculation["custo_componentes"] +
            calculation["custo_impressao"] +
            calculation["custo_mao_obra"]
        )
        
        # 6. Calcular margem de lucro configurável
        margem_percentual = budget_data.margem_lucro_percentual or 25.0
        
        margin_value = base_cost * (margem_percentual / 100)
        adjusted_cost = base_cost * quality_multiplier
        
        calculation["margens_lucro"] = {
            "margem_base_percentual": margem_percentual,
            "margem_valor": margin_value,
            "quality_multiplier": quality_multiplier,
            "adjusted_cost": adjusted_cost,
            "final_price": adjusted_cost + margin_value
        }
        
        # 7. Calcular tempo de entrega
        calculation["tempo_entrega_estimado"] = self._estimate_delivery_time(
            quality_analysis, printing_calculation["tempo_impressao_horas"]
        )
        
        # 8. Gerar justificativas
        calculation["justificativas"] = self._generate_justifications(
            quality_analysis, quality_multiplier, material_calculation
        )
        
        # 9. Calcular score de complexidade
        calculation["complexidade_score"] = self._calculate_complexity_score(
            model_3d, quality_analysis
        )
        
        # 10. Preço final
        calculation["preco_final"] = adjusted_cost + margin_value
        
        return calculation
    
    async def _calculate_smart_material_cost(
        self,
        model_3d: Model3D,
        quality_analysis: Dict[str, Any],
        fallback_material: Optional[str]
    ) -> Dict[str, Any]:
        """Calcular custo de material com recomendações inteligentes"""
        
        # Usar material recomendado pela simulação ou fallback
        recommended_material = "PLA"
        if quality_analysis["material_recommendations"]:
            recommended_material = quality_analysis["material_recommendations"][0]["material"]
        elif fallback_material:
            recommended_material = fallback_material
        
        # Ajustar preço baseado na recomendação
        base_price = self.base_material_prices.get(recommended_material, 45.0)
        confidence = 0.7  # Default
        
        if quality_analysis["material_recommendations"]:
            rec = quality_analysis["material_recommendations"][0]
            confidence = rec.get("confidence", 0.7)
            
            # Premium para recomendações de alta qualidade
            if rec.get("premium", False):
                base_price *= 1.2
        
        # Calcular volume e peso
        volume_mm3 = model_3d.volume_calculado or 100000  # Default
        volume_cm3 = volume_mm3 / 1000
        
        # Densidades por material (g/cm³)
        densities = {
            "PLA": 1.24, "ABS": 1.04, "PETG": 1.27, "Nylon": 1.15,
            "Metal": 2.7, "Composite": 1.8, "Resin": 1.1, "TPU": 1.2
        }
        
        density = densities.get(recommended_material, 1.24)
        weight_grams = volume_cm3 * density
        
        # Adicionar desperdício baseado na qualidade
        waste_multiplier = 1.3 if quality_analysis["quality_score"] < 60 else 1.2
        weight_grams *= waste_multiplier
        
        # Custo final
        material_cost = (weight_grams / 1000) * base_price
        
        item = {
            "descricao": f"Filamento {recommended_material}",
            "quantidade": f"{int(weight_grams)}g",
            "preco_unitario": base_price / 1000,
            "preco_total": material_cost,
            "fornecedor": "Sistema Inteligente",
            "confianca": confidence,
            "justificativa": quality_analysis["material_recommendations"][0]["reason"] if quality_analysis["material_recommendations"] else "Material padrão"
        }
        
        return {
            "custo_material": material_cost,
            "material_recomendado": recommended_material,
            "itens_detalhados": [item]
        }
    
    async def _calculate_quality_adjusted_printing_cost(
        self,
        model_3d: Model3D,
        quality_analysis: Dict[str, Any],
        material: str
    ) -> Dict[str, Any]:
        """Calcular custo de impressão ajustado pela qualidade"""
        
        volume_mm3 = model_3d.volume_calculado or 100000
        volume_cm3 = volume_mm3 / 1000
        
        # Velocidades de impressão por material (cm³/hora) - base
        base_speeds = {
            "PLA": 25.0, "ABS": 20.0, "PETG": 22.0, "Nylon": 15.0,
            "Metal": 10.0, "Composite": 12.0, "Resin": 30.0, "TPU": 18.0
        }
        
        base_speed = base_speeds.get(material, 20.0)
        quality_score = quality_analysis["quality_score"]
        
        # Ajustar velocidade baseada na qualidade
        if quality_score >= 80:
            quality_speed_multiplier = 0.8  # Mais lento para melhor qualidade
        elif quality_score >= 60:
            quality_speed_multiplier = 1.0  # Velocidade normal
        else:
            quality_speed_multiplier = 1.2  # Mais rápido para qualidade baixa
        
        adjusted_speed = base_speed * quality_speed_multiplier
        print_time_hours = volume_cm3 / adjusted_speed
        
        # Custo ajustado pela qualidade
        base_print_cost = print_time_hours * self.base_printing_cost_per_hour
        quality_cost_multiplier = self.quality_multipliers[quality_analysis["quality_classification"]]
        
        # Para impressão, invertemos a lógica (melhor qualidade = menor custo de tempo)
        if quality_score >= 80:
            printing_multiplier = 0.9  # 10% desconto por alta qualidade
        else:
            printing_multiplier = 1.0
        
        adjusted_print_cost = base_print_cost * printing_multiplier * quality_cost_multiplier
        
        item = {
            "descricao": f"Impressão 3D {material} (Qualidade: {quality_analysis['quality_classification'].value})",
            "tempo_horas": round(print_time_hours, 2),
            "custo_hora": self.base_printing_cost_per_hour,
            "preco_total": adjusted_print_cost,
            "fornecedor": "Serviço de Impressão Inteligente",
            "justificativa": f"Tempo ajustado por qualidade ({quality_score:.1f}%)"
        }
        
        return {
            "custo_impressao": adjusted_print_cost,
            "tempo_impressao_horas": print_time_hours,
            "itens_detalhados": [item]
        }
    
    async def _calculate_components_cost(self, components: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calcular custo de componentes eletrônicos (manter implementação existente)"""
        # Implementação similar ao service original, mas com melhorias
        total_cost = 0.0
        detailed_items = []
        suppliers = []
        
        for component in components:
            # Buscar preço via APIs ou estimativa
            estimated_price = self._estimate_component_price(component)
            quantity = component.get("quantidade", 1)
            total_price = estimated_price * quantity
            
            total_cost += total_price
            
            item = {
                "descricao": f"{component.get('tipo', 'Componente').title()} - {component.get('especificacao', '')}",
                "quantidade": quantity,
                "preco_unitario": estimated_price,
                "preco_total": total_price,
                "fornecedor": "Fornecedor Verificado"
            }
            detailed_items.append(item)
        
        return {
            "custo_componentes": total_cost,
            "itens_detalhados": detailed_items,
            "fornecedores": suppliers
        }
    
    def _estimate_component_price(self, component: Dict[str, Any]) -> float:
        """Estimar preço de componente (manter valores atualizados)"""
        component_type = component.get("tipo", "").lower()
        
        # Preços atualizados para 2025 (R$)
        estimated_prices = {
            "sensor": 18.0,
            "atuador": 30.0,
            "microcontroller": 55.0,
            "display": 40.0,
            "comunicacao": 25.0,
            "alimentacao": 20.0
        }
        
        base_price = estimated_prices.get(component_type, 12.0)
        
        # Ajustes por especificação
        specification = component.get("especificacao", "").lower()
        
        if any(x in specification for x in ["arduino", "esp32"]):
            base_price = 60.0
        elif any(x in specification for x in ["lcd", "oled"]):
            base_price = 35.0
        elif any(x in specification for x in ["servomotor", "stepper"]):
            base_price = 45.0
        
        return base_price
    
    async def _calculate_assembly_cost(
        self,
        project: Project,
        components: List[Dict[str, Any]],
        quality_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calcular custo de montagem ajustado pela qualidade"""
        
        # Tempo base por categoria
        base_time_hours = {
            "mecanico": 2.0,
            "eletronico": 4.0,
            "mixto": 6.0,
            "arquitetura": 1.0,
            "decorativo": 1.5
        }
        
        base_time = base_time_hours.get(project.categoria, 3.0)
        
        # Ajustar tempo baseado na qualidade
        quality_score = quality_analysis["quality_score"]
        if quality_score >= 80:
            quality_time_multiplier = 0.8  # Menos tempo para alta qualidade
        elif quality_score >= 60:
            quality_time_multiplier = 1.0  # Tempo normal
        else:
            quality_time_multiplier = 1.3  # Mais tempo para qualidade baixa
        
        # Tempo adicional por componente
        component_time = len(components) * 0.5
        total_time = (base_time + component_time) * quality_time_multiplier
        
        assembly_cost = total_time * self.base_assembly_cost_per_hour
        
        item = {
            "descricao": "Montagem e Acabamento (Ajustado por Qualidade)",
            "tempo_horas": round(total_time, 2),
            "custo_hora": self.base_assembly_cost_per_hour,
            "preco_total": assembly_cost,
            "fornecedor": "Serviço de Montagem",
            "justificativa": f"Tempo ajustado pela qualidade ({quality_analysis['quality_classification'].value})"
        }
        
        return {
            "custo_mao_obra": assembly_cost,
            "tempo_montagem_horas": total_time,
            "itens_detalhados": [item]
        }
    
    def _estimate_delivery_time(
        self,
        quality_analysis: Dict[str, Any],
        print_time_hours: float
    ) -> int:
        """Estimar tempo de entrega em dias"""
        
        base_days = 3  # Tempo base
        
        # Ajustar por qualidade
        quality_score = quality_analysis["quality_score"]
        if quality_score >= 80:
            base_days += 2  # Mais tempo para alta qualidade
        elif quality_score < 60:
            base_days -= 1  # Menos tempo para qualidade baixa
        
        # Ajustar por complexidade da impressão
        if print_time_hours > 10:
            base_days += 1
        
        return max(1, base_days)
    
    def _generate_justifications(
        self,
        quality_analysis: Dict[str, Any],
        quality_multiplier: float,
        material_calculation: Dict[str, Any]
    ) -> List[str]:
        """Gerar justificativas automáticas para o orçamento"""
        
        justifications = []
        
        # Justificativa de qualidade
        quality_score = quality_analysis["quality_score"]
        quality_class = quality_analysis["quality_classification"]
        
        if quality_score >= 80:
            justifications.append(
                f"Premium de {((quality_multiplier - 1) * 100):.0f}% aplicado devido à excelente "
                f"qualidade comprovada por simulações físicas (score: {quality_score:.1f}%)"
            )
        elif quality_score < 60:
            justifications.append(
                f"Desconto de {((1 - quality_multiplier) * 100):.0f}% aplicado devido à qualidade "
                f"limitada demonstrada nas simulações (score: {quality_score:.1f}%)"
            )
        
        # Justificativa de material
        if "justificativa" in material_calculation.get("itens_detalhados", [{}])[0]:
            justifications.append(
                f"Material {material_calculation['material_recomendado']} recomendado: "
                f"{material_calculation['itens_detalhados'][0]['justificativa']}"
            )
        
        # Justificativa de testes
        test_rate = quality_analysis["test_completion_rate"]
        if test_rate < 1.0:
            justifications.append(
                f"Orçamento baseado em {test_rate*100:.0f}% dos testes físicos completados. "
                f"Testes recomendados: {', '.join(quality_analysis['failure_points'])}"
            )
        
        return justifications
    
    def _calculate_complexity_score(
        self,
        model_3d: Model3D,
        quality_analysis: Dict[str, Any]
    ) -> float:
        """Calcular score de complexidade do modelo"""
        
        complexity_factors = []
        
        # Fator de volume
        volume_mm3 = model_3d.volume_calculado or 100000
        volume_score = min(1.0, volume_mm3 / 1000000)  # Normalizar por 1M mm³
        complexity_factors.append(volume_score)
        
        # Fator de qualidade (modelos de baixa qualidade podem ser mais simples)
        quality_score = quality_analysis["quality_score"] / 100
        complexity_factors.append(1.0 - quality_score * 0.5)  # Inverter
        
        # Fator de testes completados
        test_rate = quality_analysis["test_completion_rate"]
        complexity_factors.append(test_rate)
        
        return round(np.mean(complexity_factors), 3)
    
    async def _store_material_recommendations(
        self,
        db: Session,
        budget_id: UUID,
        quality_analysis: Dict[str, Any]
    ):
        """Armazenar recomendações de materiais no banco"""
        
        for recommendation in quality_analysis["material_recommendations"]:
            budget_material = BudgetMaterial(
                budget_id=budget_id,
                material=recommendation["material"],
                confidence=recommendation["confidence"],
                reason=recommendation["reason"],
                is_premium=recommendation.get("premium", False)
            )
            db.add(budget_material)
        
        db.commit()
    
    # ========== MÉTODOS PÚBLICOS PARA API ==========
    
    async def get_budget_by_id(self, db: Session, budget_id: UUID) -> Optional[Budget]:
        """Obter orçamento por ID"""
        return db.query(Budget).filter(Budget.id == budget_id).first()
    
    async def recalculate_budget(
        self,
        db: Session,
        budget_id: UUID,
        new_quality_score: Optional[float] = None,
        new_margin: Optional[float] = None
    ) -> Budget:
        """Recalcular orçamento com novos parâmetros"""
        
        budget = db.query(Budget).filter(Budget.id == budget_id).first()
        if not budget:
            raise ValueError("Orçamento não encontrado")
        
        # Atualizar score de qualidade se fornecido
        if new_quality_score is not None:
            budget.quality_score = new_quality_score
            budget.quality_classification = self._classify_quality(new_quality_score)
            budget.quality_multiplier = self.quality_multipliers[budget.quality_classification]
        
        # Atualizar margem se fornecida
        if new_margin is not None:
            budget.margens_lucro["margem_base_percentual"] = new_margin
            
            # Recalcular preço final
            base_cost = (
                budget.custo_material +
                budget.custo_componentes +
                budget.custo_impressao +
                budget.custo_mao_obra
            )
            
            adjusted_cost = base_cost * budget.quality_multiplier
            margin_value = adjusted_cost * (new_margin / 100)
            budget.preco_final = adjusted_cost + margin_value
        
        db.commit()
        db.refresh(budget)
        
        return budget
    
    async def get_material_recommendations(
        self, db: Session, budget_id: UUID
    ) -> List[Dict[str, Any]]:
        """Obter recomendações de materiais para um orçamento"""
        
        budget = db.query(Budget).filter(Budget.id == budget_id).first()
        if not budget:
            return []
        
        materials = db.query(BudgetMaterial).filter(
            BudgetMaterial.budget_id == budget_id
        ).all()
        
        return [material.__dict__ for material in materials]
    
    async def compare_suppliers(
        self, db: Session, budget_id: UUID
    ) -> Dict[str, Any]:
        """Comparar fornecedores para um orçamento"""
        
        budget = db.query(Budget).filter(Budget.id == budget_id).first()
        if not budget:
            return {}
        
        # Implementação básica - pode ser expandida
        return {
            "comparison": [
                {
                    "supplier": "Fornecedor Principal",
                    "total_cost": budget.preco_final,
                    "delivery_time": budget.tempo_entrega_estimado,
                    "quality_rating": 4.5
                },
                {
                    "supplier": "Alternativo",
                    "total_cost": budget.preco_final * 0.95,
                    "delivery_time": budget.tempo_entrega_estimado + 2,
                    "quality_rating": 4.2
                }
            ]
        }