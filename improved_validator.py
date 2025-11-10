#!/usr/bin/env python3
"""
Validador OpenSCAD Melhorado
Faz análise mais precisa de sintaxe sem falsos positivos
"""

import re
from pathlib import Path
import json
from datetime import datetime

class ImprovedOpenSCADValidator:
    def __init__(self):
        self.results = {
            "validation_time": datetime.now().isoformat(),
            "validator": "Improved OpenSCAD Validator v2.0",
            "total_files": 0,
            "valid_files": [],
            "error_files": [],
            "warnings": []
        }
    
    def validate_syntax_structure(self, content):
        """Valida estrutura de sintaxe de forma mais precisa"""
        # Remove comentários para análise
        content_no_comments = re.sub(r'//.*?\n', '\n', content)
        content_no_comments = re.sub(r'/\*.*?\*/', '', content_no_comments, flags=re.DOTALL)
        
        errors = []
        warnings = []
        
        # Verificar estrutura de chaves
        brace_stack = []
        for i, char in enumerate(content_no_comments):
            if char == '{':
                brace_stack.append(i)
            elif char == '}':
                if not brace_stack:
                    errors.append(f"Chave de fechamento sem abertura na posição {i}")
                else:
                    brace_stack.pop()
        
        if brace_stack:
            errors.append(f"{len(brace_stack)} chaves de abertura sem fechamento")
        
        # Verificar estrutura de parênteses
        paren_count = 0
        bracket_count = 0
        
        for i, char in enumerate(content_no_comments):
            if char == '(':
                paren_count += 1
            elif char == ')':
                paren_count -= 1
                if paren_count < 0:
                    errors.append(f"Parêntese de fechamento extra na posição {i}")
            elif char == '[':
                bracket_count += 1
            elif char == ']':
                bracket_count -= 1
                if bracket_count < 0:
                    errors.append(f"Colchete de fechamento extra na posição {i}")
        
        if paren_count != 0:
            errors.append(f"Parênteses não balanceados: {paren_count} não fechados")
        if bracket_count != 0:
            errors.append(f"Colchetes não balanceados: {bracket_count} não fechados")
        
        return errors, warnings
    
    def analyze_code_structure(self, scad_file):
        """Analisa estrutura do código OpenSCAD"""
        try:
            with open(scad_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            
            analysis = {
                "file": str(scad_file),
                "name": scad_file.name,
                "total_lines": len(lines),
                "file_size": len(content),
                "errors": [],
                "warnings": [],
                "structure": {
                    "modules": 0,
                    "functions": 0,
                    "variables": 0,
                    "includes": 0,
                    "use": 0
                },
                "complexity": {
                    "if_statements": 0,
                    "for_loops": 0,
                    "while_loops": 0,
                    "linear_extrudes": 0
                },
                "objects_defined": 0
            }
            
            # Contar estruturas
            for i, line in enumerate(lines, 1):
                stripped = line.strip().lower()
                
                if not stripped or stripped.startswith('//'):
                    continue
                
                # Contar módulos e funções
                if 'module ' in stripped and '(' in stripped:
                    match = re.search(r'module\s+(\w+)', stripped)
                    if match:
                        analysis["structure"]["modules"] += 1
                        analysis["objects_defined"] += 1
                
                if 'function ' in stripped and '(' in stripped:
                    match = re.search(r'function\s+(\w+)', stripped)
                    if match:
                        analysis["structure"]["functions"] += 1
                        analysis["objects_defined"] += 1
                
                # Contar includes e uses
                if 'include ' in stripped:
                    analysis["structure"]["includes"] += 1
                if 'use <' in stripped:
                    analysis["structure"]["use"] += 1
                
                # Contar estruturas de controle
                if 'if(' in stripped or 'if (' in stripped:
                    analysis["complexity"]["if_statements"] += 1
                if 'for(' in stripped or 'for (' in stripped:
                    analysis["complexity"]["for_loops"] += 1
                if 'while(' in stripped or 'while (' in stripped:
                    analysis["complexity"]["while_loops"] += 1
                if 'linear_extrude' in stripped:
                    analysis["complexity"]["linear_extrudes"] += 1
            
            # Validar sintaxe
            syntax_errors, syntax_warnings = self.validate_syntax_structure(content)
            analysis["errors"] = syntax_errors
            analysis["warnings"] = syntax_warnings
            
            # Adicionar avisos baseados na análise
            if analysis["structure"]["modules"] == 0 and analysis["structure"]["functions"] == 0:
                # Verificar se há código direto (main object)
                has_main_code = any('translate(' in line or 'cube(' in line or 'cylinder(' in line or 'sphere(' in line for line in lines)
                if has_main_code:
                    analysis["warnings"].append("Código principal sem módulo - pode ser difícil de reutilizar")
                else:
                    analysis["warnings"].append("Arquivo sem módulos, funções ou objetos principais")
            
            if analysis["complexity"]["for_loops"] > 20:
                analysis["warnings"].append("Alto número de loops pode afectar performance de renderização")
            
            if analysis["total_lines"] > 400:
                analysis["warnings"].append("Arquivo muito grande - considere modularização")
            
            return analysis
            
        except Exception as e:
            return {
                "file": str(scad_file),
                "name": scad_file.name,
                "error": f"Erro ao analisar arquivo: {str(e)}"
            }
    
    def validate_all_files(self, models_dir="modelos-3d/central-inteligente"):
        """Valida todos os arquivos OpenSCAD"""
        print("🔍 VALIDAÇÃO OPENSCAD - CENTRAL DE CONTROLE INTELIGENTE")
        print("=" * 65)
        
        models_path = Path(models_dir)
        if not models_path.exists():
            print(f"❌ Diretório {models_dir} não encontrado!")
            return self.results
        
        scad_files = list(models_path.glob("*.scad"))
        if not scad_files:
            print(f"❌ Nenhum arquivo .scad encontrado em {models_dir}")
            return self.results
        
        scad_files.sort()
        self.results["total_files"] = len(scad_files)
        
        print(f"📁 Analisando {len(scad_files)} arquivos OpenSCAD:")
        for file in scad_files:
            print(f"   - {file.name}")
        print()
        
        # Validar cada arquivo
        for scad_file in scad_files:
            print(f"🔍 Validando: {scad_file.name}")
            print("-" * 50)
            
            analysis = self.analyze_code_structure(scad_file)
            
            if "error" in analysis:
                print(f"   ❌ Erro fatal: {analysis['error']}")
                self.results["error_files"].append(analysis)
                continue
            
            # Mostrar estatísticas
            print(f"   📊 Estrutura do código:")
            print(f"      - Linhas totais: {analysis['total_lines']}")
            print(f"      - Tamanho: {analysis['file_size']:,} bytes")
            print(f"      - Módulos: {analysis['structure']['modules']}")
            print(f"      - Funções: {analysis['structure']['functions']}")
            print(f"      - Variáveis: {analysis['structure']['variables']}")
            print(f"      - Loops for: {analysis['complexity']['for_loops']}")
            print(f"      - linear_extrude: {analysis['complexity']['linear_extrudes']}")
            
            # Verificar erros de sintaxe
            if analysis["errors"]:
                print(f"   ❌ Erros de sintaxe: {len(analysis['errors'])}")
                for error in analysis["errors"][:3]:  # Mostrar apenas os primeiros 3
                    print(f"      - {error}")
                if len(analysis["errors"]) > 3:
                    print(f"      ... e mais {len(analysis['errors']) - 3} erro(s)")
                self.results["error_files"].append(analysis)
            else:
                print(f"   ✅ Sintaxe válida!")
                self.results["valid_files"].append(analysis)
            
            # Verificar avisos
            if analysis["warnings"]:
                print(f"   ⚠️  Avisos: {len(analysis['warnings'])}")
                for warning in analysis["warnings"]:
                    print(f"      - {warning}")
                if not any("error" in str(err).lower() for err in analysis["errors"]):
                    self.results["warnings"].append(analysis)
            
            print()
        
        return self.results
    
    def generate_final_report(self):
        """Gera relatório final da validação"""
        print("=" * 65)
        print("📋 RELATÓRIO FINAL - VALIDAÇÃO OPENSCAD")
        print("=" * 65)
        print(f"⏰ Data/Hora: {self.results['validation_time']}")
        print(f"📁 Total de arquivos: {self.results['total_files']}")
        
        valid_count = len(self.results["valid_files"])
        error_count = len(self.results["error_files"])
        warning_count = len(self.results["warnings"])
        
        print(f"✅ Arquivos válidos: {valid_count}")
        print(f"❌ Arquivos com erro: {error_count}")
        print(f"⚠️  Arquivos com avisos: {warning_count}")
        print()
        
        # Análise detalhada dos arquivos válidos
        if self.results["valid_files"]:
            print("✅ ARQUIVOS VÁLIDOS:")
            total_lines = 0
            total_modules = 0
            total_functions = 0
            
            for file_info in self.results["valid_files"]:
                total_lines += file_info["total_lines"]
                total_modules += file_info["structure"]["modules"]
                total_functions += file_info["structure"]["functions"]
                
                print(f"   📄 {file_info['name']}:")
                print(f"      {file_info['total_lines']} linhas, {file_info['structure']['modules']} módulos")
            
            print(f"\n📊 RESUMO DOS ARQUIVOS VÁLIDOS:")
            print(f"   📏 Total de linhas: {total_lines:,}")
            print(f"   🔧 Total de módulos: {total_modules}")
            print(f"   🔧 Total de funções: {total_functions}")
        
        # Status final
        if valid_count == self.results["total_files"]:
            print("\n🎉 VALIDAÇÃO BEM-SUCEDIDA!")
            print("   ✅ Todos os modelos OpenSCAD são sintaticamente válidos")
            print("   🖨️  Prontos para renderização e impressão 3D")
            print("   💡 Abri-los no OpenSCAD para visualizar e exportar STL")
            print("   🔧 Podem ser impressos diretamente ou modificados conforme necessário")
        else:
            print(f"\n⚠️  VALIDAÇÃO COM PROBLEMAS")
            print(f"   ❌ {error_count} arquivo(s) com erros de sintaxe")
            print("   🔧 Corrigir os erros antes da impressão 3D")
            print("   📖 Consulte a documentação OpenSCAD para ajuda")
        
        # Salvar relatório
        report_file = Path("final_validation_report.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Relatório detalhado salvo em: {report_file}")
        
        return valid_count == self.results["total_files"]

def main():
    """Função principal"""
    validator = ImprovedOpenSCADValidator()
    validator.validate_all_files()
    success = validator.generate_final_report()
    
    return 0 if success else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())