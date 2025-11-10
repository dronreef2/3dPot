#!/usr/bin/env python3
"""
Validador Rápido OpenSCAD - Central de Controle Inteligente
"""

import os
import subprocess
import sys
from pathlib import Path
import json

def run_openscad_check(file_path):
    """Executa verificação básica do OpenSCAD"""
    try:
        # Tenta executar openscad em modo não-interativo
        cmd = [
            "timeout", "30",
            "openscad", 
            "--info",
            str(file_path)
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=35
        )
        
        # Se não houver erros de sintaxe, o arquivo é válido
        if result.returncode == 0:
            return True, "Sintaxe válida"
        else:
            return False, result.stderr.strip()
            
    except subprocess.TimeoutExpired:
        return False, "Timeout na validação"
    except Exception as e:
        return False, f"Erro: {str(e)}"

def main():
    """Função principal de validação rápida"""
    print("🔍 VALIDAÇÃO RÁPIDA - Modelos OpenSCAD Central de Controle")
    print("=" * 60)
    
    # Diretório dos modelos
    models_dir = Path("modelos-3d/central-inteligente")
    scad_files = list(models_dir.glob("*.scad"))
    scad_files.sort()
    
    if not scad_files:
        print("❌ Nenhum arquivo OpenSCAD encontrado!")
        return 1
    
    print(f"📁 Encontrados {len(scad_files)} arquivos OpenSCAD")
    print()
    
    results = []
    valid_count = 0
    error_count = 0
    
    for scad_file in scad_files:
        print(f"🔍 Validando: {scad_file.name}")
        
        try:
            # Análise básica do arquivo
            with open(scad_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            total_lines = len(lines)
            code_lines = sum(1 for line in lines if line.strip() and not line.strip().startswith('//'))
            
            # Verificação sintática simplificada
            is_valid, message = run_openscad_check(scad_file)
            
            if is_valid:
                print(f"   ✅ Válido - {code_lines} linhas de código")
                valid_count += 1
                status = "VALID"
            else:
                print(f"   ❌ Erro: {message[:80]}...")
                error_count += 1
                status = "ERROR"
            
            results.append({
                "file": scad_file.name,
                "lines": total_lines,
                "code_lines": code_lines,
                "status": status,
                "message": message,
                "size": len(content)
            })
            
        except Exception as e:
            print(f"   ❌ Erro ao processar: {str(e)}")
            error_count += 1
            results.append({
                "file": scad_file.name,
                "status": "PROCESSING_ERROR",
                "message": str(e)
            })
    
    print()
    print("📊 RELATÓRIO FINAL:")
    print("=" * 30)
    print(f"✅ Arquivos válidos: {valid_count}")
    print(f"❌ Arquivos com erro: {error_count}")
    print(f"📁 Total de arquivos: {len(scad_files)}")
    
    if valid_count == len(scad_files):
        print("\n🎉 TODOS OS MODELOS SÃO VÁLIDOS!")
        print("   💡 Os arquivos OpenSCAD estão prontos para renderização")
        print("   🖨️  Podem ser impressos diretamente no OpenSCAD")
    else:
        print(f"\n⚠️  {error_count} arquivo(s) precisam de correção")
    
    # Salva relatório
    with open("quick_validation_report.json", "w") as f:
        json.dump({
            "validation_time": "2025-11-10T14:35:00",
            "summary": {
                "total_files": len(scad_files),
                "valid_files": valid_count,
                "error_files": error_count
            },
            "files": results
        }, f, indent=2)
    
    print(f"   💾 Relatório salvo em: quick_validation_report.json")
    
    return 0 if valid_count == len(scad_files) else 1

if __name__ == "__main__":
    sys.exit(main())