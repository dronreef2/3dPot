#!/usr/bin/env python3
"""
Script para testar rapidamente a integração com Minimax M2

⚠️ NOTA: Este é um dos vários scripts de teste Minimax disponíveis:
- teste-rapido-minimax.py (este script): Teste rápido e básico
- teste-minimax-standalone.py: Teste standalone mais completo
- Para uso em produção, use o serviço backend/services/minimax_service.py
"""

import os
import sys
import asyncio
import argparse
import json
from datetime import datetime
from typing import Dict, List, Any

# Adicionar diretório pai ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.minimax_service import MinimaxService

async def test_quick_conversation():
    """Teste rápido de conversação com Minimax M2"""
    print("=" * 60)
    print("🔬 TESTE RÁPIDO DA INTEGRAÇÃO MINIMAX M2")
    print("=" * 60)
    
    # Verificar se a chave da API está configurada
    api_key = os.environ.get("MINIMAX_API_KEY")
    if not api_key:
        print("⚠️ MINIMAX_API_KEY não está definida no ambiente")
        print("Configure no arquivo backend/.env ou na variável de ambiente")
        print("\nSugestão: Adicione uma chave de teste ao arquivo backend/.env")
        print("MINIMAX_API_KEY=your-minimax-api-key-here")
        return False
    
    # Inicializar serviço
    print("\n▶️ Inicializando serviço Minimax...")
    service = MinimaxService()
    print(f"   Base URL: {service.base_url}")
    print(f"   Model: {service.model}")
    print("   ✅ Serviço inicializado")
    
    # Teste 1: Mensagem simples
    print("\n▶️ Teste 1: Mensagem simples")
    message = "Quero criar um gabinete para Arduino Uno em PLA"
    
    try:
        response = await service.send_message(message, [])
        
        if response["success"]:
            print("   ✅ Resposta recebida com sucesso!")
            print(f"   Conteúdo: {response['content'][:100]}...")
            
            # Testar extração de especificações
            print("\n▶️ Teste 2: Extração de especificações")
            specs = service.extract_specifications(response["content"])
            
            print("   Especificações extraídas:")
            for key, value in specs.items():
                if value:
                    print(f"   - {key}: {value}")
            
            print("\n✅ Testes concluídos com sucesso!")
            return True
        else:
            print(f"   ⚠️ Resposta de fallback: {response['content'][:100]}...")
            print(f"   Erro: {response.get('error', 'Desconhecido')}")
            print("\n   Isso é esperado se a chave API não for válida")
            return False
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False

async def test_extraction():
    """Teste de extração de especificações com exemplos de texto"""
    print("\n\n" + "=" * 60)
    print("🔬 TESTE DE EXTRAÇÃO DE ESPECIFICAÇÕES")
    print("=" * 60)
    
    # Inicializar serviço (não precisamos da API key para este teste)
    service = MinimaxService()
    
    # Exemplos de texto para testar extração
    examples = [
        {
            "name": "Projeto Arduino",
            "text": "Quero criar um gabinete para Arduino Uno em PLA. O gabinete deve ter 10cm de largura, 7cm de profundidade e 4cm de altura. Precisa ter aberturas para ventilação e acesso aos conectores."
        },
        {
            "name": "Projeto Mecânico",
            "text": "Preciso de uma peça mecânica em ABS. A peça é uma engrenagem com diâmetro de 50mm e altura de 10mm. Deve ter 20 dentes e ser impressa em ABS."
        },
        {
            "name": "Projeto Eletrônico",
            "text": "Vou projetar uma PCB em FR4. A placa terá 50mm x 50mm e толщиной 1.6mm. É para um circuito de controle de LED RGB com microcontroller ATMega328P."
        },
        {
            "name": "Projeto Arquitetura",
            "text": "Preciso de um modelo arquitetônico em escala 1:100. É uma casa de dois andares com 8m x 10m em implantação, altura de 6m. Construído em PLA."
        }
    ]
    
    print("\n▶️ Testando extração de especificações em diferentes textos...\n")
    
    all_success = True
    
    for example in examples:
        print(f"\n📄 Exemplo: {example['name']}")
        print(f"   Texto: {example['text'][:50]}...")
        
        try:
            specs = service.extract_specifications(example["text"])
            
            print("   Especificações extraídas:")
            for key, value in specs.items():
                if value:
                    print(f"   - {key}: {value}")
            
            # Verificar se pelo menos a categoria foi extraída
            if not specs["categoria"]:
                print("   ⚠️ Categoria não extraída corretamente")
                all_success = False
                
        except Exception as e:
            print(f"   ❌ Erro: {e}")
            all_success = False
    
    return all_success

async def simulate_conversation():
    """Simula uma conversa completa com a IA"""
    print("\n\n" + "=" * 60)
    print("🔬 SIMULAÇÃO DE CONVERSA")
    print("=" * 60)
    
    # Inicializar serviço (não precisamos da API key para este teste se usarmos fallback)
    service = MinimaxService()
    
    # Lista de mensagens na conversa
    messages = [
        "Quero criar um suporte para Arduino Uno",
        "Deve ser feito em PLA",
        "Vou precisar de aberturas para ventilação",
        "Preciso de 10cm de largura",
        "5cm de profundidade seria suficiente",
        "A altura deve ser 5cm também",
        "Quero um botão power na frente",
    ]
    
    print("\n▶️ Simulando conversa progressiva...\n")
    
    # Histórico vazio
    history = []
    
    # Simular cada mensagem
    for i, message in enumerate(messages, 1):
        print(f"\n💬 Usuário: {message}")
        
        try:
            # Se a chave API estiver definida, chamar a API, senão usar fallback
            api_key = os.environ.get("MINIMAX_API_KEY")
            if api_key:
                response = await service.send_message(message, history)
            else:
                # Simular resposta de fallback
                response = {
                    "success": False,
                    "content": f"Entendi que você quer {message}. Continue descrevendo seu projeto para que eu possa extrair mais especificações.",
                    "error": "API key não configurada"
                }
            
            # Adicionar ao histórico
            history.append({"role": "user", "content": message})
            history.append({"role": "assistant", "content": response["content"]})
            
            # Exibir resposta
            content = response["content"]
            print(f"🤖 IA: {content[:100]}...")
            
            # Extrair especificações desta resposta
            specs = service.extract_specifications(content)
            
            # Mostrar especificações encontradas
            found_specs = {k: v for k, v in specs.items() if v}
            if found_specs:
                print("   Especificações encontradas:")
                for key, value in found_specs.items():
                    print(f"   - {key}: {value}")
            
        except Exception as e:
            print(f"❌ Erro ao enviar mensagem: {e}")
    
    # Resumo final
    print("\n\n📊 Resumo final da conversa")
    print(f"   Total de mensagens trocadas: {len(messages) * 2}")
    
    # Extrair especificações de toda a conversa
    combined_content = "\n\n".join([msg["content"] for msg in history if msg["role"] == "assistant"])
    final_specs = service.extract_specifications(combined_content)
    
    print("\n   Especificações finais extraídas:")
    for key, value in final_specs.items():
        if value:
            print(f"   - {key}: {value}")
    
    return True

async def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Teste rápido da integração Minimax M2")
    parser.add_argument("--no-api", action="store_true", help="Não testar com API real (usar apenas fallback)")
    parser.add_argument("--quick", action="store_true", help="Teste rápido de mensagem simples")
    parser.add_argument("--extract", action="store_true", help="Teste de extração de especificações")
    parser.add_argument("--conversation", action="store_true", help="Simular conversa completa")
    
    args = parser.parse_args()
    
    # Por padrão, executar todos os testes
    run_all = not (args.quick or args.extract or args.conversation)
    
    success = True
    
    if args.quick or run_all:
        success = success and await test_quick_conversation()
    
    if args.extract or run_all:
        success = success and await test_extraction()
    
    if args.conversation or run_all:
        success = success and await simulate_conversation()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ TODOS OS TESTES EXECUTADOS COM SUCESSO")
    else:
        print("⚠️ ALGUNS TESTES FALHARAM - VERIFIQUE OS LOGS ACIMA")
    print("=" * 60)
    
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)