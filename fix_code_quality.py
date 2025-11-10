#!/usr/bin/env python3
"""
Script para corrigir problemas de qualidade de código no projeto 3dPot.
Corrige: isort, flake8, formatação black
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Executa comando e exibe output."""
    print(f"\n🔧 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - Sucesso")
            if result.stdout.strip():
                print(f"Output: {result.stdout.strip()}")
        else:
            print(f"❌ {description} - Erro")
            if result.stdout.strip():
                print(f"Stdout: {result.stdout.strip()}")
            if result.stderr.strip():
                print(f"Stderr: {result.stderr.strip()}")
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Erro ao executar comando: {e}")
        return False

def fix_isort_issues():
    """Corrige problemas de import sorting."""
    directories = [
        "codigos",
        "tests", 
        "browser",
        "external_api"
    ]
    
    success = True
    for directory in directories:
        if os.path.exists(directory):
            print(f"\n📦 Corrigindo imports em {directory}/...")
            cmd = f"isort {directory}/ --profile black --line-length 88"
            if not run_command(cmd, f"Sorting imports in {directory}"):
                success = False
        else:
            print(f"⚠️  Directory {directory} not found, skipping...")
    
    return success

def fix_black_formatting():
    """Aplica formatação black."""
    directories = [
        "codigos",
        "tests",
        "browser", 
        "external_api"
    ]
    
    success = True
    for directory in directories:
        if os.path.exists(directory):
            print(f"\n🎨 Formatando código em {directory}/...")
            cmd = f"black {directory}/ --line-length 88"
            if not run_command(cmd, f"Black formatting in {directory}"):
                success = False
        else:
            print(f"⚠️  Directory {directory} not found, skipping...")
    
    return success

def fix_flake8_issues():
    """Corrige problemas do flake8."""
    print(f"\n🔍 Verificando problemas do flake8...")
    
    # Primeiro, vamos verificar os problemas específicos
    cmd = "flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics"
    run_command(cmd, "Verificando erros críticos do flake8")
    
    # Tentar auto-corrigir alguns problemas
    cmd = "autopep8 --in-place --aggressive --aggressive ."
    run_command(cmd, "Auto-corrigindo com autopep8")
    
    return True

def install_required_tools():
    """Instala ferramentas necessárias."""
    tools = ["isort", "black", "flake8", "autopep8"]
    
    for tool in tools:
        cmd = f"pip install {tool}"
        if not run_command(cmd, f"Instalando {tool}"):
            print(f"⚠️  Could not install {tool}, continuing...")
    
    return True

def add_missing_imports():
    """Adiciona imports que podem estar faltando."""
    files_to_check = [
        "codigos/raspberry-pi/estacao_qc.py",
        "codigos/raspberry-pi/estacao-qc-avancada.py"
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"\n📄 Verificando imports em {file_path}...")
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Verificar se cv2 está importado em arquivos que usam opencv
            if 'cv2.' in content and 'import cv2' not in content:
                print(f"⚠️  Adicionando import cv2 em {file_path}")
                lines = content.split('\n')
                insert_index = 0
                
                # Encontrar onde inserir o import
                for i, line in enumerate(lines):
                    if line.startswith('import ') or line.startswith('from '):
                        insert_index = i + 1
                    elif line.strip() == '':
                        continue
                    else:
                        break
                
                lines.insert(insert_index, 'import cv2')
                lines.insert(insert_index + 1, 'import numpy as np')
                
                with open(file_path, 'w') as f:
                    f.write('\n'.join(lines))
                
                print(f"✅ Added missing cv2 import to {file_path}")
        else:
            print(f"⚠️  File {file_path} not found")

def main():
    """Função principal."""
    print("🚀 Iniciando correção de qualidade de código para 3dPot")
    print("=" * 60)
    
    # Instalar ferramentas
    install_required_tools()
    
    # Adicionar imports faltantes
    add_missing_imports()
    
    # Corrigir isort
    if not fix_isort_issues():
        print("❌ Some isort issues could not be fixed")
    
    # Aplicar black
    if not fix_black_formatting():
        print("❌ Some black formatting issues could not be fixed")
    
    # Corrigir flake8
    fix_flake8_issues()
    
    print("\n" + "=" * 60)
    print("🎯 Verificação final...")
    
    # Verificação final
    run_command("isort --check-only .", "Verificação final - isort")
    run_command("black --check .", "Verificação final - black")
    run_command("flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics", "Verificação final - flake8")
    
    print("\n✨ Correção de código concluída!")
    print("Agora você pode fazer commit e push para acionar os workflows.")

if __name__ == "__main__":
    main()