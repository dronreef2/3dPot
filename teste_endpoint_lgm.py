#!/usr/bin/env python3
"""
Exemplo prático: Teste do Endpoint Integrado LGM
Script para testar facilmente o sistema completo
"""

import requests
import json
import time

# Configuração
BASE_URL = "http://localhost:5000"
ENDPOINT_PRINCIPAL = f"{BASE_URL}/api/lgm/projeto-completo"
ENDPOINT_STATUS = f"{BASE_URL}/api/lgm/status"

def verificar_servidor():
    """Verifica se o servidor está rodando"""
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Servidor ativo: {data.get('status', 'unknown')}")
            print(f"   Sistema Slant 3D: {'✅' if data.get('system_initialized') else '❌'}")
            print(f"   Sistema LGM: {'✅' if data.get('lgm_initialized') else '❌'}")
            return True
        else:
            print(f"❌ Servidor retornou status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Servidor não encontrado. Certifique-se de que está rodando:")
        print("   python3 servidor_integracao.py")
        return False
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        return False

def testar_projeto_completo(prompt):
    """Testa o endpoint de projeto completo"""
    print(f"\n🚀 TESTANDO PROJETO COMPLETO")
    print(f"📝 Prompt: '{prompt}'")
    print("-" * 50)
    
    payload = {
        "prompt": prompt,
        "include_analysis": True,
        "include_budget": True
    }
    
    start_time = time.time()
    
    try:
        response = requests.post(
            ENDPOINT_PRINCIPAL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=300  # 5 minutos timeout
        )
        
        if response.status_code == 200:
            resultado = response.json()
            elapsed = time.time() - start_time
            
            print(f"⏱️  Tempo total: {elapsed:.1f}s")
            print(f"✅ Status: {resultado.get('overall_status', 'unknown')}")
            print(f"📊 Progresso: {resultado.get('completion_rate', 'unknown')}")
            
            # Mostrar resultados por estágio
            stages = resultado.get('stages', {})
            for stage_name, stage_data in stages.items():
                status_emoji = "✅" if stage_data.get('success', False) else "❌"
                print(f"   {status_emoji} {stage_name.replace('_', ' ').title()}")
                
                if stage_name == 'lgm_generation' and stage_data.get('success'):
                    files = stage_data.get('output_files', [])
                    if files:
                        print(f"      📁 Arquivos gerados: {len(files)}")
                        for file in files[:2]:  # Mostrar apenas os 2 primeiros
                            print(f"         - {file}")
                
                elif stage_name == 'project_analysis' and stage_data.get('success'):
                    print(f"      📏 Volume: {stage_data.get('volume_estimado', 0):.1f}cm³")
                    print(f"      🧱 Materiais: {', '.join(stage_data.get('materiais_recomendados', []))}")
                
                elif stage_name == 'budget_calculation' and stage_data.get('success'):
                    custos = stage_data.get('custos', {})
                    print(f"      💰 Custo total: R$ {custos.get('total', 0):.2f}")
                    print(f"      ⏱️  Tempo estimado: {stage_data.get('tempo_estimado', 'N/A')}")
            
            return True
        else:
            print(f"❌ Erro HTTP {response.status_code}")
            print(f"   Resposta: {response.text[:200]}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Timeout: O processo demorou mais de 5 minutos")
        return False
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False

def mostrar_exemplos():
    """Mostra exemplos de prompts para testar"""
    exemplos = [
        "um carro de corrida vermelho com detalhes metálicos",
        "um robô humanoide com olhos LED azuis",
        "uma Xícara de café com steam realista",
        "um drone quadcopter com proteção de hélices",
        "uma estatua de gato sentado elegante",
        "uma chave inglesa ajustável em 3D",
        "um relógio de pulso digital moderno",
        "um suporte para celular em formato de árvore"
    ]
    
    print("\n🎯 EXEMPLOS DE PROMPTS:")
    for i, exemplo in enumerate(exemplos, 1):
        print(f"   {i}. {exemplo}")
    
    return exemplos

def menu_interativo():
    """Menu interativo para testes"""
    while True:
        print("\n" + "="*60)
        print("🤖 TESTE DO SISTEMA LGM INTEGRADO")
        print("="*60)
        print("1. Verificar status do servidor")
        print("2. Testar projeto completo (exemplo 1)")
        print("3. Testar projeto completo (exemplo 2)")
        print("4. Testar projeto completo (exemplo 3)")
        print("5. Mostrar exemplos de prompts")
        print("6. Entrar com prompt personalizado")
        print("0. Sair")
        print("-"*60)
        
        opcao = input("Escolha uma opção: ").strip()
        
        if opcao == "0":
            print("👋 Encerrando...")
            break
        elif opcao == "1":
            verificar_servidor()
        elif opcao == "2":
            testar_projeto_completo("um carro de corrida vermelho com detalhes metálicos")
        elif opcao == "3":
            testar_projeto_completo("um robô humanoide com olhos LED azuis")
        elif opcao == "4":
            testar_projeto_completo("uma Xícara de café com steam realista")
        elif opcao == "5":
            exemplos = mostrar_exemplos()
        elif opcao == "6":
            prompt = input("Digite seu prompt: ").strip()
            if prompt:
                testar_projeto_completo(prompt)
            else:
                print("❌ Prompt vazio")
        else:
            print("❌ Opção inválida")

def teste_rapido():
    """Teste rápido com exemplo pré-definido"""
    print("🚀 TESTE RÁPIDO - SISTEMA LGM INTEGRADO")
    print("="*50)
    
    if not verificar_servidor():
        return False
    
    # Teste com exemplo simples
    return testar_projeto_completo("um dado de 6 faces com textura de madeira")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        teste_rapido()
    elif len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        menu_interativo()
    else:
        print("🤖 Script de Teste - Sistema LGM Integrado")
        print("\nUse:")
        print("  python3 teste_endpoint_lgm.py --quick    # Teste rápido")
        print("  python3 teste_endpoint_lgm.py --interactive  # Menu interativo")
        print("\nCertifique-se de que o servidor está rodando:")
        print("  python3 servidor_integracao.py")
