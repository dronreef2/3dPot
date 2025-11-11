"""
Serviço de Orçamento Automatizado - Octopart & DigiKey
Cálculo automático de custos de materiais e componentes
"""

import json
import logging
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from uuid import UUID

import httpx
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import and_

from ..core.config import OCTOPART_API_KEY, DIGIKEY_API_KEY
from ..models import Budget, Project, Model3D
from ..schemas import BudgetCreate, ItemDetalhado, Fornecedor

logger = logging.getLogger(__name__)

class BudgetingService:
    """Serviço para cálculo automatizado de orçamentos"""
    
    def __init__(self):
        self.octopart_base_url = "https://api.octopart.com/v4"
        self.digikey_base_url = "https://api.digikey.com/v1"
        
        self.octopart_headers = {
            "X-API-KEY": OCTOPART_API_KEY,
            "Content-Type": "application/json"
        }
        
        self.digikey_headers = {
            "X-DigiKey-Api-Key": DIGIKEY_API_KEY,
            "Content-Type": "application/json"
        }
        
        # Preços de materiais por kg (R$)
        self.material_prices = {
            "PLA": 45.0,
            "ABS": 55.0,
            "PETG": 65.0,
            "nylon": 120.0,
            "metal": 180.0,
            "composite": 200.0
        }
        
        # Custos de impressão por hora (R$/h)
        self.printing_cost_per_hour = 25.0
        
        # Custos de montagem (R$/hora)
        self.assembly_cost_per_hour = 50.0
    
    async def create_budget(self, db: Session, budget_data: BudgetCreate) -> Budget:
        """
        Criar orçamento automatizado para um projeto
        
        Args:
            db: Sessão do banco de dados
            budget_data: Dados do orçamento
            
        Returns:
            Orçamento calculado
        """
        try:
            # Obter projeto e modelo 3D
            project = db.query(Project).filter(Project.id == budget_data.projeto_id).first()
            if not project:
                raise ValueError("Projeto não encontrado")
            
            model_3d = db.query(Model3D).filter(Model3D.projeto_id == project.id).first()
            if not model_3d:
                raise ValueError("Modelo 3D não encontrado para o projeto")
            
            # Calcular custos automaticamente
            budget_calculation = await self._calculate_project_budget(project, model_3d)
            
            # Criar registro no banco
            budget = Budget(
                projeto_id=budget_data.projeto_id,
                custo_material=budget_calculation["custo_material"],
                custo_componentes=budget_calculation["custo_componentes"],
                custo_impressao=budget_calculation["custo_impressao"],
                custo_mao_obra=budget_calculation["custo_mao_obra"],
                tempo_impressao_horas=budget_calculation["tempo_impressao_horas"],
                tempo_montagem_horas=budget_calculation["tempo_montagem_horas"],
                itens_detalhados=budget_calculation["itens_detalhados"],
                fornecedores=budget_calculation["fornecedores"],
                margem_lucro_percentual=budget_data.margem_lucro_percentual,
                preco_final=budget_calculation["preco_final"]
            )
            
            db.add(budget)
            db.commit()
            db.refresh(budget)
            
            # Atualizar projeto
            project.orcamento_id = budget.id
            project.orcamento_gerado = asyncio.get_event_loop().time()
            db.commit()
            
            return budget
            
        except Exception as e:
            logger.error(f"Erro na criação do orçamento: {e}")
            db.rollback()
            raise
    
    async def _calculate_project_budget(self, project: Project, model_3d: Model3D) -> Dict[str, Any]:
        """Calcular orçamento completo do projeto"""
        calculation = {
            "custo_material": 0.0,
            "custo_componentes": 0.0,
            "custo_impressao": 0.0,
            "custo_mao_obra": 0.0,
            "tempo_impressao_horas": 0.0,
            "tempo_montagem_horas": 0.0,
            "itens_detalhados": [],
            "fornecedores": [],
            "preco_final": 0.0
        }
        
        # 1. Calcular custo de material
        material_cost_info = await self._calculate_material_cost(project, model_3d)
        calculation.update(material_cost_info)
        
        # 2. Calcular custo de componentes eletrônicos
        if project.componentes_eletronicos:
            components_cost_info = await self._calculate_components_cost(
                project.componentes_eletronicos
            )
            calculation.update(components_cost_info)
        
        # 3. Calcular custo de impressão
        printing_cost_info = await self._calculate_printing_cost(
            model_3d, project.material_tipo
        )
        calculation.update(printing_cost_info)
        
        # 4. Estimar custo de montagem
        assembly_cost_info = await self._calculate_assembly_cost(
            project, project.componentes_eletronicos or []
        )
        calculation.update(assembly_cost_info)
        
        # 5. Calcular preço final com margem
        calculation["preco_final"] = (
            calculation["custo_material"] +
            calculation["custo_componentes"] +
            calculation["custo_impressao"] +
            calculation["custo_mao_obra"]
        )
        
        return calculation
    
    async def _calculate_material_cost(self, project: Project, model_3d: Model3D) -> Dict[str, Any]:
        """Calcular custo do material de impressão"""
        material_type = project.material_tipo or "PLA"
        volume_cm3 = model_3d.volume_calculado or 0
        
        # Converter volume de mm³ para cm³
        volume_cm3 = volume_cm3 / 1000
        
        # Calcular peso do objeto (densidade em g/cm³)
        densities = {
            "PLA": 1.24,
            "ABS": 1.04,
            "PETG": 1.27,
            "nylon": 1.15,
            "metal": 2.7,
            "composite": 1.8
        }
        
        density = densities.get(material_type.upper(), 1.24)
        weight_grams = volume_cm3 * density
        
        # Adicionar desperdício (20%)
        weight_grams *= 1.2
        
        # Custo do material
        material_price_per_kg = self.material_prices.get(material_type.upper(), 45.0)
        material_cost = (weight_grams / 1000) * material_price_per_kg
        
        item = ItemDetalhado(
            descricao=f"Filamento {material_type}",
            quantidade=int(weight_grams / 1000 * 1000),  # em metros de filamento
            preco_unitario=material_price_per_kg / 1000,  # por grama
            preco_total=material_cost,
            fornecedor="Loja Local de Filamentos"
        )
        
        return {
            "custo_material": material_cost,
            "itens_detalhados": [item.dict()]
        }
    
    async def _calculate_components_cost(self, components: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calcular custo de componentes eletrônicos via APIs"""
        total_cost = 0.0
        detailed_items = []
        suppliers = []
        
        # Processar componentes em paralelo
        tasks = [self._get_component_price(component) for component in components]
        component_prices = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, (component, price_result) in enumerate(zip(components, component_prices)):
            if isinstance(price_result, Exception):
                logger.warning(f"Erro ao buscar preço para {component}: {price_result}")
                # Usar preço estimado
                estimated_price = self._estimate_component_price(component)
                price_result = {
                    "price": estimated_price,
                    "supplier": "Estimativa",
                    "availability": "disponível"
                }
            
            quantity = component.get("quantidade", 1)
            total_price = price_result["price"] * quantity
            
            total_cost += total_price
            
            item = ItemDetalhado(
                descricao=f"{component.get('tipo', 'componente').title()} - {component.get('especificacao', '')}",
                quantidade=quantity,
                preco_unitario=price_result["price"],
                preco_total=total_price,
                fornecedor=price_result["supplier"]
            )
            detailed_items.append(item.dict())
            
            # Adicionar fornecedor à lista
            if price_result["supplier"] not in [s["nome"] for s in suppliers]:
                supplier = Fornecedor(
                    nome=price_result["supplier"],
                    url=f"https://{price_result['supplier'].lower()}.com",
                    confiabilidade=0.9 if price_result["availability"] == "disponível" else 0.7
                )
                suppliers.append(supplier.dict())
        
        return {
            "custo_componentes": total_cost,
            "itens_detalhados": detailed_items,
            "fornecedores": suppliers
        }
    
    async def _get_component_price(self, component: Dict[str, Any]) -> Dict[str, Any]:
        """Buscar preço de componente via Octopart"""
        component_type = component.get("tipo", "")
        specification = component.get("especificacao", "")
        
        try:
            # Tentar Octopart primeiro
            price = await self._search_octopart(component_type, specification)
            if price:
                return {
                    "price": price,
                    "supplier": "Octopart",
                    "availability": "disponível"
                }
        except Exception as e:
            logger.warning(f"Octopart indisponível: {e}")
        
        # Fallback para DigiKey
        try:
            price = await self._search_digikey(component_type, specification)
            if price:
                return {
                    "price": price,
                    "supplier": "DigiKey",
                    "availability": "disponível"
                }
        except Exception as e:
            logger.warning(f"DigiKey indisponível: {e}")
        
        # Usar preço estimado se APIs indisponíveis
        estimated_price = self._estimate_component_price(component)
        return {
            "price": estimated_price,
            "supplier": "Estimativa",
            "availability": "disponível"
        }
    
    async def _search_octopart(self, component_type: str, specification: str) -> Optional[float]:
        """Buscar componente no Octopart"""
        if not OCTOPART_API_KEY:
            return None
        
        try:
            async with httpx.AsyncClient() as client:
                # Query para buscar componente
                query = f"{component_type} {specification}"
                
                search_data = {
                    "queries": [{
                        "q": query,
                        "limit": 5
                    }]
                }
                
                response = await client.post(
                    f"{self.octopart_base_url}/search",
                    headers=self.octopart_headers,
                    json=search_data,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Extrair preço do primeiro resultado
                    if data.get("results") and len(data["results"]) > 0:
                        first_result = data["results"][0]
                        if "offers" in first_result and first_result["offers"]:
                            # Pegar o menor preço disponível
                            prices = [
                                offer.get("price_breaks", [{}])[-1].get("price", float('inf'))
                                for offer in first_result["offers"]
                                if offer.get("price_breaks")
                            ]
                            if prices:
                                return min([p for p in prices if p != float('inf')])
                
                return None
                
        except Exception as e:
            logger.error(f"Erro na busca Octopart: {e}")
            return None
    
    async def _search_digikey(self, component_type: str, specification: str) -> Optional[float]:
        """Buscar componente no DigiKey"""
        if not DIGIKEY_API_KEY:
            return None
        
        try:
            async with httpx.AsyncClient() as client:
                # DigiKey usa parâmetros de query diferentes
                query = f"{component_type} {specification}"
                
                params = {
                    "keywords": query,
                    "recordcount": 5,
                    "start": 0
                }
                
                response = await client.get(
                    f"{self.digikey_base_url}/search",
                    headers=self.digikey_headers,
                    params=params,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Extrair preço
                    if data.get("products") and len(data["products"]) > 0:
                        first_product = data["products"][0]
                        pricing = first_product.get("productpricing", {})
                        if pricing.get("tierprices"):
                            # Pegar o menor preço
                            prices = [tier["price"] for tier in pricing["tierprices"]]
                            return min(prices)
                
                return None
                
        except Exception as e:
            logger.error(f"Erro na busca DigiKey: {e}")
            return None
    
    def _estimate_component_price(self, component: Dict[str, Any]) -> float:
        """Estimar preço de componente baseado no tipo"""
        component_type = component.get("tipo", "").lower()
        
        # Preços estimados por tipo (R$)
        estimated_prices = {
            "sensor": 15.0,
            "atuador": 25.0,
            "microcontroller": 45.0,
            "display": 35.0,
            "comunicacao": 20.0
        }
        
        base_price = estimated_prices.get(component_type, 10.0)
        
        # Ajustar baseado na especificação
        specification = component.get("especificacao", "").lower()
        
        if "arduino" in specification or "esp32" in specification:
            base_price = 50.0
        elif "lcd" in specification or "oled" in specification:
            base_price = 30.0
        elif "servomotor" in specification or "stepper" in specification:
            base_price = 40.0
        
        return base_price
    
    async def _calculate_printing_cost(self, model_3d: Model3D, material_type: str) -> Dict[str, Any]:
        """Calcular custo de impressão"""
        volume_mm3 = model_3d.volume_calculado or 0
        volume_cm3 = volume_mm3 / 1000  # converter para cm³
        
        # Velocidade de impressão por material (cm³/hora)
        printing_speeds = {
            "PLA": 25.0,
            "ABS": 20.0,
            "PETG": 22.0,
            "nylon": 15.0,
            "metal": 10.0,
            "composite": 12.0
        }
        
        speed = printing_speeds.get(material_type.upper(), 20.0)
        print_time_hours = volume_cm3 / speed
        
        # Custo de impressão
        print_cost = print_time_hours * self.printing_cost_per_hour
        
        item = ItemDetalhado(
            descricao=f"Impressão 3D ({material_type})",
            quantidade=print_time_hours,
            preco_unitario=self.printing_cost_per_hour,
            preco_total=print_cost,
            fornecedor="Serviço de Impressão Local"
        )
        
        return {
            "custo_impressao": print_cost,
            "tempo_impressao_horas": print_time_hours,
            "itens_detalhados": [item.dict()]
        }
    
    async def _calculate_assembly_cost(self, project: Project, components: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calcular custo de montagem"""
        # Tempo base de montagem por tipo de projeto
        base_time_hours = {
            "mecanico": 2.0,
            "eletronico": 4.0,
            "mixto": 6.0,
            "arquitetura": 1.0
        }
        
        base_time = base_time_hours.get(project.categoria, 3.0)
        
        # Adicionar tempo adicional por componente
        component_time = len(components) * 0.5  # 30 min por componente
        
        total_time = base_time + component_time
        assembly_cost = total_time * self.assembly_cost_per_hour
        
        item = ItemDetalhado(
            descricao="Montagem e Acabamento",
            quantidade=total_time,
            preco_unitario=self.assembly_cost_per_hour,
            preco_total=assembly_cost,
            fornecedor="Serviço de Montagem"
        )
        
        return {
            "custo_mao_obra": assembly_cost,
            "tempo_montagem_horas": total_time,
            "itens_detalhados": [item.dict()]
        }
    
    async def generate_proposal_pdf(self, budget: Budget, project: Project) -> str:
        """Gerar proposta em PDF usando WeasyPrint"""
        try:
            from weasyprint import HTML
            from jinja2 import Template
            
            # Template HTML da proposta
            html_template = self._get_proposal_template()
            
            # Preparar dados para o template
            template_data = {
                "project": project,
                "budget": budget,
                "items": budget.itens_detalhados or [],
                "suppliers": budget.fornecedores or [],
                "generated_date": project.orcamento_gerado or asyncio.get_event_loop().time(),
                "proposal_number": budget.numero_proposta or f"ORC-{budget.id[:8]}"
            }
            
            # Renderizar template
            template = Template(html_template)
            html_content = template.render(**template_data)
            
            # Gerar PDF
            pdf_path = self._storage_path / f"proposta_{budget.id}.pdf"
            HTML(string=html_content).write_pdf(str(pdf_path))
            
            # Atualizar orçamento com caminho do PDF
            budget.proposta_pdf_path = str(pdf_path)
            
            return str(pdf_path)
            
        except ImportError:
            logger.warning("WeasyPrint não disponível, gerando proposta em HTML")
            return await self._generate_proposal_html(budget, project)
        except Exception as e:
            logger.error(f"Erro na geração da proposta: {e}")
            raise
    
    def _get_proposal_template(self) -> str:
        """Template HTML da proposta"""
        return """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Proposta de Orççamento - 3dPot</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .header { text-align: center; border-bottom: 2px solid #333; padding-bottom: 20px; }
        .project-info { margin: 20px 0; }
        .items-table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        .items-table th, .items-table td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        .items-table th { background-color: #f2f2f2; }
        .total { font-size: 18px; font-weight: bold; text-align: right; }
        .footer { margin-top: 40px; text-align: center; color: #666; }
    </style>
</head>
<body>
    <div class="header">
        <h1>3dPot - Sistema de Prototipagem</h1>
        <h2>Proposta de Orçamento</h2>
        <p>Número: {{ proposal_number }}<br>
        Data: {{ generated_date }}</p>
    </div>
    
    <div class="project-info">
        <h3>Informações do Projeto</h3>
        <p><strong>Nome:</strong> {{ project.nome }}</p>
        <p><strong>Categoria:</strong> {{ project.categoria }}</p>
        <p><strong>Descrição:</strong> {{ project.descricao_usuario }}</p>
    </div>
    
    <table class="items-table">
        <thead>
            <tr>
                <th>Item</th>
                <th>Quantidade</th>
                <th>Preço Unitário</th>
                <th>Total</th>
                <th>Fornecedor</th>
            </tr>
        </thead>
        <tbody>
            {% for item in items %}
            <tr>
                <td>{{ item.descricao }}</td>
                <td>{{ item.quantidade }}</td>
                <td>R$ {{ "%.2f"|format(item.preco_unitario) }}</td>
                <td>R$ {{ "%.2f"|format(item.preco_total) }}</td>
                <td>{{ item.fornecedor }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
    
    <div class="total">
        <p>Subtotal: R$ {{ "%.2f"|format((budget.custo_material + budget.custo_componentes + budget.custo_impressao + budget.custo_mao_obra)) }}</p>
        <p>Margem ({{ budget.margem_lucro_percentual }}%): R$ {{ "%.2f"|format((budget.preco_final - (budget.custo_material + budget.custo_componentes + budget.custo_impressao + budget.custo_mao_obra))) }}</p>
        <p>TOTAL: R$ {{ "%.2f"|format(budget.preco_final) }}</p>
    </div>
    
    <div class="footer">
        <p>3dPot v2.0 - Prototipagem Sob Demanda</p>
        <p>Tempo estimado de entrega: {{ (budget.tempo_impressao_horas + budget.tempo_montagem_horas) | round(1) }} horas</p>
    </div>
</body>
</html>
"""
    
    async def _generate_proposal_html(self, budget: Budget, project: Project) -> str:
        """Gerar proposta em HTML como fallback"""
        html_content = f"""
        <html>
        <head><title>Proposta {budget.id}</title></head>
        <body>
            <h1>Proposta de Orçamento</h1>
            <h2>Projeto: {project.nome}</h2>
            <p><strong>Total: R$ {budget.preco_final:.2f}</strong></p>
            <p>Esta proposta foi gerada automaticamente pelo sistema 3dPot v2.0</p>
        </body>
        </html>
        """
        
        html_path = self._storage_path / f"proposta_{budget.id}.html"
        html_path.write_text(html_content, encoding='utf-8')
        
        return str(html_path)
    
    def get_budget_by_project(self, db: Session, project_id: UUID) -> Optional[Budget]:
        """Obter orçamento por ID do projeto"""
        return db.query(Budget).filter(Budget.projeto_id == project_id).first()
    
    def update_budget_margin(self, db: Session, budget_id: UUID, new_margin: float) -> Budget:
        """Atualizar margem de lucro do orçamento"""
        budget = db.query(Budget).filter(Budget.id == budget_id).first()
        if not budget:
            raise ValueError("Orçamento não encontrado")
        
        budget.margem_lucro_percentual = new_margin
        
        # Recalcular preço final
        subtotal = (budget.custo_material + budget.custo_componentes + 
                   budget.custo_impressao + budget.custo_mao_obra)
        
        margin_value = subtotal * (new_margin / 100)
        budget.preco_final = subtotal + margin_value
        
        db.commit()
        db.refresh(budget)
        
        return budget