#!/usr/bin/env python3
"""
Integração Completa: Sistema de Modelagem Inteligente + LGM
Exemplo de como integrar LGM ao sistema existente
"""

import os
import sys
import time
import json
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

# Adicionar diretório atual ao path para importes
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar sistema existente
try:
    from slant3d_integration import Slant3DAPI, ModelagemInteligente
except ImportError:
    print("Erro: slant3d_integration.py não encontrado")
    sys.exit(1)

# Importar integração LGM
try:
    from lgm_integration_example import LGMIntegration
except ImportError:
    print("Erro: lgm_integration_example.py não encontrado")
    sys.exit(1)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SistemaModelagemAvancado:
    """
    Sistema avançado de modelagem 3D que combina:
    - Análise inteligente de prompts
    - Geração 3D com LGM
    - Integração com APIs de impressão 3D
    - Análise de custo e orçamento
    """
    
    def __init__(self, 
                 slant_api_key: str,
                 lgm_config: Optional[Dict[str, Any]] = None,
                 workspace_path: str = "/workspace/sistema_avancado"):
        """
        Inicializa o sistema completo
        
        Args:
            slant_api_key: Chave da API Slant 3D
            lgm_config: Configuração do LGM (None para desabilitar)
            workspace_path: Diretório de trabalho
        """
        self.workspace_path = Path(workspace_path)
        self.workspace_path.mkdir(exist_ok=True)
        
        # Inicializar componentes
        self.slant_api = Slant3DAPI(slant_api_key)
        self.modelagem_base = ModelagemInteligente(slant_api_key)
        
        # Inicializar LGM se configurado
        if lgm_config:
            try:
                self.lgm = LGMIntegration(**lgm_config)
                logger.info("LGM integração ativada")
            except Exception as e:
                logger.error(f"Erro ao inicializar LGM: {e}")
                self.lgm = None
        else:
            self.lgm = None
            logger.info("LGM desabilitado")
        
        # Histórico de operações
        self.operation_history = []
        
        # Métricas de performance
        self.performance_metrics = {
            'total_operations': 0,
            'successful_generations': 0,
            'failed_generations': 0,
            'average_generation_time': 0,
            'cost_saved': 0
        }
    
    def processar_projeto_completo(self, 
                                 prompt: str,
                                 usar_lgm: bool = True,
                                 material_preferido: str = "PLA",
                                 qualidade_modelo: str = "medium") -> Dict[str, Any]:
        """
        Processa um projeto completo desde o prompt até o orçamento final
        
        Args:
            prompt: Descrição do projeto
            usar_lgm: Se deve usar LGM para gerar modelo 3D
            material_preferido: Material preferido para impressão
            qualidade_modelo: Qualidade do modelo (low, medium, high)
        
        Returns:
            Dict com resultado completo do projeto
        """
        start_time = time.time()
        operation_id = f"proj_{int(start_time)}_{hash(prompt) % 10000}"
        
        logger.info(f"Iniciando projeto completo: {operation_id}")
        
        result = {
            'operation_id': operation_id,
            'timestamp': start_time,
            'prompt': prompt,
            'config': {
                'usar_lgm': usar_lgm,
                'material_preferido': material_preferido,
                'qualidade_modelo': qualidade_modelo
            }
        }
        
        try:
            # 1. Análise inteligente do prompt
            logger.info("1. Analisando prompt...")
            analise = self.modelagem_base.analisar_tipo_projeto(prompt)
            result['analise_prompt'] = analise
            
            # 2. Geração de modelo 3D (se LGM disponível)
            if usar_lgm and self.lgm:
                logger.info("2. Gerando modelo 3D com LGM...")
                lgm_result = self._gerar_modelo_3d(prompt, qualidade_modelo)
                result['geracao_3d'] = lgm_result
                
                if not lgm_result['success']:
                    logger.warning("Falha na geração 3D, continuando sem modelo")
            else:
                result['geracao_3d'] = {
                    'success': False,
                    'message': 'LGM desabilitado ou indisponível'
                }
            
            # 3. Análise de materiais e recomendações
            logger.info("3. Analisando materiais...")
            materiais = self._analisar_materiais(analise, material_preferido)
            result['materiais'] = materiais
            
            # 4. Cálculo de orçamento completo
            logger.info("4. Calculando orçamento...")
            orcamento = self._calcular_orcamento_completo(
                analise, materiais, result.get('geracao_3d', {})
            )
            result['orcamento'] = orcamento
            
            # 5. Geração de código OpenSCAD (se aplicável)
            logger.info("5. Gerando código OpenSCAD...")
            openscad = self._gerar_openscad_optional(analise, prompt)
            result['openscad'] = openscad
            
            # 6. Análise de viabilidade
            logger.info("6. Analisando viabilidade...")
            viabilidade = self._analisar_viabilidade(result)
            result['viabilidade'] = viabilidade
            
            # 7. Recomendações finais
            logger.info("7. Gerando recomendações...")
            recomendacoes = self._gerar_recomendacoes(result)
            result['recomendacoes'] = recomendacoes
            
            # Marcar como sucesso
            result['success'] = True
            result['processing_time'] = time.time() - start_time
            
            # Atualizar métricas
            self._update_metrics(result['success'], result['processing_time'])
            
            logger.info(f"Projeto concluído com sucesso: {operation_id}")
            
        except Exception as e:
            logger.error(f"Erro no processamento: {e}")
            result['success'] = False
            result['error'] = str(e)
            result['processing_time'] = time.time() - start_time
            
            # Atualizar métricas
            self._update_metrics(False, result['processing_time'])
        
        # Salvar no histórico
        self.operation_history.append(result)
        
        return result
    
    def _gerar_modelo_3d(self, prompt: str, qualidade: str) -> Dict[str, Any]:
        """Gera modelo 3D usando LGM"""
        if not self.lgm:
            return {
                'success': False,
                'error': 'LGM não configurado'
            }
        
        try:
            # Configurações baseadas na qualidade
            quality_configs = {
                'low': {'resolution': 512, 'num_outputs': 1},
                'medium': {'resolution': 800, 'num_outputs': 1},
                'high': {'resolution': 1024, 'num_outputs': 2}
            }
            
            config = quality_configs.get(qualidade, quality_configs['medium'])
            
            # Gerar modelo
            result = self.lgm.generate_3d_from_text(
                prompt=prompt,
                **config
            )
            
            if result['success'] and result.get('output_files'):
                # Tentar converter para formato imprimível
                converted = []
                for output_file in result['output_files']:
                    if output_file.endswith('.ply'):
                        conv_result = self.lgm.convert_to_printable_format(
                            output_file, 'obj'
                        )
                        if conv_result['success']:
                            converted.append(conv_result['output_file'])
                        else:
                            converted.append(output_file)  # Usar original
                    else:
                        converted.append(output_file)
                
                result['output_files'] = converted
                result['printable_files'] = converted
            
            return result
            
        except Exception as e:
            logger.error(f"Erro na geração 3D: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _analisar_materiais(self, analise: Dict, material_preferido: str) -> Dict[str, Any]:
        """Analisa e recomenda materiais"""
        # Usar sistema base para recomendações
        materiais_recomendados = self.modelagem_base.recomendar_materiais(analise)
        
        # Adicionar informações específicas do LGM
        materiais_recomendados['configuracao_lgm'] = {
            'modelo_suportado': True,
            'complexidade_geometrica': analise.get('complexidade', 'media'),
            'resolucao_sugerida': self._sugerir_resolucao(analise),
            'tempo_estimado_geracao': self._estimar_tempo_geracao(analise)
        }
        
        # Preferência do usuário
        if material_preferido in [m['nome'] for m in materiais_recomendados['materiais']]:
            materiais_recomendados['material_preferido'] = material_preferido
            materiais_recomendados['recomendacao_personalizada'] = True
        
        return materiais_recomendados
    
    def _sugerir_resolucao(self, analise: Dict) -> int:
        """Sugere resolução baseada na análise"""
        complexidade = analise.get('complexidade', 'media')
        
        resolucoes = {
            'simples': 512,
            'media': 800,
            'complexa': 1024
        }
        
        return resolucoes.get(complexidade, 800)
    
    def _estimar_tempo_geracao(self, analise: Dict) -> float:
        """Estima tempo de geração em minutos"""
        complexidade = analise.get('complexidade', 'media')
        
        # Tempos base (em minutos)
        if self.lgm and self.lgm.method == 'local':
            tempos = {'simples': 0.5, 'media': 1.0, 'complexa': 2.0}
        else:
            tempos = {'simples': 1.0, 'media': 2.0, 'complexa': 4.0}
        
        return tempos.get(complexidade, 1.5)
    
    def _calcular_orcamento_completo(self, analise: Dict, materiais: Dict, geracao_3d: Dict) -> Dict[str, Any]:
        """Calcula orçamento completo incluindo custo de geração LGM"""
        # Usar orçamento base
        orcamento_base = self.modelagem_base.calcular_orcamento_completo(analise, materiais)
        
        # Adicionar custos de geração LGM
        lgm_costs = self._calcular_custos_lgm(geracao_3d)
        orcamento_base['custos_lgm'] = lgm_costs
        
        # Cálculo total
        custo_material = orcamento_base.get('custo_total', 0)
        custo_lgm = lgm_costs.get('custo_total', 0)
        
        orcamento_base['custo_total_completo'] = custo_material + custo_lgm
        orcamento_base['economia_vs_manual'] = self._calcular_economia(orcamento_base['custo_total_completo'])
        
        return orcamento_base
    
    def _calcular_custos_lgm(self, geracao_3d: Dict) -> Dict[str, Any]:
        """Calcula custos específicos da geração LGM"""
        if not geracao_3d.get('success'):
            return {'custo_total': 0, 'metodo': 'nao_gerado'}
        
        method = geracao_3d.get('method', 'desconhecido')
        processing_time = geracao_3d.get('processing_time', 0)
        
        # Estimativas de custo por método
        if method == 'replicate':
            # Custo estimado: $0.02-0.05 por geração
            custo_unitario = 0.03
            custo_total = custo_unitario * geracao_3d.get('output_files', [1])
        elif method == 'local':
            # Custo zero, mas considerar tempo de GPU
            custo_total = 0
        else:
            custo_total = 0
        
        return {
            'metodo': method,
            'tempo_processamento': processing_time,
            'custo_unitario': custo_unitario if method == 'replicate' else 0,
            'custo_total': custo_total,
            'arquivos_gerados': len(geracao_3d.get('output_files', []))
        }
    
    def _calcular_economia(self, custo_total: float) -> Dict[str, Any]:
        """Calcula economia comparado a métodos manuais"""
        # Estimativas de custo manual
        custo_manual_modelagem = 50.0  # R$50-200 por modelagem manual
        custo_manual_3d = 100.0  # R$100-300 por impressão de teste
        custo_manual_total = custo_manual_modelagem + custo_manual_3d
        
        if custo_total < custo_manual_total:
            economia = custo_manual_total - custo_total
            percentual = (economia / custo_manual_total) * 100
        else:
            economia = 0
            percentual = 0
        
        return {
            'economia_absoluta': economia,
            'economia_percentual': percentual,
            'custo_manual_estimado': custo_manual_total,
            'custo_automatico': custo_total,
            'viabilidade_economica': economia > 0
        }
    
    def _gerar_openscad_optional(self, analise: Dict, prompt: str) -> Dict[str, Any]:
        """Gera código OpenSCAD quando aplicável"""
        try:
            # Detectar se é um projeto que pode ser modelado parametricamente
            tipo_projeto = analise.get('tipo_projeto', '')
            
            projetos_parametricos = [
                'suporte', 'estrutura', 'carcaça', 'gabinete', 
                'adaptador', 'suporte arduino', 'suporte raspberry pi'
            ]
            
            if any(palavra in tipo_projeto.lower() for palavra in projetos_parametricos):
                # Gerar código OpenSCAD básico
                codigo_openscad = self._gerar_codigo_openscad_basico(analise, prompt)
                
                return {
                    'success': True,
                    'gerado': True,
                    'codigo': codigo_openscad,
                    'arquivo': f"codigo_{int(time.time())}.scad",
                    'recomendacao': 'Código OpenSCAD gerado para modelagem paramétrica'
                }
            else:
                return {
                    'success': True,
                    'gerado': False,
                    'motivo': 'Projeto não adequado para modelagem paramétrica OpenSCAD'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _gerar_codigo_openscad_basico(self, analise: Dict, prompt: str) -> str:
        """Gera código OpenSCAD básico"""
        # Exemplo simples - em uma implementação real seria mais sofisticado
        codigo = f"""
// Código OpenSCAD gerado automaticamente
// Projeto: {prompt[:50]}...
// Tipo: {analise.get('tipo_projeto', 'N/A')}

// Parâmetros básicos
width = {analise.get('dimensoes', {}).get('largura', 50)};
height = {analise.get('dimensoes', {}).get('altura', 30)};
depth = {analise.get('dimensoes', {}).get('profundidade', 20)};

// Modelo base
module projeto_base() {{
    cube([width, depth, height], center=true);
}}

// Executar modelo
projeto_base();
"""
        return codigo
    
    def _analisar_viabilidade(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa viabilidade do projeto"""
        viabilidade = {
            'score_geral': 0,
            'aspectos': {},
            'recomendacoes': [],
            'riscos': []
        }
        
        # Analisar complexidade
        analise = result.get('analise_prompt', {})
        complexidade = analise.get('complexidade', 'media')
        
        scores = {'simples': 9, 'media': 7, 'complexa': 5}
        viabilidade['aspectos']['complexidade'] = scores.get(complexidade, 7)
        
        # Analisar custo
        orcamento = result.get('orcamento', {})
        custo_total = orcamento.get('custo_total_completo', float('inf'))
        
        if custo_total < 50:
            viabilidade['aspectos']['custo'] = 9
        elif custo_total < 100:
            viabilidade['aspectos']['custo'] = 7
        else:
            viabilidade['aspectos']['custo'] = 5
            viabilidade['riscos'].append('Custo alto pode impactar viabilidade')
        
        # Analisar disponibilidade de materiais
        materiais = result.get('materiais', {})
        materiais_disponiveis = len(materiais.get('materiais', []))
        
        if materiais_disponiveis >= 3:
            viabilidade['aspectos']['materiais'] = 9
        elif materiais_disponiveis >= 1:
            viabilidade['aspectos']['materiais'] = 7
        else:
            viabilidade['aspectos']['materiais'] = 3
            viabilidade['riscos'].append('Poucos materiais disponíveis')
        
        # Score geral
        viabilidade['score_geral'] = sum(viabilidade['aspectos'].values()) / len(viabilidade['aspectos'])
        
        # Recomendações baseadas no score
        if viabilidade['score_geral'] >= 8:
            viabilidade['recomendacoes'].append('Projeto altamente viável. Proceder com confiança.')
        elif viabilidade['score_geral'] >= 6:
            viabilidade['recomendacoes'].append('Projeto viável com algumas considerações.')
        else:
            viabilidade['recomendacoes'].append('Projeto requer revisão. Considerar simplificações.')
        
        return viabilidade
    
    def _gerar_recomendacoes(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Gera recomendações finais baseadas em toda a análise"""
        recomendacoes = {
            'prioridades': [],
            'proximos_passos': [],
            'otimizacoes': [],
            'alternativas': []
        }
        
        # Análise de prioridades
        if result.get('geracao_3d', {}).get('success'):
            recomendacoes['prioridades'].append('Iniciar impressão 3D com modelo gerado')
        else:
            recomendacoes['proximos_passos'].append('Revisar prompt para melhorar geração 3D')
        
        # Análise de custo
        orcamento = result.get('orcamento', {})
        custo_total = orcamento.get('custo_total_completo', 0)
        
        if custo_total < 30:
            recomendacoes['otimizacoes'].append('Projeto econômico - ideal para prototipagem')
        elif custo_total > 100:
            recomendacoes['otimizacoes'].append('Considerar otimização de design para reduzir custos')
        
        # Recomendações de material
        materiais = result.get('materiais', {})
        material_recomendado = materiais.get('materiais', [{}])[0] if materiais.get('materiais') else {}
        
        if material_recomendado:
            recomendacoes['proximos_passos'].append(
                f"Usar {material_recomendado.get('nome', 'PLA')} como material principal"
            )
        
        # Alternativas baseadas na viabilidade
        viabilidade = result.get('viabilidade', {})
        if viabilidade.get('score_geral', 0) < 6:
            recomendacoes['alternativas'].append('Considerar modelagem paramétrica manual')
            recomendacoes['alternativas'].append('Simplificar design se necessário')
        
        return recomendacoes
    
    def _update_metrics(self, success: bool, processing_time: float):
        """Atualiza métricas de performance"""
        self.performance_metrics['total_operations'] += 1
        
        if success:
            self.performance_metrics['successful_generations'] += 1
        else:
            self.performance_metrics['failed_generations'] += 1
        
        # Média móvel do tempo de processamento
        total = self.performance_metrics['total_operations']
        current_avg = self.performance_metrics['average_generation_time']
        new_avg = ((current_avg * (total - 1)) + processing_time) / total
        self.performance_metrics['average_generation_time'] = new_avg
    
    def get_estatisticas_sistema(self) -> Dict[str, Any]:
        """Retorna estatísticas completas do sistema"""
        stats = {
            'timestamp': time.time(),
            'lgm_disponivel': self.lgm is not None,
            'performance_metrics': self.performance_metrics.copy(),
            'configuracao': {
                'workspace_path': str(self.workspace_path),
                'historial_size': len(self.operation_history)
            }
        }
        
        if self.lgm:
            stats['lgm_stats'] = self.lgm.get_usage_stats()
        
        return stats
    
    def salvar_projeto(self, result: Dict[str, Any], filename: Optional[str] = None) -> str:
        """Salva resultado do projeto em arquivo JSON"""
        if not filename:
            timestamp = int(time.time())
            filename = f"projeto_{timestamp}.json"
        
        filepath = self.workspace_path / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Projeto salvo: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Erro ao salvar projeto: {e}")
            return ""


# Exemplo de uso
def exemplo_uso_completo():
    """Exemplo de como usar o sistema completo"""
    
    # Configuração
    SLANT_API_KEY = "sl-cc497e90df04027eed2468af328a2d00fa99ca5e3b57893394f6cd6012aba3d4"
    LGM_CONFIG = {
        'replicate_api_key': 'r8_your_replicate_token',
        'local_model_path': '/path/to/lgm/model.safetensors',
        'workspace_path': '/workspace/sistema_lgm',
        'cache_enabled': True
    }
    
    # Inicializar sistema
    sistema = SistemaModelagemAvancado(
        slant_api_key=SLANT_API_KEY,
        lgm_config=LGM_CONFIG
    )
    
    # Exemplos de prompts para testar
    prompts_exemplo = [
        "Criar suporte para Arduino Uno com ventilação e acesso aos conectores",
        "Gabinete para Raspberry Pi 4 com dissipadores e furos de ventilação",
        "Suporte para sensor ultrasônico com ajuste de ângulo",
        "Estrutura para impressora 3D mini com bandeja retrátil"
    ]
    
    print("🚀 Sistema de Modelagem Avançado + LGM")
    print("=" * 50)
    
    # Processar cada exemplo
    for i, prompt in enumerate(prompts_exemplo, 1):
        print(f"\n📋 Exemplo {i}: {prompt}")
        print("-" * 50)
        
        result = sistema.processar_projeto_completo(
            prompt=prompt,
            usar_lgm=True,
            material_preferido="PLA",
            qualidade_modelo="medium"
        )
        
        if result['success']:
            print(f"✅ Sucesso em {result['processing_time']:.1f}s")
            print(f"🎯 Score viabilidade: {result['viabilidade']['score_geral']:.1f}/10")
            print(f"💰 Custo total: R$ {result['orcamento']['custo_total_completo']:.2f}")
            
            # Salvar projeto
            filename = sistema.salvar_projeto(result)
            print(f"💾 Projeto salvo: {filename}")
        else:
            print(f"❌ Erro: {result.get('error', 'Desconhecido')}")
    
    # Mostrar estatísticas
    print("\n📊 Estatísticas do Sistema")
    print("=" * 30)
    stats = sistema.get_estatisticas_sistema()
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    exemplo_uso_completo()