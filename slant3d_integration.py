#!/usr/bin/env python3
"""
Sistema de Modelagem Inteligente com API Slant 3D
Integração completa para automação de impressão 3D
"""

import requests
import json
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class FilamentInfo:
    """Informações sobre filamentos disponíveis"""
    id: str
    name: str
    color: str
    type: str
    available: bool
    price_per_gram: float
    diameter: float
    weight: int

@dataclass
class APIUsage:
    """Informações de uso da API"""
    total_requests: int
    remaining_requests: int
    limit: int
    reset_time: int
    account_tier: str

class Slant3DAPI:
    """Cliente da API Slant 3D"""
    
    def __init__(self, api_key: str):
        """
        Inicializar cliente da API Slant 3D
        
        Args:
            api_key: Chave de API do Slant 3D
        """
        self.api_key = api_key
        self.base_url = "https://slant3dapi.com/v2/api"
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        })
        self.usage_info = None
        
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Fazer requisição HTTP com tratamento de erros
        
        Args:
            method: Método HTTP
            endpoint: Endpoint da API
            **kwargs: Argumentos para requests
            
        Returns:
            Resposta da API
            
        Raises:
            Exception: Em caso de erro na requisição
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            logger.info(f"Fazendo requisição: {method} {url}")
            response = self.session.request(method, url, **kwargs)
            
            # Atualizar informações de uso
            self._update_usage_info(response.headers)
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na requisição: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao decodificar JSON: {e}")
            raise
    
    def _update_usage_info(self, headers: requests.structures.CaseInsensitiveDict):
        """Atualizar informações de uso da API"""
        try:
            self.usage_info = APIUsage(
                total_requests=0,  # Será atualizado conforme necessário
                remaining_requests=int(headers.get('X-RateLimit-Remaining', 0)),
                limit=int(headers.get('X-RateLimit-Limit', 100)),
                reset_time=int(headers.get('X-RateLimit-Reset', 0)),
                account_tier=headers.get('X-RateLimit-Role', 'free')
            )
        except (ValueError, TypeError) as e:
            logger.warning(f"Erro ao atualizar uso da API: {e}")
    
    def get_filaments(self) -> List[FilamentInfo]:
        """
        Obter lista de filamentos disponíveis
        
        Returns:
            Lista de filamentos
        """
        logger.info("Obtendo filamentos disponíveis...")
        
        try:
            data = self._make_request("GET", "/filaments")
            filaments = []
            
            for filament_data in data.get("filaments", []):
                filament = FilamentInfo(
                    id=filament_data.get("id", ""),
                    name=filament_data.get("name", ""),
                    color=filament_data.get("color", ""),
                    type=filament_data.get("type", ""),
                    available=filament_data.get("available", False),
                    price_per_gram=filament_data.get("price_per_gram", 0.0),
                    diameter=filament_data.get("diameter", 1.75),
                    weight=filament_data.get("weight", 1000)
                )
                filaments.append(filament)
            
            logger.info(f"Encontrados {len(filaments)} filamentos")
            return filaments
            
        except Exception as e:
            logger.error(f"Erro ao obter filamentos: {e}")
            return []
    
    def check_usage(self) -> APIUsage:
        """
        Verificar uso atual da API
        
        Returns:
            Informações de uso
        """
        try:
            data = self._make_request("GET", "/usage")
            
            if self.usage_info:
                # Atualizar com dados mais recentes
                self.usage_info.total_requests = data.get("total_requests", 0)
                self.usage_info.remaining_requests = data.get("remaining_requests", 0)
            
            logger.info(f"Uso da API: {self.usage_info.remaining_requests}/{self.usage_info.limit} requests")
            return self.usage_info
            
        except Exception as e:
            logger.error(f"Erro ao verificar uso: {e}")
            return self.usage_info
    
    def filter_filaments(self, filters: Dict[str, Any]) -> List[FilamentInfo]:
        """
        Filtrar filamentos por critérios
        
        Args:
            filters: Critérios de filtro
                - available: Apenas filamentos disponíveis
                - type: Tipo de material (PLA, ABS, PETG, etc.)
                - color: Cor específica
                - diameter: Diâmetro específico
                - max_price: Preço máximo por grama
                
        Returns:
            Lista de filamentos filtrados
        """
        all_filaments = self.get_filaments()
        filtered = all_filaments
        
        if filters.get("available", True):
            filtered = [f for f in filtered if f.available]
        
        if filters.get("type"):
            filtered = [f for f in filtered if f.type.lower() == filters["type"].lower()]
        
        if filters.get("color"):
            filtered = [f for f in filtered if filters["color"].lower() in f.color.lower()]
        
        if filters.get("diameter"):
            filtered = [f for f in filtered if f.diameter == filters["diameter"]]
        
        if filters.get("max_price"):
            filtered = [f for f in filtered if f.price_per_gram <= filters["max_price"]]
        
        return filtered
    
    def estimate_print_cost(self, filament_id: str, model_volume_cm3: float, 
                           material_density: float = 1.24) -> Dict[str, float]:
        """
        Estimar custo de impressão
        
        Args:
            filament_id: ID do filamento
            model_volume_cm3: Volume do modelo em cm³
            material_density: Densidade do material (g/cm³)
            
        Returns:
            Estimativa de custo
        """
        try:
            filaments = self.get_filaments()
            filament = next((f for f in filaments if f.id == filament_id), None)
            
            if not filament:
                raise ValueError(f"Filamento {filament_id} não encontrado")
            
            # Calcular peso do modelo
            model_weight_g = model_volume_cm3 * material_density
            
            # Calcular custo
            material_cost = model_weight_g * filament.price_per_gram
            
            # Adicionar margem de 30% para outros custos
            total_cost = material_cost * 1.30
            
            return {
                "filament_name": filament.name,
                "filament_color": filament.color,
                "model_weight_g": round(model_weight_g, 2),
                "material_cost": round(material_cost, 2),
                "total_cost": round(total_cost, 2),
                "price_per_gram": filament.price_per_gram
            }
            
        except Exception as e:
            logger.error(f"Erro ao estimar custo: {e}")
            return {}

class ModelagemInteligente:
    """Sistema de Modelagem Inteligente"""
    
    def __init__(self, api_key: str, models_dir: str = "modelos-3d"):
        """
        Inicializar sistema de modelagem inteligente
        
        Args:
            api_key: Chave da API Slant 3D
            models_dir: Diretório dos modelos 3D
        """
        self.api = Slant3DAPI(api_key)
        self.models_dir = Path(models_dir)
        self.central_inteligente_dir = self.models_dir / "central-inteligente"
        
    def processar_prompt(self, prompt: str) -> Dict[str, Any]:
        """
        Processar prompt de usuário para gerar sugestões inteligentes
        
        Args:
            prompt: Descrição do modelo desejado
            
        Returns:
            Resultado do processamento
        """
        logger.info(f"Processando prompt: {prompt}")
        
        # Análise de intenção do prompt
        intent = self._analisar_intencao(prompt)
        
        # Gerar sugestões
        sugestoes = self._gerar_sugestoes(intent, prompt)
        
        return {
            "prompt_original": prompt,
            "intencao": intent,
            "sugestoes": sugestoes,
            "recomendacoes": self._gerar_recomendacoes(intent),
            "estimativas": self._gerar_estimativas(intent)
        }
    
    def _analisar_intencao(self, prompt: str) -> Dict[str, Any]:
        """Analisar intenção do prompt"""
        intent = {
            "tipo": "general",
            "materiais_preferidos": [],
            "complexidade": "media",
            "proposito": "prototipo",
            "dimensoes_estimadas": {}
        }
        
        prompt_lower = prompt.lower()
        
        # Detectar tipo de objeto
        if any(word in prompt_lower for word in ["chassi", "base", "estrutura", "case"]):
            intent["tipo"] = "estrutura"
            intent["materiais_preferidos"] = ["PLA", "ABS"]
            intent["complexidade"] = "baixa"
        elif any(word in prompt_lower for word in ["suporte", "holder", "bracket"]):
            intent["tipo"] = "suporte"
            intent["materiais_preferidos"] = ["PLA", "PETG"]
            intent["complexidade"] = "media"
        elif any(word in prompt_lower for word in ["caixa", "enclosure", "gabinete"]):
            intent["tipo"] = "enclosure"
            intent["materiais_preferidos"] = ["ABS", "PETG"]
            intent["complexidade"] = "alta"
        elif any(word in prompt_lower for word in ["projeto", "central", "control"]):
            intent["tipo"] = "central_inteligente"
            intent["materiais_preferidos"] = ["PLA", "PETG"]
            intent["complexidade"] = "alta"
            intent["proposito"] = "producao"
        
        # Detectar proposito
        if any(word in prompt_lower for word in ["estudo", "teste", "validacao", "mockup"]):
            intent["proposito"] = "prototipo"
        elif any(word in prompt_lower for word in ["producao", "final", "comercial"]):
            intent["proposito"] = "producao"
        
        return intent
    
    def _gerar_sugestoes(self, intent: Dict[str, Any], prompt: str) -> List[str]:
        """Gerar sugestões baseadas na intenção"""
        sugestoes = []
        
        # Sugestões de materiais baseadas no tipo
        if intent["tipo"] == "estrutura":
            sugestoes.append("Para estruturas: PLA branco ou ABS cinza são ideais para resistêcia e precisão")
        elif intent["tipo"] == "suporte":
            sugestoes.append("Para suportes: PETG transparente permite visualização interna ou PLA para peças funcionais")
        elif intent["tipo"] == "enclosure":
            sugestoes.append("Para gabinetes: ABS é ideal por sua resistência a impactos e acabamento")
        elif intent["tipo"] == "central_inteligente":
            sugestoes.append("Para projeto central: Use PLA ou PETG para encaixes precisos e durabilidade")
        
        # Sugestões baseadas na complexidade
        if intent["complexidade"] == "alta":
            sugestoes.append("Peças complexas: Considere geração automática de supports no slicer")
            sugestoes.append("Tolerâncias: Adicione folga de 0.2mm para encaixes em peças móveis")
        elif intent["complexidade"] == "media":
            sugestoes.append("Peças médias: Orientação de impressão vertical para melhor resistência")
        
        # Sugestões baseadas no proposito
        if intent["proposito"] == "prototipo":
            sugestoes.append("Prototipagem: Use baixo preenchimento (15-20%) para velocidade")
        elif intent["proposito"] == "producao":
            sugestoes.append("Produção: Use preenchimento 30-50% e qualidade alta para acabamento")
        
        return sugestoes
    
    def _gerar_recomendacoes(self, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Gerar recomendações específicas"""
        # Obter filamentos disponíveis
        filaments = self.api.get_filaments()
        
        # Filtrar por materiais preferidos
        filamentos_sugeridos = []
        for material in intent["materiais_preferidos"]:
            materiais_disponiveis = self.api.filter_filaments({
                "type": material,
                "available": True
            })
            filamentos_sugeridos.extend(materiais_disponiveis[:3])  # Top 3 por material
        
        return {
            "filamentos_recomendados": [
                {
                    "id": f.id,
                    "nome": f.name,
                    "cor": f.color,
                    "tipo": f.type,
                    "preco_por_grama": f.price_per_gram
                }
                for f in filamentos_sugeridos
            ],
            "configuracoes_impressao": {
                "nozzle_temp": "200-220°C" if "PLA" in intent["materiais_preferidos"] else "240-260°C",
                "bed_temp": "60-70°C" if "ABS" in intent["materiais_preferidos"] else "50-60°C",
                "layer_height": "0.2mm",
                "infill": "30%" if intent["proposito"] == "producao" else "20%",
                "print_speed": "50-60mm/s"
            }
        }
    
    def _gerar_estimativas(self, intent: Dict[str, Any]) -> Dict[str, float]:
        """Gerar estimativas de custo e tempo"""
        # Estimativa baseada no tipo de projeto
        estimativas = {}
        
        if intent["tipo"] == "estrutura":
            estimativas.update({
                "tempo_estimado": "2-4 horas",
                "peso_estimado": "50-150g",
                "custo_estimado": "5-15 USD"
            })
        elif intent["tipo"] == "suporte":
            estimativas.update({
                "tempo_estimado": "1-3 horas",
                "peso_estimado": "20-80g",
                "custo_estimado": "2-8 USD"
            })
        elif intent["tipo"] == "enclosure":
            estimativas.update({
                "tempo_estimado": "4-8 horas",
                "peso_estimado": "100-300g",
                "custo_estimado": "10-30 USD"
            })
        elif intent["tipo"] == "central_inteligente":
            estimativas.update({
                "tempo_estimado": "6-12 horas (total projeto)",
                "peso_estimado": "200-500g (total projeto)",
                "custo_estimado": "20-50 USD (total projeto)"
            })
        
        return estimativas
    
    def buscar_filamentos_compatíveis(self, requisitos: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Buscar filamentos compatíveis com requisitos específicos
        
        Args:
            requisitos: Requisitos específicos (material, cor, preço, etc.)
            
        Returns:
            Lista de filamentos compatíveis
        """
        filtros = {}
        
        if "material" in requisitos:
            filtros["type"] = requisitos["material"]
        if "cor" in requisitos:
            filtros["color"] = requisitos["cor"]
        if "max_preco" in requisitos:
            filtros["max_price"] = requisitos["max_preco"]
        if "diametro" in requisitos:
            filtros["diameter"] = requisitos["diametro"]
        
        # Disponível por padrão
        filtros["available"] = requisitos.get("disponiveis_somente", True)
        
        filamentos_filtrados = self.api.filter_filaments(filtros)
        
        return [
            {
                "id": f.id,
                "nome": f.name,
                "cor": f.color,
                "tipo": f.type,
                "disponivel": f.available,
                "preco_por_grama": f.price_per_gram,
                "diametro": f.diameter,
                "peso": f.weight
            }
            for f in filamentos_filtrados
        ]
    
    def calcular_orçamento_completo(self, modelo: str, volume_cm3: float, 
                                   requisitos_filamento: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calcular orçamento completo para impressão
        
        Args:
            modelo: Nome do modelo
            volume_cm3: Volume do modelo em cm³
            requisitos_filamento: Requisitos para o filamento
            
        Returns:
            Orçamento completo com múltiplas opções
        """
        # Buscar filamentos compatíveis
        filamentos = self.buscar_filamentos_compatíveis(requisitos_filamento)
        
        opcoes_orcamento = []
        
        for filament in filamentos[:5]:  # Top 5 opções
            estimativa = self.api.estimate_print_cost(
                filament["id"], 
                volume_cm3
            )
            
            opcoes_orcamento.append({
                "filamento": filament,
                "estimativa": estimativa,
                "vantagens": self._avaliar_qualidade_opcao(filament, estimativa),
                "rating": self._calcular_rating_opcao(filament, estimativa)
            })
        
        # Ordenar por rating
        opcoes_orcamento.sort(key=lambda x: x["rating"], reverse=True)
        
        return {
            "modelo": modelo,
            "volume_modelo_cm3": volume_cm3,
            "numero_opcoes": len(opcoes_orcamento),
            "opcoes": opcoes_orcamento,
            "recomendacao_principal": opcoes_orcamento[0] if opcoes_orcamento else None,
            "total_opcoes_consideradas": len(filamentos)
        }
    
    def _avaliar_qualidade_opcao(self, filament: Dict[str, Any], 
                               estimativa: Dict[str, float]) -> List[str]:
        """Avaliar qualidade de uma opção de filamento"""
        vantagens = []
        
        # Vantagens baseadas no preço
        if estimativa.get("total_cost", 0) < 10:
            vantagens.append("Custo baixo")
        elif estimativa.get("total_cost", 0) < 20:
            vantagens.append("Custo moderado")
        
        # Vantagens baseadas no tipo de material
        if filament["tipo"] == "PLA":
            vantagens.append("Fácil impressão")
            vantagens.append("Boa precisão dimensional")
        elif filament["tipo"] == "ABS":
            vantagens.append("Alta resistência mecânica")
            vantagens.append("Resistente a impactos")
        elif filament["tipo"] == "PETG":
            vantagens.append("Resistente a produtos químicos")
            vantagens.append("Boa transparência")
        
        # Vantagens baseadas no peso do filamento
        if filament["peso"] > 1000:
            vantagens.append("Filamento de qualidade profissional")
        
        return vantagens
    
    def _calcular_rating_opcao(self, filament: Dict[str, Any], 
                             estimativa: Dict[str, float]) -> float:
        """Calcular rating de uma opção (0-10)"""
        rating = 5.0  # Base
        
        # Fator de preço (mais barato = melhor)
        custo = estimativa.get("total_cost", 20)
        if custo < 5:
            rating += 2
        elif custo < 10:
            rating += 1
        elif custo > 30:
            rating -= 2
        
        # Fator de material
        if filament["tipo"] in ["PLA", "PETG", "ABS"]:
            rating += 1
        
        # Fator de disponibilidade
        if filament["disponivel"]:
            rating += 1
        
        # Fator de qualidade do filamento
        if filament["peso"] > 1000:
            rating += 0.5
        
        return min(rating, 10.0)
    
    def gerar_prompt_otimizado(self, especificacoes: Dict[str, Any]) -> str:
        """
        Gerar prompt otimizado para modelagem OpenSCAD
        
        Args:
            especificacoes: Especificações do modelo
            
        Returns:
            Prompt otimizado para gerar código OpenSCAD
        """
        # Prompt base com especificações
        prompt = f"""
        Gerar modelo 3D em OpenSCAD com as seguintes especificações:
        
        Tipo: {especificacoes.get('tipo', 'peça genérica')}
        Dimensões: {especificacoes.get('dimensoes', 'A definir')}
        Tolerâncias: {especificacoes.get('tolerancias', '0.2mm')}
        Material: {especificacoes.get('material', 'PLA')}
        Propósito: {especificacoes.get('proposito', 'prototipagem')}
        
        Requisitos técnicos:
        """
        
        # Adicionar requisitos específicos baseados no tipo
        tipo = especificacoes.get('tipo', '').lower()
        
        if 'chassi' in tipo or 'estrutura' in tipo:
            prompt += """
        - Parede mínima: 2mm
        - Resistência: Estrutural
        - Densidade de preenchimento: 30%
        - Furos de fixação: Ø3.5mm
        - Tolerâncias de encaixe: +0.2mm
        """
        elif 'suporte' in tipo:
            prompt += """
        - Precisão: Média
        - Montagem: Simples
        - Furos: Ø2.5mm para parafuso M3
        - Suporte de cabos: Incluir se necessário
        """
        elif 'enclosure' in tipo or 'caixa' in tipo:
            prompt += """
        - Vedação: Hermética
        - Acesso: Tampa removível
        - Ventilação: Furos de airis
        - Espessura: 3mm mínimo
        - Incluir: Furos para LEDs e conectores
        """
        
        # Adicionar parâmetros de impressão
        prompt += f"""
        
        Parâmetros de impressão:
        - Altura de camada: {especificacoes.get('layer_height', '0.2mm')}
        - Temperatura extrusor: {especificacoes.get('nozzle_temp', '200-220°C')}
        - Temperatura mesa: {especificacoes.get('bed_temp', '60°C')}
        - Velocidade: {especificacoes.get('print_speed', '50mm/s')}
        - Suporte: {especificacoes.get('supports', 'auto')}
        
        Código deve ser bem comentado e modular.
        """
        
        return prompt

def main():
    """Função principal para demonstração"""
    # API key fornecida pelo usuário
    API_KEY = "sl-cc497e90df04027eed2468af328a2d00fa99ca5e3b57893394f6cd6012aba3d4"
    
    # Inicializar sistema
    sistema = ModelagemInteligente(API_KEY)
    
    # Demonstração de uso
    print("=== SISTEMA DE MODELAGEM INTELIGENTE ===\n")
    
    # 1. Verificar API
    print("1. Verificando API Slant 3D...")
    usage = sistema.api.check_usage()
    if usage:
        print(f"   ✓ API conectada: {usage.remaining_requests}/{usage.limit} requests restantes")
    else:
        print("   ✗ Erro ao conectar com API")
        return
    
    # 2. Demonstrar filtros de filamentos
    print("\n2. Filamentos PLA disponíveis:")
    pla_filaments = sistema.api.filter_filaments({
        "type": "PLA",
        "available": True
    })
    
    for f in pla_filaments[:3]:
        print(f"   - {f.name} ({f.color}) - ${f.price_per_gram:.3f}/g")
    
    # 3. Processar prompt de exemplo
    print("\n3. Processando prompt inteligente...")
    prompt_exemplo = "criar chassi de base para projeto central de controle inteligente"
    resultado = sistema.processar_prompt(prompt_exemplo)
    
    print(f"   Prompt: '{resultado['prompt_original']}'")
    print(f"   Intenção: {resultado['intencao']['tipo']}")
    print(f"   Materiais: {', '.join(resultado['intencao']['materiais_preferidos'])}")
    
    # 4. Estimar custo
    print("\n4. Estimativa de custo:")
    if pla_filaments:
        estimativa = sistema.api.estimate_print_cost(
            pla_filaments[0].id, 
            volume_cm3=50.0
        )
        print(f"   Material: {estimativa['filament_name']}")
        print(f"   Peso estimado: {estimativa['model_weight_g']}g")
        print(f"   Custo total: ${estimativa['total_cost']:.2f}")
    
    print("\n=== SISTEMA PRONTO PARA USO ===")

if __name__ == "__main__":
    main()