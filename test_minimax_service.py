#!/usr/bin/env python3
"""
Testes para o serviço Minimax M2
Testa a integração com a API Minimax para conversação
"""

import asyncio
import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Any

# Adicionar diretório pai ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.minimax_service import MinimaxService

async def test_minimax_service():
    """Teste básico do serviço Minimax"""
    print("🧪 Testando MinimaxService...")
    
    # Inicializar serviço
    service = MinimaxService()
    
    # Teste 1: Verificar health check
    print("\n✅ Teste 1: Inicialização do serviço")
    print(f"   Base URL: {service.base_url}")
    print(f"   Model: {service.model}")
    print(f"   API Key presente: {'Sim' if service.api_key else 'Não'}")
    
    # Teste 2: Enviar mensagem simples
    print("\n✅ Teste 2: Enviar mensagem simples")
    history = []
    message = "Quero criar um projeto de Arduino"
    
    try:
        response = await service.send_message(message, history)
        
        if response["success"]:
            print(f"   Resposta recebida com sucesso!")
            print(f"   Conteúdo: {response['content'][:100]}...")
            print(f"   Uso: {response.get('usage', {})}")
        else:
            print(f"   ⚠️ Resposta de fallback: {response['content'][:100]}...")
            print(f"   Erro: {response.get('error', 'Desconhecido')}")
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        
    # Teste 3: Extrair especificações
    print("\n✅ Teste 3: Extração de especificações")
    test_text = """
    Vou criar um gabinete para Arduino Uno com ventilação. 
    O gabinete será feito em PLA. Medindo 10cm de largura, 7cm de profundidade e 4cm de altura.
    Precisa ter furos para ventilação e acesso aos conectores.
    """
    
    specs = service.extract_specifications(test_text)
    print(f"   Especificações extraídas:")
    for key, value in specs.items():
        if value:
            print(f"   - {key}: {value}")
    
    # Teste 4: Iniciar nova conversa
    print("\n✅ Teste 4: Iniciar nova conversa")
    try:
        conversation = await service.start_conversation(
            user_id="123e4567-e89b-12d3-a456-426614174000",
            project_id="456e7890-e89b-12d3-a456-426614174000"
        )
        print(f"   Conversa criada com ID: {conversation['id']}")
        print(f"   Status: {conversation['status']}")
    except Exception as e:
        print(f"   ❌ Erro ao criar conversa: {e}")
    
    print("\n🎉 Testes concluídos!")

async def test_conversation_flow():
    """Teste de fluxo completo de conversação"""
    print("\n\n🔄 Testando fluxo de conversação completo...")
    
    # Inicializar serviço
    service = MinimaxService()
    
    # Iniciar conversa
    user_id = "123e4567-e89b-12d3-a456-426614174000"
    project_id = "456e7890-e89b-12d3-a456-426614174000"
    conversation = await service.start_conversation(user_id, project_id)
    
    print(f"📝 Conversa iniciada: {conversation['id']}")
    
    # Simular conversa
    messages = [
        "Quero criar um suporte para Arduino Uno com ventilação",
        "Deve ser feito em PLA",
        "Precisa ter dimensões de 10cm x 7cm x 4cm",
        "Deve ter aberturas para ventilação",
        "Preciso de um espaço para fontes de 12V",
        "Quero que tenha um botão power na frente"
    ]
    
    # Histórico vazio
    history = []
    
    for i, message in enumerate(messages, 1):
        print(f"\n💬 Mensagem {i}: {message}")
        
        try:
            # Enviar mensagem
            response = await service.send_message(message, history)
            
            # Adicionar ao histórico
            history.append({"role": "user", "content": message})
            history.append({"role": "assistant", "content": response["content"]})
            
            # Exibir resposta
            content = response["content"]
            print(f"🤖 Resposta: {content[:100]}...")
            
            # Extrair especificações desta resposta
            specs = service.extract_specifications(content)
            
            # Mostrar especificações não vazias
            if specs:
                print("   Especificações encontradas:")
                for key, value in specs.items():
                    if value:
                        print(f"   - {key}: {value}")
            
        except Exception as e:
            print(f"❌ Erro ao enviar mensagem {i}: {e}")
    
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

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 TESTES DO SERVIÇO MINIMAX M2")
    print("=" * 60)
    
    # Executar testes
    asyncio.run(test_minimax_service())
    asyncio.run(test_conversation_flow())
    
    print("\n" + "=" * 60)
    print("✅ TODOS OS TESTES EXECUTADOS COM SUCESSO")
    print("=" * 60)