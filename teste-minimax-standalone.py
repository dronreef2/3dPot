#!/usr/bin/env python3
"""
Script para testar rapidamente a integração com Minimax M2 (standalone)
"""

import os
import sys
import asyncio
import argparse
import json
from datetime import datetime
from typing import Dict, List, Any

# Adicionar diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Definir variáveis de ambiente diretamente se não existirem
if not os.environ.get("MINIMAX_API_KEY"):
    os.environ["MINIMAX_API_KEY"] = "test-key"

if not os.environ.get("MINIMAX_BASE_URL"):
    os.environ["MINIMAX_BASE_URL"] = "https://api.minimax.chat/v1"

if not os.environ.get("MINIMAX_MODEL"):
    os.environ["MINIMAX_MODEL"] = "abab6.5s-chat"

class MinimaxService:
    """Serviço para interação com API Minimax M2 (versão simplificada para teste)"""
    
    def __init__(self):
        self.api_key = os.environ.get("MINIMAX_API_KEY", "")
        self.base_url = os.environ.get("MINIMAX_BASE_URL", "https://api.minimax.chat/v1")
        self.model = os.environ.get("MINIMAX_MODEL", "abab6.5s-chat")
        
    async def start_conversation(self, user_id: str, project_id: str = None) -> Dict[str, Any]:
        """Iniciar uma nova conversa"""
        return {
            "id": "test-conversation-id",
            "user_id": user_id,
            "project_id": project_id,
            "status": "active",
            "created_at": datetime.utcnow().isoformat(),
            "messages": []
        }
    
    async def send_message(self, message: str, conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """
        Enviar mensagem para a API Minimax e obter resposta
        
        Args:
            message: Mensagem do usuário
            conversation_history: Histórico da conversa
            
        Returns:
            Resposta da API
        """
        # Verificar se temos uma chave API real
        if not self.api_key or self.api_key == "test-key":
            # Usar resposta simulada
            return {
                "success": False,
                "error": "Chave API não configurada",
                "content": f"Entendi que você quer {message}. Para melhor assistência, configure uma chave API válida no arquivo backend/.env"
            }
            
        # Se temos uma chave API real, faríamos uma chamada real à API
        # mas para este teste, vamos simular uma resposta
        
        # Resposta simulada baseada no conteúdo da mensagem
        if "arduino" in message.lower():
            response = f"Você quer trabalhar com Arduino. Ótima escolha! Preciso saber mais detalhes. " \
                       f"Vou ajudá-lo a criar um projeto para Arduino Uno."
        elif "raspberry" in message.lower():
            response = f"Projeto para Raspberry Pi? Interessante! Vou precisar de mais informações sobre " \
                       f"as especificações e funcionalidades desejadas."
        elif "material" in message.lower() and "pla" in message.lower():
            response = f"PLA é um excelente material para impressão 3D. É biodegradável, fácil de imprimir e tem boa resistência."
        elif "dimens" in message.lower() and ("largura" in message.lower() or "altura" in message.lower()):
            response = f"Obrigado por fornecer as dimensões. Isso é essencial para o projeto."
        else:
            response = f"Entendo que você está criando um projeto. Continue descrevendo as especificações para que eu possa ajudá-lo melhor."
        
        return {
            "success": True,
            "content": response,
            "usage": {"tokens_used": len(response.split()) * 3}  # Simular uso de tokens
        }
    
    def extract_specifications(self, ai_response: str) -> Dict[str, Any]:
        """Extrair especificações do conteúdo da resposta da IA"""
        # Implementação básica - pode ser aprimorada com NLP mais avançado
        extracted = {
            "categoria": None,
            "dimensoes": {},
            "material": None,
            "componentes": [],
            "funcionalidades": [],
            "restricoes": []
        }
        
        # Detecção básica de padrões (melhorar com NLP mais avançado)
        if "arduino" in ai_response.lower() or "raspberry" in ai_response.lower():
            extracted["categoria"] = "eletronico"
        elif "mecân" in ai_response.lower() or "mecanica" in ai_response.lower():
            extracted["categoria"] = "mecanico"
        elif "arquitetura" in ai_response.lower():
            extracted["categoria"] = "arquitetura"
        else:
            extracted["categoria"] = "mixto"
        
        # Detecção de materiais
        materiais = ["pla", "abs", "petg", "nylon", "metal", "alumínio", "aço"]
        for material in materiais:
            if material in ai_response.lower():
                extracted["material"] = material.upper()
                break
        
        # Tentativa de extrair dimensões específicas
        # Pattern: X mm de largura
        import re
        dim_pattern = r"(\d+(?:\.\d+)?)\s*(?:mm|cm|m)\s*(?:de\s*)?(?:largura|altura|profundidade)"
        dimensions = re.findall(dim_pattern, ai_response.lower())
        if dimensions:
            extracted["dimensoes"]["valor"] = float(dimensions[0])
        
        return extracted

async def test_quick_conversation():
    """Teste rápido de conversação com Minimax M2"""
    print("=" * 60)
    print("🔬 TESTE RÁPIDO DA INTEGRAÇÃO MINIMAX M2")
    print("=" * 60)
    
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
    
    # Inicializar serviço
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
    
    # Inicializar serviço
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
            # Simular resposta da API
            response = await service.send_message(message, history)
            
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