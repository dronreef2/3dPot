#!/usr/bin/env python3
"""
Validador Sintático Estático OpenSCAD
Analisa sintaxe sem executar o OpenSCAD (modo headless)
"""

import re
from pathlib import Path
import json
from datetime import datetime

class OpenSCADSintaticValidator:
    def __init__(self):
        self.results = {
            "validation_time": datetime.now().isoformat(),
            "validator": "OpenSCAD Sintatic Validator v1.0",
            "total_files": 0,
            "valid_files": [],
            "syntax_errors": [],
            "warnings": []
        }
    
    def analyze_file_syntax(self, scad_file):
        """Analisa sintaxe de um arquivo OpenSCAD"""
        try:
            with open(scad_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            
            analysis = {
                "file": str(scad_file),
                "total_lines": len(lines),
                "file_size": len(content),
                "syntax_errors": [],
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
                    "while_loops": 0
                }
            }
            
            # Análise linha por linha
            brace_count = 0
            for i, line in enumerate(lines, 1):
                stripped = line.strip()
                line_num = i
                
                if not stripped or stripped.startswith('//'):
                    continue
                
                # Verificar balancement de chaves
                open_braces = stripped.count('{')
                close_braces = stripped.count('}')
                brace_count += open_braces - close_braces
                
                # Detectar estruturas
                if 'module ' in stripped and '(' in stripped:
                    module_name = re.search(r'module\s+(\w+)', stripped)
                    if module_name:
                        analysis["structure"]["modules"] += 1
                
                if 'function ' in stripped and '(' in stripped:
                    func_name = re.search(r'function\s+(\w+)', stripped)
                    if func_name:
                        analysis["structure"]["functions"] += 1
                
                if '=' in stripped and not stripped.startswith('//'):
                    # Identificar variáveis (não dentro de estruturas)
                    if not any(x in stripped for x in ['module', 'function', 'if', 'for', 'while']):
                        analysis["structure"]["variables"] += 1
                
                if 'include ' in stripped:
                    analysis["structure"]["includes"] += 1
                
                if 'use <' in stripped:
                    analysis["structure"]["use"] += 1
                
                # Verificações de complexidade
                if 'if(' in stripped or 'if (' in stripped:
                    analysis["complexity"]["if_statements"] += 1
                
                if 'for(' in stripped or 'for (' in stripped:
                    analysis["complexity"]["for_loops"] += 1
                
                if 'while(' in stripped or 'while (' in stripped:
                    analysis["complexity"]["while_loops"] += 1
                
                # Verificações sintáticas comuns
                if stripped.count('(') != stripped.count(')'):
                    analysis["syntax_errors"].append({
                        "line": line_num,
                        "type": "MISMATCHED_PARENTHESES",
                        "message": f"Parênteses não balanceados na linha {line_num}: {stripped[:50]}..."
                    })
                
                if stripped.count('[') != stripped.count(']'):
                    analysis["syntax_errors"].append({
                        "line": line_num,
                        "type": "MISMATCHED_BRACKETS",
                        "message": f"Colchetes não balanceados na linha {line_num}: {stripped[:50]}..."
                    })
            
            # Verificar se as chaves estão balanceadas no final
            if brace_count != 0:
                analysis["syntax_errors"].append({
                    "line": "end",
                    "type": "MISMATCHED_BRACES",
                    "message": f"Chaves não balanceadas. Excesso de {brace_count} chaves"
                })
            
            # Adicionar avisos para padrões potencialmente problemáticos
            if content.count('//') > content.count('\n') * 0.3:
                analysis["warnings"].append({
                    "type": "HIGH_COMMENT_RATIO",
                    "message": "Alta proporção de comentários pode indicar código mal estruturado"
                })
            
            if analysis["structure"]["modules"] == 0 and analysis["structure"]["functions"] == 0:
                analysis["warnings"].append({
                    "type": "NO_MODULES",
                    "message": "Arquivo não contém módulos ou funções definidos"
                })
            
            return analysis
            
        except Exception as e:
            return {
                "file": str(scad_file),
                "error": f"Erro ao analisar arquivo: {str(e)}"
            }
    
    def validate_all_files(self, models_dir="modelos-3d/central-inteligente"):
        """Valida todos os arquivos OpenSCAD no diretório"""
        print("🔍 VALIDAÇÃO SINTÁTICA ESTÁTICA - OpenSCAD")
        print("=" * 60)
        
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
        
        print(f"📁 Encontrados {len(scad_files)} arquivos OpenSCAD:")
        for file in scad_files:
            print(f"   - {file.name}")
        print()
        
        # Validar cada arquivo
        for scad_file in scad_files:
            print(f"🔍 Analisando: {scad_file.name}")
            print("-" * 40)
            
            analysis = self.analyze_file_syntax(scad_file)
            
            if "error" in analysis:
                print(f"   ❌ Erro: {analysis['error']}")
                self.results["syntax_errors"].append(analysis)
                continue
            
            # Mostrar estatísticas do arquivo
            print(f"   📊 Estatísticas:")
            print(f"      - Linhas: {analysis['total_lines']}")
            print(f"      - Tamanho: {analysis['file_size']:,} bytes")
            print(f"      - Módulos: {analysis['structure']['modules']}")
            print(f"      - Funções: {analysis['structure']['functions']}")
            print(f"      - Variáveis: {analysis['structure']['variables']}")
            print(f"      - Loops for: {analysis['complexity']['for_loops']}")
            print(f"      - Estruturas if: {analysis['complexity']['if_statements']}")
            
            # Verificar erros
            if analysis["syntax_errors"]:
                print(f"   ❌ Erros sintáticos encontrados: {len(analysis['syntax_errors'])}")
                for error in analysis["syntax_errors"]:
                    print(f"      - {error['type']}: {error['message']}")
                self.results["syntax_errors"].append(analysis)
            else:
                print(f"   ✅ Sintaxe válida!")
                self.results["valid_files"].append(analysis)
            
            # Verificar avisos
            if analysis["warnings"]:
                print(f"   ⚠️  Avisos: {len(analysis['warnings'])}")
                for warning in analysis["warnings"]:
                    print(f"      - {warning['type']}: {warning['message']}")
                self.results["warnings"].append(analysis)
            
            print()
        
        return self.results
    
    def generate_summary_report(self):
        """Gera relatório resumido da validação"""
        print("=" * 60)
        print("📋 RELATÓRIO DE VALIDAÇÃO SINTÁTICA - CENTRAL DE CONTROLE")
        print("=" * 60)
        print(f"⏰ Data/Hora: {self.results['validation_time']}")
        print(f"📁 Total de arquivos: {self.results['total_files']}")
        
        valid_count = len(self.results["valid_files"])
        error_count = len(self.results["syntax_errors"])
        warning_count = len(self.results["warnings"])
        
        print(f"✅ Arquivos válidos: {valid_count}")
        print(f"❌ Arquivos com erro: {error_count}")
        print(f"⚠️  Arquivos com avisos: {warning_count}")
        print()
        
        if valid_count == self.results["total_files"]:
            print("🎉 TODOS OS ARQUIVOS SÃO SINTATICAMENTE VÁLIDOS!")
            print("💡 Os modelos OpenSCAD estão prontos para renderização")
            print("🖨️  Podem ser abertos e impressos no OpenSCAD")
            
            if warning_count > 0:
                print(f"\n💡 Nota: {warning_count} arquivo(s) possui(em) avisos não-críticos")
        else:
            print(f"⚠️  {error_count} arquivo(s) precisa(m) de correção sintática")
            print("🔧 Revise os erros listados acima")
        
        # Salvar relatório
        report_file = Path("syntax_validation_report.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Relatório detalhado salvo em: {report_file}")
        
        return valid_count == self.results["total_files"]

def main():
    """Função principal"""
    validator = OpenSCADSintaticValidator()
    validator.validate_all_files()
    success = validator.generate_summary_report()
    
    return 0 if success else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())