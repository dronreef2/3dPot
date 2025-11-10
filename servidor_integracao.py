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

def inicializar_sistema():
    """Inicializar sistema de modelagem inteligente"""
    global sistema
    try:
        sistema = ModelagemInteligente(API_KEY)
        logger.info("Sistema de modelagem inteligente inicializado com sucesso")
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
        if sistema and sistema.api:
            usage = sistema.api.check_usage()
            return jsonify({
                'status': 'online',
                'api_connected': True,
                'usage': {
                    'remaining': usage.remaining_requests if usage else 0,
                    'limit': usage.limit if usage else 100,
                    'tier': usage.account_tier if usage else 'free'
                },
                'message': 'API Slant 3D funcionando normalmente'
            })
        else:
            return jsonify({
                'status': 'error',
                'api_connected': False,
                'message': 'Sistema não inicializado'
            }), 500
    except Exception as e:
        logger.error(f"Erro ao verificar status: {e}")
        return jsonify({
            'status': 'error',
            'api_connected': False,
            'message': f'Erro interno: {str(e)}'
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
        'version': '1.0.0'
    })

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
    
    if debug:
        print("🐛 Modo debug ativado")
    
    print("\n=== SISTEMA PRONTO ===")
    print("API Slant 3D integrada com sucesso!")
    print("Interface web disponível para uso")
    print("Prompt de sistema funcionando")
    
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