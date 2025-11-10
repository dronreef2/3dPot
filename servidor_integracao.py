#!/usr/bin/env python3
"""
Servidor de Integração para Sistema de Modelagem Inteligente
Conecta interface web com API Slant 3D
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import os
from pathlib import Path
import logging
from slant3d_integration import ModelagemInteligente, Slant3DAPI
import threading
import time
import tempfile
import shutil
from werkzeug.utils import secure_filename

# Importar integração LGM
from lgm_integration_example import LGMIntegration

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar Flask
app = Flask(__name__)
CORS(app)  # Permitir requisições de diferentes origens

# API Key do Slant 3D
API_KEY = "sl-cc497e90df04027eed2468af328a2d00fa99ca5e3b57893394f6cd6012aba3d4"

# Inicializar sistema de modelagem inteligente
sistema = None
sistema_lgm = None

def inicializar_sistema():
    """Inicializar sistema de modelagem inteligente e LGM"""
    global sistema, sistema_lgm
    try:
        # Inicializar sistema Slant 3D
        sistema = ModelagemInteligente(API_KEY)
        logger.info("Sistema de modelagem inteligente inicializado com sucesso")
        
        # Inicializar sistema LGM
        try:
            replicate_key = os.environ.get('REPLICATE_API_TOKEN')
            sistema_lgm = LGMIntegration(
                replicate_api_key=replicate_key,
                workspace_path="workspace_lgm",
                cache_enabled=True
            )
            logger.info("Sistema LGM inicializado com sucesso")
            
            # Log do método utilizado
            stats = sistema_lgm.get_usage_stats()
            logger.info(f"Método LGM utilizado: {stats['method']}")
            
        except Exception as e:
            logger.warning(f"Erro ao inicializar LGM (continuando sem): {e}")
            sistema_lgm = None
        
        return True
    except Exception as e:
        logger.error(f"Erro ao inicializar sistema: {e}")
        return False

# Rotas da aplicação web
@app.route('/')
def index():
    """Página principal"""
    return send_from_directory('.', 'modelagem-inteligente.html')

@app.route('/api/status')
def api_status():
    """Verificar status da API"""
    try:
        status_info = {
            'status': 'online',
            'api_connected': False,
            'lgm_connected': False,
            'version': '1.1.0',
            'timestamp': time.time()
        }
        
        # Verificar API Slant 3D
        if sistema and sistema.api:
            usage = sistema.api.check_usage()
            status_info['api_connected'] = True
            status_info['usage'] = {
                'remaining': usage.remaining_requests if usage else 0,
                'limit': usage.limit if usage else 100,
                'tier': usage.account_tier if usage else 'free'
            }
            status_info['message'] = 'API Slant 3D funcionando normalmente'
        else:
            status_info['message'] = 'Sistema não inicializado'
        
        # Verificar sistema LGM
        if sistema_lgm:
            lgm_stats = sistema_lgm.get_usage_stats()
            lgm_health = sistema_lgm.health_check()
            status_info['lgm_connected'] = True
            status_info['lgm_status'] = {
                'method': lgm_stats['method'],
                'gpu_available': lgm_stats['gpu_available'],
                'health': lgm_health['overall_status']
            }
            status_info['message'] += ' + Sistema LGM ativo'
        else:
            status_info['lgm_status'] = {
                'method': 'unavailable',
                'reason': 'Configure REPLICATE_API_TOKEN'
            }
        
        # Status geral
        if status_info['api_connected'] and status_info['lgm_connected']:
            status_info['overall_status'] = 'full'
        elif status_info['api_connected']:
            status_info['overall_status'] = 'partial'
        else:
            status_info['overall_status'] = 'error'
            return jsonify(status_info), 500
        
        return jsonify(status_info)
        
    except Exception as e:
        logger.error(f"Erro ao verificar status: {e}")
        return jsonify({
            'status': 'error',
            'api_connected': False,
            'lgm_connected': False,
            'message': f'Erro interno: {str(e)}',
            'timestamp': time.time()
        }), 500

@app.route('/api/filaments')
def get_filaments():
    """Obter lista de filamentos com filtros opcionais"""
    try:
        if not sistema:
            return jsonify({'error': 'Sistema não inicializado'}), 500
        
        # Obter parâmetros de filtro
        material = request.args.get('material', '')
        color = request.args.get('color', '')
        max_price = request.args.get('max_price', '')
        available_only = request.args.get('available_only', 'true').lower() == 'true'
        
        # Construir filtros
        filtros = {}
        if material:
            filtros['type'] = material
        if color:
            filtros['color'] = color
        if max_price:
            filtros['max_price'] = float(max_price)
        if available_only:
            filtros['available'] = True
        
        # Buscar filamentos
        filamentos = sistema.api.filter_filaments(filtros)
        
        # Converter para formato JSON
        resultado = {
            'success': True,
            'count': len(filamentos),
            'filters_applied': filtros,
            'filaments': [
                {
                    'id': f.id,
                    'name': f.name,
                    'color': f.color,
                    'type': f.type,
                    'available': f.available,
                    'price_per_gram': f.price_per_gram,
                    'diameter': f.diameter,
                    'weight': f.weight
                }
                for f in filamentos
            ]
        }
        
        return jsonify(resultado)
        
    except Exception as e:
        logger.error(f"Erro ao buscar filamentos: {e}")
        return jsonify({
            'success': False,
            'error': f'Erro ao buscar filamentos: {str(e)}'
        }), 500

@app.route('/api/analyze-prompt', methods=['POST'])
def analyze_prompt():
    """Analisar prompt de usuário"""
    try:
        if not sistema:
            return jsonify({'error': 'Sistema não inicializado'}), 500
        
        data = request.get_json()
        if not data or 'prompt' not in data:
            return jsonify({'error': 'Prompt não fornecido'}), 400
        
        prompt = data['prompt']
        project_type = data.get('project_type', 'prototipo')
        complexity = data.get('complexity', 'media')
        
        # Processar prompt com sistema inteligente
        resultado = sistema.processar_prompt(prompt)
        
        # Adicionar metadados
        resultado['timestamp'] = time.time()
        resultado['api_key_status'] = 'active'
        
        return jsonify({
            'success': True,
            'analysis': resultado
        })
        
    except Exception as e:
        logger.error(f"Erro ao analisar prompt: {e}")
        return jsonify({
            'success': False,
            'error': f'Erro ao analisar prompt: {str(e)}'
        }), 500

@app.route('/api/estimate-cost', methods=['POST'])
def estimate_cost():
    """Calcular estimativa de custo"""
    try:
        if not sistema:
            return jsonify({'error': 'Sistema não inicializado'}), 500
        
        data = request.get_json()
        required_fields = ['filament_id', 'volume']
        
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Campo obrigatório: {field}'}), 400
        
        filament_id = data['filament_id']
        volume = float(data['volume'])
        material_density = float(data.get('material_density', 1.24))
        
        # Calcular estimativa
        estimativa = sistema.api.estimate_print_cost(filament_id, volume, material_density)
        
        if not estimativa:
            return jsonify({'error': 'Filamento não encontrado'}), 404
        
        return jsonify({
            'success': True,
            'estimate': estimativa
        })
        
    except Exception as e:
        logger.error(f"Erro ao calcular custo: {e}")
        return jsonify({
            'success': False,
            'error': f'Erro ao calcular custo: {str(e)}'
        }), 500

@app.route('/api/calculate-budget', methods=['POST'])
def calculate_budget():
    """Calcular orçamento completo"""
    try:
        if not sistema:
            return jsonify({'error': 'Sistema não inicializado'}), 500
        
        data = request.get_json()
        required_fields = ['model_name', 'volume']
        
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Campo obrigatório: {field}'}), 400
        
        modelo = data['model_name']
        volume = float(data['volume'])
        requisitos_filamento = {
            'material': data.get('preferred_material', ''),
            'cor': data.get('preferred_color', ''),
            'max_preco': data.get('max_price', 0)
        }
        
        # Remover campos vazios
        requisitos_filamento = {k: v for k, v in requisitos_filamento.items() if v}
        
        # Calcular orçamento
        orcamento = sistema.calcular_orçamento_completo(
            modelo, 
            volume, 
            requisitos_filamento
        )
        
        return jsonify({
            'success': True,
            'budget': orcamento
        })
        
    except Exception as e:
        logger.error(f"Erro ao calcular orçamento: {e}")
        return jsonify({
            'success': False,
            'error': f'Erro ao calcular orçamento: {str(e)}'
        }), 500

@app.route('/api/generate-prompt', methods=['POST'])
def generate_prompt():
    """Gerar prompt otimizado para OpenSCAD"""
    try:
        if not sistema:
            return jsonify({'error': 'Sistema não inicializado'}), 500
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Especificações não fornecidas'}), 400
        
        # Gerar prompt otimizado
        prompt_otimizado = sistema.gerar_prompt_otimizado(data)
        
        return jsonify({
            'success': True,
            'generated_prompt': prompt_otimizado
        })
        
    except Exception as e:
        logger.error(f"Erro ao gerar prompt: {e}")
        return jsonify({
            'success': False,
            'error': f'Erro ao gerar prompt: {str(e)}'
        }), 500

@app.route('/api/usage')
def get_usage():
    """Obter informações de uso da API"""
    try:
        if not sistema or not sistema.api:
            return jsonify({'error': 'API não disponível'}), 503
        
        usage = sistema.api.check_usage()
        if not usage:
            return jsonify({'error': 'Não foi possível obter informações de uso'}), 500
        
        return jsonify({
            'success': True,
            'usage': {
                'total_requests': usage.total_requests,
                'remaining_requests': usage.remaining_requests,
                'limit': usage.limit,
                'reset_time': usage.reset_time,
                'account_tier': usage.account_tier
            }
        })
        
    except Exception as e:
        logger.error(f"Erro ao obter uso da API: {e}")
        return jsonify({
            'success': False,
            'error': f'Erro ao obter uso: {str(e)}'
        }), 500

@app.route('/models')
def list_models():
    """Listar modelos 3D disponíveis"""
    try:
        models_dir = Path("modelos-3d")
        if not models_dir.exists():
            return jsonify({'error': 'Diretório de modelos não encontrado'}), 404
        
        models = []
        for model_dir in models_dir.iterdir():
            if model_dir.is_dir():
                # Verificar se tem arquivos .scad
                scad_files = list(model_dir.glob("*.scad"))
                if scad_files:
                    models.append({
                        'name': model_dir.name,
                        'path': str(model_dir),
                        'scad_files': [f.name for f in scad_files],
                        'description': f"Coleção de {len(scad_files)} modelos"
                    })
        
        return jsonify({
            'success': True,
            'models': models,
            'total_models': len(models)
        })
        
    except Exception as e:
        logger.error(f"Erro ao listar modelos: {e}")
        return jsonify({
            'success': False,
            'error': f'Erro ao listar modelos: {str(e)}'
        }), 500

@app.route('/api/health')
def health_check():
    """Health check da aplicação"""
    return jsonify({
        'status': 'healthy',
        'timestamp': time.time(),
        'system_initialized': sistema is not None,
        'lgm_initialized': sistema_lgm is not None,
        'version': '1.1.0'
    })

# ================================
# ENDPOINTS LGM (Large Multi-View Gaussian Model)
# ================================

@app.route('/api/lgm/status')
def lgm_status():
    """Verificar status do sistema LGM"""
    try:
        if not sistema_lgm:
            return jsonify({
                'success': False,
                'status': 'uninitialized',
                'message': 'Sistema LGM não inicializado',
                'recommendation': 'Configure REPLICATE_API_TOKEN ou setup local'
            }), 503
        
        # Obter informações do sistema
        stats = sistema_lgm.get_usage_stats()
        health = sistema_lgm.health_check()
        
        return jsonify({
            'success': True,
            'status': 'online',
            'system': stats,
            'health': health,
            'timestamp': time.time()
        })
        
    except Exception as e:
        logger.error(f"Erro ao verificar status LGM: {e}")
        return jsonify({
            'success': False,
            'status': 'error',
            'message': f'Erro interno: {str(e)}'
        }), 500

@app.route('/api/lgm/gerar-texto', methods=['POST'])
def lgm_gerar_texto():
    """Gerar modelo 3D a partir de texto"""
    try:
        if not sistema_lgm:
            return jsonify({
                'success': False,
                'error': 'Sistema LGM não disponível',
                'message': 'Configure REPLICATE_API_TOKEN ou setup local'
            }), 503
        
        data = request.get_json()
        if not data or 'prompt' not in data:
            return jsonify({
                'success': False,
                'error': 'Campo "prompt" obrigatório'
            }), 400
        
        prompt = data['prompt']
        num_outputs = int(data.get('num_outputs', 1))
        resolution = int(data.get('resolution', 800))
        guidance_scale = float(data.get('guidance_scale', 7.5))
        seed = data.get('seed')
        
        logger.info(f"Iniciando geração LGM de texto: '{prompt[:50]}...'")
        
        # Gerar modelo 3D
        resultado = sistema_lgm.generate_3d_from_text(
            prompt=prompt,
            num_outputs=num_outputs,
            resolution=resolution,
            guidance_scale=guidance_scale,
            seed=seed
        )
        
        if resultado.get('success'):
            # Se sistema tradicional está disponível, adicionar análise
            projeto_completo = None
            if sistema:
                try:
                    projeto_completo = sistema.processar_prompt(prompt)
                except Exception as e:
                    logger.warning(f"Erro na análise de projeto: {e}")
            
            return jsonify({
                'success': True,
                'lgm_result': resultado,
                'project_analysis': projeto_completo,
                'timestamp': time.time(),
                'method': resultado.get('method', 'unknown')
            })
        else:
            return jsonify({
                'success': False,
                'error': resultado.get('error', 'Erro na geração'),
                'lgm_result': resultado
            }), 500
            
    except Exception as e:
        logger.error(f"Erro na geração LGM (texto): {e}")
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500

@app.route('/api/lgm/gerar-imagem', methods=['POST'])
def lgm_gerar_imagem():
    """Gerar modelo 3D a partir de imagem"""
    try:
        if not sistema_lgm:
            return jsonify({
                'success': False,
                'error': 'Sistema LGM não disponível',
                'message': 'Configure REPLICATE_API_TOKEN ou setup local'
            }), 503
        
        if 'imagem' not in request.files:
            return jsonify({
                'success': False,
                'error': 'Arquivo de imagem obrigatório (campo "imagem")'
            }), 400
        
        # Receber dados do formulário
        imagem_file = request.files['imagem']
        prompt = request.form.get('prompt', '')
        num_outputs = int(request.form.get('num_outputs', 1))
        resolution = int(request.form.get('resolution', 800))
        
        # Verificar se arquivo foi enviado
        if imagem_file.filename == '':
            return jsonify({
                'success': False,
                'error': 'Nenhum arquivo selecionado'
            }), 400
        
        # Verificar extensão
        allowed_extensions = {'jpg', 'jpeg', 'png', 'bmp', 'tiff'}
        filename = secure_filename(imagem_file.filename)
        if '.' not in filename:
            return jsonify({
                'success': False,
                'error': 'Arquivo deve ter extensão válida'
            }), 400
        
        ext = filename.rsplit('.', 1)[1].lower()
        if ext not in allowed_extensions:
            return jsonify({
                'success': False,
                'error': f'Formato não suportado: {ext}. Use: {", ".join(allowed_extensions)}'
            }), 400
        
        # Salvar arquivo temporariamente
        temp_dir = tempfile.mkdtemp()
        try:
            image_path = os.path.join(temp_dir, filename)
            imagem_file.save(image_path)
            
            logger.info(f"Iniciando geração LGM de imagem: {filename}")
            
            # Gerar modelo 3D
            resultado = sistema_lgm.generate_3d_from_image(
                image_path=image_path,
                prompt=prompt if prompt else None,
                num_outputs=num_outputs,
                resolution=resolution
            )
            
            if resultado.get('success'):
                return jsonify({
                    'success': True,
                    'lgm_result': resultado,
                    'source_file': filename,
                    'timestamp': time.time(),
                    'method': resultado.get('method', 'unknown')
                })
            else:
                return jsonify({
                    'success': False,
                    'error': resultado.get('error', 'Erro na geração'),
                    'lgm_result': resultado
                }), 500
                
        finally:
            # Limpar arquivo temporário
            try:
                shutil.rmtree(temp_dir)
            except:
                pass
                
    except Exception as e:
        logger.error(f"Erro na geração LGM (imagem): {e}")
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500

@app.route('/api/lgm/convert', methods=['POST'])
def lgm_convert():
    """Converter arquivo PLY para OBJ/STL"""
    try:
        if not sistema_lgm:
            return jsonify({
                'success': False,
                'error': 'Sistema LGM não disponível',
                'message': 'Configure REPLICATE_API_TOKEN ou setup local'
            }), 503
        
        data = request.get_json()
        required_fields = ['file_path', 'format']
        
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Campo obrigatório: {field}'
                }), 400
        
        file_path = data['file_path']
        output_format = data['format'].lower()
        quality = data.get('quality', 'high')
        
        # Verificar formato suportado
        supported_formats = ['obj', 'stl', 'glb']
        if output_format not in supported_formats:
            return jsonify({
                'success': False,
                'error': f'Formato não suportado: {output_format}. Use: {", ".join(supported_formats)}'
            }), 400
        
        # Verificar se arquivo existe
        if not os.path.exists(file_path):
            return jsonify({
                'success': False,
                'error': f'Arquivo não encontrado: {file_path}'
            }), 404
        
        logger.info(f"Iniciando conversão LGM: {file_path} -> {output_format}")
        
        # Converter arquivo
        resultado = sistema_lgm.convert_to_printable_format(
            input_file=file_path,
            output_format=output_format,
            quality=quality
        )
        
        if resultado.get('success'):
            return jsonify({
                'success': True,
                'conversion_result': resultado,
                'timestamp': time.time()
            })
        else:
            return jsonify({
                'success': False,
                'error': resultado.get('error', 'Erro na conversão'),
                'conversion_result': resultado
            }), 500
            
    except Exception as e:
        logger.error(f"Erro na conversão LGM: {e}")
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500

# ================================
# ENDPOINT INTEGRADO: PROMPT PARA RESULTADO COMPLETO
# ================================

@app.route('/api/lgm/projeto-completo', methods=['POST'])
def lgm_projeto_completo():
    """
    Endpoint integrado: recebe texto e retorna projeto completo
    Gera modelo 3D com LGM + análise com sistema tradicional + orçamento
    """
    try:
        data = request.get_json()
        if not data or 'prompt' not in data:
            return jsonify({
                'success': False,
                'error': 'Campo "prompt" obrigatório'
            }), 400
        
        prompt = data['prompt']
        include_analysis = data.get('include_analysis', True)
        include_budget = data.get('include_budget', True)
        
        logger.info(f"Iniciando projeto completo LGM: '{prompt[:50]}...'")
        
        resultado_completo = {
            'success': True,
            'prompt': prompt,
            'timestamp': time.time(),
            'stages': {}
        }
        
        # Estágio 1: Geração LGM (se disponível)
        lgm_result = None
        if sistema_lgm:
            try:
                logger.info("Estágio 1: Gerando modelo 3D com LGM")
                lgm_result = sistema_lgm.generate_3d_from_text(
                    prompt=prompt,
                    num_outputs=1,
                    resolution=800,
                    guidance_scale=7.5
                )
                resultado_completo['stages']['lgm_generation'] = lgm_result
                logger.info("✅ Geração LGM concluída")
            except Exception as e:
                logger.error(f"Erro na geração LGM: {e}")
                resultado_completo['stages']['lgm_generation'] = {
                    'success': False,
                    'error': str(e)
                }
        else:
            resultado_completo['stages']['lgm_generation'] = {
                'success': False,
                'error': 'Sistema LGM não disponível',
                'note': 'Configure REPLICATE_API_TOKEN para usar geração AI'
            }
        
        # Estágio 2: Análise tradicional (se disponível)
        if sistema and include_analysis:
            try:
                logger.info("Estágio 2: Analisando projeto com sistema tradicional")
                analysis_result = sistema.processar_prompt(prompt)
                resultado_completo['stages']['project_analysis'] = analysis_result
                logger.info("✅ Análise tradicional concluída")
            except Exception as e:
                logger.error(f"Erro na análise tradicional: {e}")
                resultado_completo['stages']['project_analysis'] = {
                    'success': False,
                    'error': str(e)
                }
        
        # Estágio 3: Orçamento completo (se disponível)
        if sistema and include_budget:
            try:
                logger.info("Estágio 3: Calculando orçamento completo")
                
                # Extrair informações para orçamento
                analysis_data = resultado_completo['stages'].get('project_analysis', {})
                volume_estimado = 50.0  # Volume padrão
                
                # Se análise disponível, usar volume calculado
                if analysis_data and isinstance(analysis_data, dict):
                    volume_estimado = analysis_data.get('volume_estimado', 50.0)
                
                orcamento = sistema.calcular_orçamento_completo(
                    modelo=prompt[:50] + "...",
                    volume=volume_estimado,
                    requisitos_filamento={}
                )
                
                resultado_completo['stages']['budget_calculation'] = orcamento
                logger.info("✅ Orçamento calculado")
            except Exception as e:
                logger.error(f"Erro no cálculo de orçamento: {e}")
                resultado_completo['stages']['budget_calculation'] = {
                    'success': False,
                    'error': str(e)
                }
        
        # Determinar status geral
        success_stages = sum(1 for stage in resultado_completo['stages'].values() 
                           if isinstance(stage, dict) and stage.get('success', False))
        total_stages = len(resultado_completo['stages'])
        
        if success_stages == total_stages:
            resultado_completo['overall_status'] = 'complete'
        elif success_stages > 0:
            resultado_completo['overall_status'] = 'partial'
        else:
            resultado_completo['overall_status'] = 'failed'
        
        resultado_completo['completion_rate'] = f"{success_stages}/{total_stages} estágios"
        
        return jsonify(resultado_completo)
        
    except Exception as e:
        logger.error(f"Erro no projeto completo LGM: {e}")
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500

# Middleware para logging de requisições
@app.before_request
def log_request():
    """Log de todas as requisições"""
    logger.info(f"{request.method} {request.path} - {request.remote_addr}")

# Middleware para tratamento de erros
@app.errorhandler(404)
def not_found(error):
    """Página não encontrada"""
    return jsonify({
        'error': 'Endpoint não encontrado',
        'path': request.path,
        'method': request.method
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Erro interno do servidor"""
    return jsonify({
        'error': 'Erro interno do servidor',
        'message': 'Tente novamente em alguns momentos'
    }), 500

# Função de inicialização
def main():
    """Função principal"""
    print("=== SISTEMA DE MODELAGEM INTELIGENTE 3D ===")
    print("Inicializando servidor de integração...")
    
    # Inicializar sistema
    if not inicializar_sistema():
        print("❌ Erro ao inicializar sistema")
        return
    
        # Configurar servidor
        port = int(os.environ.get('PORT', 5000))
        host = os.environ.get('HOST', '0.0.0.0')
        debug = os.environ.get('DEBUG', 'false').lower() == 'true'
        
        print(f"🌐 Servidor rodando em: http://{host}:{port}")
        print(f"🔗 Interface web: http://{host}:{port}/")
        print(f"📊 Status API: http://{host}:{port}/api/status")
        print(f"🏥 Health check: http://{host}:{port}/api/health")
        print(f"💾 Modelos 3D: http://{host}:{port}/models")
        
        # Mostrar status do LGM
        if sistema_lgm:
            stats = sistema_lgm.get_usage_stats()
            print(f"🤖 Sistema LGM: ATIVO (método: {stats['method']})")
            print(f"🔧 LGM Status: http://{host}:{port}/api/lgm/status")
            print(f"📝 Projeto Completo: http://{host}:{port}/api/lgm/projeto-completo")
        else:
            print("🤖 Sistema LGM: INATIVO (configure REPLICATE_API_TOKEN)")
        
        if debug:
            print("🐛 Modo debug ativado")
        
        print("\n=== SISTEMA PRONTO ===")
        print("API Slant 3D integrada com sucesso!")
        print("Interface web disponível para uso")
        print("Sistema LGM disponível para geração de modelos 3D")
        print("Endpoint integrado: texto → modelo 3D + análise + orçamento")
        
        # Iniciar servidor Flask
        try:
            app.run(host=host, port=port, debug=debug)
        except KeyboardInterrupt:
            print("\n🔴 Servidor interrompido pelo usuário")
        except Exception as e:
            print(f"❌ Erro no servidor: {e}")
        finally:
            print("👋 Servidor finalizado")

if __name__ == "__main__":
    main()