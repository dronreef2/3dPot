#!/usr/bin/env python3
"""
Script para iniciar o servidor do backend 3dPot v2.0 com integrações
"""

import os
import sys
import asyncio
import subprocess
import argparse
import time

def run_command(cmd, description):
    """Executa um comando com print de descrição"""
    print(f"\n▶️ {description}")
    print(f"📝 Comando: {cmd}")
    
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )
        print(f"✅ {description} - Concluído com sucesso")
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Erro")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
        return None

def check_env_vars():
    """Verifica se as variáveis de ambiente necessárias estão configuradas"""
    required_vars = [
        "MINIMAX_API_KEY",
        "DATABASE_URL",
        "SECRET_KEY",
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("⚠️ As seguintes variáveis de ambiente não estão configuradas:")
        for var in missing_vars:
            print(f"   - {var}")
        
        print("\n💡 Configure essas variáveis no arquivo .env na raiz do backend")
        print("   Copie o arquivo .env.example para .env e preencha com seus valores")
        return False
    
    return True

def start_database():
    """Inicia o PostgreSQL usando docker-compose"""
    docker_compose_path = os.path.join("docker-compose.yml")
    if not os.path.exists(docker_compose_path):
        print("⚠️ Arquivo docker-compose.yml não encontrado")
        return False
    
    print("🔧 Iniciando PostgreSQL com docker-compose...")
    cmd = "docker-compose up -d postgres"
    result = run_command(cmd, "Iniciar PostgreSQL")
    return result is not None

def start_minimax_service():
    """Inicia o serviço Minimax diretamente"""
    print("🚀 Iniciando serviço Minimax...")
    
    # Comando para executar o script de teste
    cmd = "python3 /workspace/test_minimax_service.py"
    result = run_command(cmd, "Executar testes Minimax")
    return result is not None

def start_api_server():
    """Inicia o servidor FastAPI"""
    print("🚀 Iniciando servidor API...")
    
    # Comando para executar o servidor
    cmd = "uvicorn backend.main:app --reload --port 8000"
    result = run_command(cmd, "Iniciar servidor FastAPI")
    return result is not None

async def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Iniciar servidor 3dPot v2.0 com integrações")
    parser.add_argument("--skip-db", action="store_true", help="Pular inicialização do banco de dados")
    parser.add_argument("--skip-minimax", action="store_true", help="Pular teste do serviço Minimax")
    parser.add_argument("--only-tests", action="store_true", help="Apenas executar testes sem iniciar o servidor")
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("🔧 3dPot v2.0 - Sistema de Prototipagem Sob Demanda")
    print("=" * 70)
    
    # Verificar variáveis de ambiente
    if not check_env_vars():
        print("\n❌ Variáveis de ambiente necessárias não encontradas")
        print("Configure-as em backend/.env")
        return False
    
    # Inicializar banco de dados se não for pular
    if not args.skip_db:
        if not start_database():
            print("\n❌ Falha ao inicializar banco de dados")
            return False
        print("⏳ Aguardando inicialização do banco de dados...")
        time.sleep(5)  # Aguardar o PostgreSQL inicializar
    
    # Testar serviço Minimax se não for pular
    if not args.skip_minimax:
        if not start_minimax_service():
            print("\n❌ Falha ao testar serviço Minimax")
            return False
    
    # Verificar se deve executar apenas testes
    if args.only_tests:
        print("\n✅ Testes executados com sucesso!")
        return True
    
    # Iniciar servidor API
    if not start_api_server():
        print("\n❌ Falha ao iniciar servidor FastAPI")
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)