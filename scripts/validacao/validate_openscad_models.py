#!/usr/bin/env python3
"""
Validador de Modelos OpenSCAD - Central de Controle Inteligente
Valida sintaxe e renderiza os 6 modelos da Central de Controle 3dPot
"""

import os
import subprocess
import sys
from pathlib import Path
import json
from datetime import datetime

def setup_matplotlib_for_plotting():
    """Setup matplotlib for non-interactive plotting"""
    import warnings
    import matplotlib.pyplot as plt
    import seaborn as sns
    
    warnings.filterwarnings('default')
    plt.switch_backend("Agg")
    plt.style.use("seaborn-v0_8")
    sns.set_palette("husl")
    plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "WenQuanYi Zen Hei", "PingFang SC", "Arial Unicode MS", "Hiragino Sans GB"]
    plt.rcParams["axes.unicode_minus"] = False

class OpenSCADValidator:
    def __init__(self, models_dir="modelos-3d/central-inteligente"):
        self.models_dir = Path(models_dir)
        self.results = {
            "validation_time": datetime.now().isoformat(),
            "validator_version": "1.0",
            "total_files": 0,
            "valid_files": [],
            "error_files": [],
            "warning_files": [],
            "stl_generated": [],
            "stl_failed": []
        }
    
    def find_openscad_files(self):
        """Encontra todos os arquivos .scad no diretório especificado"""
        scad_files = []
        if self.models_dir.exists():
            scad_files = list(self.models_dir.glob("*.scad"))
            scad_files.sort()
        return scad_files
    
    def validate_syntax(self, scad_file):
        """Valida a sintaxe de um arquivo OpenSCAD"""
        try:
            # Comando para validar sintaxe sem gerar STL
            cmd = [
                "openscad", 
                "--export-format", "stl",
                "-o", "/tmp/validation_temp.stl",  # Arquivo temporário
                str(scad_file)
            ]
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=60,
                env=dict(os.environ, DISPLAY=":99")  # Usar display virtual se disponível
            )
            
            return {
                "valid": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "file": str(scad_file)
            }
            
        except subprocess.TimeoutExpired:
            return {
                "valid": False,
                "stdout": "",
                "stderr": "Timeout durante validação",
                "file": str(scad_file)
            }
        except Exception as e:
            return {
                "valid": False,
                "stdout": "",
                "stderr": f"Erro durante validação: {str(e)}",
                "file": str(scad_file)
            }
    
    def generate_stl(self, scad_file, stl_output_path):
        """Gera arquivo STL a partir do OpenSCAD"""
        try:
            cmd = [
                "openscad",
                "-o", str(stl_output_path),
                str(scad_file)
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
                env=dict(os.environ, DISPLAY=":99")
            )
            
            # Verifica se o arquivo STL foi criado e não está vazio
            stl_created = stl_output_path.exists() and stl_output_path.stat().st_size > 0
            
            return {
                "success": result.returncode == 0 and stl_created,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "stl_size": stl_output_path.stat().st_size if stl_created else 0,
                "stl_path": str(stl_output_path)
            }
            
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Erro ao gerar STL: {str(e)}",
                "stl_size": 0,
                "stl_path": str(stl_output_path)
            }
    
    def analyze_openscad_code(self, scad_file):
        """Analisa o código OpenSCAD para informações detalhadas"""
        try:
            with open(scad_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            analysis = {
                "file_size": len(content),
                "total_lines": len(lines),
                "comment_lines": sum(1 for line in lines if line.strip().startswith('//')),
                "code_lines": sum(1 for line in lines if line.strip() and not line.strip().startswith('//')),
                "empty_lines": sum(1 for line in lines if not line.strip()),
                "modules": [],
                "functions": [],
                "variables": []
            }
            
            # Procura por módulos, funções e variáveis
            for line in lines:
                stripped = line.strip()
                if stripped.startswith('module '):
                    module_name = stripped.split('(')[0].replace('module ', '')
                    analysis["modules"].append(module_name)
                elif stripped.startswith('function '):
                    func_name = stripped.split('(')[0].replace('function ', '')
                    analysis["functions"].append(func_name)
                elif '=' in stripped and not stripped.startswith('//'):
                    var_name = stripped.split('=')[0].strip()
                    if var_name:
                        analysis["variables"].append(var_name)
            
            return analysis
            
        except Exception as e:
            return {"error": f"Erro ao analisar código: {str(e)}"}
    
    def run_validation(self):
        """Executa validação completa dos modelos OpenSCAD"""
        print("🔍 Iniciando validação dos modelos OpenSCAD...")
        print("=" * 60)
        
        # Encontra arquivos OpenSCAD
        scad_files = self.find_openscad_files()
        self.results["total_files"] = len(scad_files)
        
        if not scad_files:
            print("❌ Nenhum arquivo OpenSCAD encontrado no diretório")
            return self.results
        
        print(f"📁 Encontrados {len(scad_files)} arquivos OpenSCAD:")
        for file in scad_files:
            print(f"   - {file.name}")
        print()
        
        # Valida cada arquivo
        for scad_file in scad_files:
            print(f"🔍 Validando: {scad_file.name}")
            print("-" * 40)
            
            # Análise do código
            code_analysis = self.analyze_openscad_code(scad_file)
            print(f"   📊 Análise do código:")
            print(f"      - Tamanho: {code_analysis.get('file_size', 0):,} bytes")
            print(f"      - Linhas totais: {code_analysis.get('total_lines', 0)}")
            print(f"      - Linhas de código: {code_analysis.get('code_lines', 0)}")
            print(f"      - Módulos definidos: {len(code_analysis.get('modules', []))}")
            print(f"      - Funções definidas: {len(code_analysis.get('functions', []))}")
            
            # Validação de sintaxe
            syntax_result = self.validate_syntax(scad_file)
            
            if syntax_result["valid"]:
                print(f"   ✅ Sintaxe válida")
                self.results["valid_files"].append({
                    "file": str(scad_file),
                    "analysis": code_analysis
                })
                
                # Geração de STL
                stl_path = scad_file.with_suffix('.stl')
                print(f"   🖨️  Gerando arquivo STL...")
                
                stl_result = self.generate_stl(scad_file, stl_path)
                
                if stl_result["success"]:
                    print(f"   ✅ STL gerado com sucesso: {stl_result['stl_size']:,} bytes")
                    self.results["stl_generated"].append({
                        "scad_file": str(scad_file),
                        "stl_file": str(stl_path),
                        "stl_size": stl_result["stl_size"]
                    })
                else:
                    print(f"   ❌ Falha na geração do STL: {stl_result['stderr']}")
                    self.results["stl_failed"].append({
                        "scad_file": str(scad_file),
                        "error": stl_result["stderr"]
                    })
                
            else:
                print(f"   ❌ Erro de sintaxe encontrado:")
                if syntax_result["stderr"]:
                    print(f"      Erro: {syntax_result['stderr']}")
                if syntax_result["stdout"]:
                    print(f"      Saída: {syntax_result['stdout']}")
                
                self.results["error_files"].append({
                    "file": str(scad_file),
                    "error": syntax_result["stderr"],
                    "output": syntax_result["stdout"]
                })
            
            print()
        
        return self.results
    
    def generate_report(self):
        """Gera relatório detalhado da validação"""
        print("=" * 60)
        print("📋 RELATÓRIO DE VALIDAÇÃO - CENTRAL DE CONTROLE INTELIGENTE")
        print("=" * 60)
        print(f"⏰ Data/Hora: {self.results['validation_time']}")
        print(f"📁 Arquivos encontrados: {self.results['total_files']}")
        print()
        
        # Resumo geral
        valid_count = len(self.results["valid_files"])
        error_count = len(self.results["error_files"])
        stl_count = len(self.results["stl_generated"])
        stl_failed_count = len(self.results["stl_failed"])
        
        print("📊 RESUMO GERAL:")
        print(f"   ✅ Arquivos válidos: {valid_count}")
        print(f"   ❌ Arquivos com erro: {error_count}")
        print(f"   🖨️  STL gerados: {stl_count}")
        print(f"   🚫 STL falharam: {stl_failed_count}")
        print()
        
        # Detalhes dos arquivos válidos
        if self.results["valid_files"]:
            print("✅ ARQUIVOS VÁLIDOS:")
            for file_info in self.results["valid_files"]:
                scad_path = Path(file_info["file"])
                analysis = file_info["analysis"]
                print(f"   📄 {scad_path.name}")
                print(f"      Módulos: {', '.join(analysis.get('modules', [])[:3])}{'...' if len(analysis.get('modules', [])) > 3 else ''}")
                print(f"      Linhas: {analysis.get('code_lines', 0)}")
            
        # Detalhes dos arquivos com erro
        if self.results["error_files"]:
            print()
            print("❌ ARQUIVOS COM ERRO:")
            for error_info in self.results["error_files"]:
                scad_path = Path(error_info["file"])
                print(f"   📄 {scad_path.name}")
                print(f"      Erro: {error_info['error'][:100]}...")
        
        # Detalhes dos STL gerados
        if self.results["stl_generated"]:
            print()
            print("🖨️  ARQUIVOS STL GERADOS:")
            total_size = sum(stl["stl_size"] for stl in self.results["stl_generated"])
            for stl_info in self.results["stl_generated"]:
                stl_path = Path(stl_info["stl_file"])
                print(f"   📁 {stl_path.name}: {stl_info['stl_size']:,} bytes")
            print(f"   📊 Tamanho total: {total_size:,} bytes")
        
        # Recomendações
        print()
        print("💡 RECOMENDAÇÕES:")
        if valid_count == self.results["total_files"]:
            print("   🎉 Todos os modelos estão prontos para impressão 3D!")
            print("   📐 Verificar dimensões antes da impressão")
            print("   🧪 Testar montagem física dos componentes")
        else:
            print("   ⚠️  Corrigir erros de sintaxe antes da impressão")
            print("   🔍 Revisar código OpenSCAD dos arquivos com problema")
        
        # Salva relatório em JSON em outputs/relatorios/
        output_dir = Path("outputs/relatorios")
        output_dir.mkdir(parents=True, exist_ok=True)
        report_file = output_dir / "validation_report.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"   💾 Relatório salvo em: {report_file}")
        
        return self.results

def main():
    """Função principal"""
    print("🚀 VALIDADOR DE MODELOS OPENSCAD - CENTRAL DE CONTROLE INTELIGENTE 3dPot")
    print("=" * 80)
    
    # Inicializa validador
    validator = OpenSCADValidator()
    
    # Executa validação
    results = validator.run_validation()
    
    # Gera relatório
    validator.generate_report()
    
    # Retorna código de saída apropriado
    if results["error_files"]:
        print("\n❌ Validação falhou - há arquivos com erros")
        return 1
    else:
        print("\n✅ Validação bem-sucedida - todos os modelos são válidos")
        return 0

if __name__ == "__main__":
    sys.exit(main())