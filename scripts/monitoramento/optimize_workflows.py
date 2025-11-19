#!/usr/bin/env python3
"""
3dPot Workflow Optimizer
Script para implementar automaticamente as otimizações de performance
nos workflows do GitHub Actions.
"""

import os
import re
import shutil
from datetime import datetime
from typing import Dict, List, Tuple


class WorkflowOptimizer:
    """Otimizador automático de workflows GitHub Actions"""
    
    def __init__(self, workflows_dir: str = ".github/workflows"):
        self.workflows_dir = workflows_dir
        self.backup_dir = f"workflows_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.optimizations_applied = []
        
    def create_backup(self):
        """Cria backup dos workflows originais"""
        if os.path.exists(self.backup_dir):
            shutil.rmtree(self.backup_dir)
        
        shutil.copytree(self.workflows_dir, self.backup_dir)
        print(f"✅ Backup criado em: {self.backup_dir}")
    
    def optimize_arduino_build(self) -> bool:
        """Otimiza o workflow arduino-build.yml"""
        file_path = os.path.join(self.workflows_dir, "arduino-build.yml")
        
        if not os.path.exists(file_path):
            print(f"❌ Arquivo não encontrado: {file_path}")
            return False
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Otimizações a serem aplicadas
        optimizations = [
            # 1. Adicionar cache para Arduino CLI
            {
                "description": "Adicionar cache para Arduino CLI",
                "pattern": r"(steps:.*?name: Setup Arduino CLI.*?uses: arduino/setup-arduino-cli.*?\n)",
                "replacement": r"\1\n      - name: Cache Arduino CLI and platforms\n        uses: actions/cache@v3\n        with:\n          path: |\n            ~/.arduino-cli\n            ~/.arduino15\n          key: arduino-${{ runner.os }}-${{ hashFiles('codigos/**/*.ino') }}\n          restore-keys: |\n            arduino-${{ runner.os }}-"
            },
            # 2. Atualizar upload-artifact para v4
            {
                "description": "Atualizar upload-artifact para v4",
                "pattern": r"uses: actions/upload-artifact@v3",
                "replacement": "uses: actions/upload-artifact@v4"
            },
            # 3. Adicionar timeout otimizado
            {
                "description": "Adicionar timeout otimizado",
                "pattern": r"jobs:\n  build-arduino:\n    name: Build Arduino/ESP32 Sketches\n    runs-on: ubuntu-latest",
                "replacement": "jobs:\n  build-arduino:\n    name: Build Arduino/ESP32 Sketches\n    runs-on: ubuntu-latest\n    timeout-minutes: 15"
            }
        ]
        
        for opt in optimizations:
            if opt["description"] in content:
                print(f"⚠️  {opt['description']} já aplicado")
                continue
                
            content = re.sub(opt["pattern"], opt["replacement"], content, flags=re.DOTALL)
            self.optimizations_applied.append(opt["description"])
        
        # Salvar arquivo otimizado
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Arduino Build otimizado")
        return True
    
    def optimize_code_quality(self) -> bool:
        """Otimiza o workflow code-quality.yml"""
        file_path = os.path.join(self.workflows_dir, "code-quality.yml")
        
        if not os.path.exists(file_path):
            print(f"❌ Arquivo não encontrado: {file_path}")
            return False
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        optimizations = [
            # 1. Adicionar cache para pip
            {
                "description": "Adicionar cache para pip",
                "pattern": r"(name: Set up Python.*?python-version: '3.9'.*?\n)",
                "replacement": r"\1      - name: Cache pip dependencies\n        uses: actions/cache@v3\n        with:\n          path: ~/.cache/pip\n          key: pip-${{ runner.os }}-${{ hashFiles('**/requirements*.txt') }}\n          restore-keys: |\n            pip-${{ runner.os }}-"
            },
            # 2. Atualizar upload-artifact para v4
            {
                "description": "Atualizar upload-artifact para v4",
                "pattern": r"uses: actions/upload-artifact@v3",
                "replacement": "uses: actions/upload-artifact@v4"
            },
            # 3. Adicionar timeout
            {
                "description": "Adicionar timeout otimizado",
                "pattern": r"jobs:\n  quality:\n    name: Code Quality Analysis\n    runs-on: ubuntu-latest",
                "replacement": "jobs:\n  quality:\n    name: Code Quality Analysis\n    runs-on: ubuntu-latest\n    timeout-minutes: 10"
            }
        ]
        
        for opt in optimizations:
            if opt["description"] in content:
                print(f"⚠️  {opt['description']} já aplicado")
                continue
                
            content = re.sub(opt["pattern"], opt["replacement"], content, flags=re.DOTALL)
            self.optimizations_applied.append(opt["description"])
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Code Quality otimizado")
        return True
    
    def optimize_python_tests(self) -> bool:
        """Otimiza o workflow python-tests.yml"""
        file_path = os.path.join(self.workflows_dir, "python-tests.yml")
        
        if not os.path.exists(file_path):
            print(f"❌ Arquivo não encontrado: {file_path}")
            return False
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        optimizations = [
            # 1. Adicionar cache para pip (já tem cache, mas otimizar)
            {
                "description": "Otimizar cache pip existente",
                "pattern": r"cache: 'pip'",
                "replacement": "cache: 'pip'\n      - name: Cache additional dependencies\n        uses: actions/cache@v3\n        with:\n          path: ~/.cache/pip\n          key: pip-python${{ matrix.python-version }}-${{ runner.os }}-${{ hashFiles('**/requirements*.txt') }}"
            },
            # 2. Adicionar timeout
            {
                "description": "Adicionar timeout otimizado",
                "pattern": r"test:\n    name: Test Python \${{ matrix.python-version }}\n    runs-on: ubuntu-latest",
                "replacement": "test:\n    name: Test Python ${{ matrix.python-version }}\n    runs-on: ubuntu-latest\n    timeout-minutes: 10"
            }
        ]
        
        for opt in optimizations:
            if opt["description"] in content:
                print(f"⚠️  {opt['description']} já aplicado")
                continue
                
            content = re.sub(opt["pattern"], opt["replacement"], content, flags=re.DOTALL)
            self.optimizations_applied.append(opt["description"])
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Python Tests otimizado")
        return True
    
    def optimize_ci_pipeline(self) -> bool:
        """Otimiza o workflow ci.yml"""
        file_path = os.path.join(self.workflows_dir, "ci.yml")
        
        if not os.path.exists(file_path):
            print(f"❌ Arquivo não encontrado: {file_path}")
            return False
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        optimizations = [
            # 1. Adicionar paths para triggers inteligentes
            {
                "description": "Adicionar paths para triggers inteligentes",
                "pattern": r"on:\n  push:\n    branches: \[ main, develop \]",
                "replacement": "on:\n  push:\n    branches: [ main, develop ]\n    paths:\n      - 'codigos/**'\n      - 'tests/**'\n      - 'modelos-3d/**'"
            },
            {
                "description": "Adicionar paths para PR",
                "pattern": r"  pull_request:\n    branches: \[ main, develop \]",
                "replacement": "  pull_request:\n    branches: [ main, develop ]\n    paths:\n      - 'codigos/**'\n      - 'tests/**'\n      - 'modelos-3d/**'"
            },
            # 2. Adicionar cache para pip
            {
                "description": "Adicionar cache global",
                "pattern": r"(name: Set up Python.*?python-version: \${{ inputs\\.python_version \\|\\| '3\\.9' }}.*?cache: 'pip'.*?\n)",
                "replacement": r"\1      - name: Cache global pip dependencies\n        uses: actions/cache@v3\n        with:\n          path: ~/.cache/pip\n          key: global-pip-${{ runner.os }}-${{ hashFiles('**/requirements*.txt') }}"
            },
            # 3. Adicionar timeout aos jobs principais
            {
                "description": "Adicionar timeout ao job lint-and-format",
                "pattern": r"lint-and-format:\n    name: Code Quality Check\n    runs-on: ubuntu-latest",
                "replacement": "lint-and-format:\n    name: Code Quality Check\n    runs-on: ubuntu-latest\n    timeout-minutes: 8"
            },
            {
                "description": "Adicionar timeout ao job python-tests",
                "pattern": r"python-tests:\n    name: Python Tests\n    runs-on: ubuntu-latest",
                "replacement": "python-tests:\n    name: Python Tests\n    runs-on: ubuntu-latest\n    timeout-minutes: 10"
            }
        ]
        
        for opt in optimizations:
            if opt["description"] in content:
                print(f"⚠️  {opt['description']} já aplicado")
                continue
                
            content = re.sub(opt["pattern"], opt["replacement"], content, flags=re.DOTALL)
            self.optimizations_applied.append(opt["description"])
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ CI Pipeline otimizado")
        return True
    
    def optimize_openscad(self) -> bool:
        """Otimiza o workflow openscad.yml"""
        file_path = os.path.join(self.workflows_dir, "openscad.yml")
        
        if not os.path.exists(file_path):
            print(f"❌ Arquivo não encontrado: {file_path}")
            return False
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        optimizations = [
            # 1. Atualizar upload-artifact para v4
            {
                "description": "Atualizar upload-artifact para v4",
                "pattern": r"uses: actions/upload-artifact@v3",
                "replacement": "uses: actions/upload-artifact@v4"
            },
            # 2. Adicionar timeout
            {
                "description": "Adicionar timeout otimizado",
                "pattern": r"validate-openscad:\n    name: Validate OpenSCAD 3D Models\n    runs-on: ubuntu-latest",
                "replacement": "validate-openscad:\n    name: Validate OpenSCAD 3D Models\n    runs-on: ubuntu-latest\n    timeout-minutes: 8"
            }
        ]
        
        for opt in optimizations:
            if opt["description"] in content:
                print(f"⚠️  {opt['description']} já aplicado")
                continue
                
            content = re.sub(opt["pattern"], opt["replacement"], content, flags=re.DOTALL)
            self.optimizations_applied.append(opt["description"])
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ OpenSCAD otimizado")
        return True
    
    def generate_optimization_report(self) -> str:
        """Gera relatório das otimizações aplicadas"""
        report = f"""# 🚀 3dPot - Relatório de Otimização de Workflows

## Resumo
- **Data**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Backup**: {self.backup_dir}
- **Otimizações Aplicadas**: {len(self.optimizations_applied)}

## Otimizações Implementadas

"""
        
        for i, opt in enumerate(self.optimizations_applied, 1):
            report += f"{i}. ✅ {opt}\n"
        
        report += f"""
## Próximos Passos
1. Testar os workflows otimizados
2. Monitorar performance após as mudanças
3. Validar melhoria na taxa de sucesso
4. Medir redução de custos

## Como Reverter
Para reverter as mudanças, execute:
```bash
rm -rf .github/workflows
cp -r {self.backup_dir} .github/workflows
```

---
*Otimização automática realizada pelo 3dPot Workflow Optimizer*
"""
        
        return report
    
    def run_optimization(self) -> bool:
        """Executa todas as otimizações"""
        print("🔧 Iniciando otimização automática dos workflows...")
        
        if not os.path.exists(self.workflows_dir):
            print(f"❌ Diretório de workflows não encontrado: {self.workflows_dir}")
            return False
        
        # Criar backup
        self.create_backup()
        
        # Otimizar cada workflow
        workflows = [
            ("arduino-build.yml", self.optimize_arduino_build),
            ("code-quality.yml", self.optimize_code_quality),
            ("python-tests.yml", self.optimize_python_tests),
            ("ci.yml", self.optimize_ci_pipeline),
            ("openscad.yml", self.optimize_openscad)
        ]
        
        success_count = 0
        for workflow_file, optimizer_func in workflows:
            print(f"\n🔍 Otimizando {workflow_file}...")
            if optimizer_func():
                success_count += 1
        
        # Gerar relatório
        report = self.generate_optimization_report()
        with open("OPTIMIZATION_REPORT.md", 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n✅ Otimização concluída!")
        print(f"📊 {success_count}/{len(workflows)} workflows otimizados")
        print(f"📋 Relatório salvo em: OPTIMIZATION_REPORT.md")
        print(f"💾 Backup salvo em: {self.backup_dir}")
        
        return success_count > 0


def main():
    """Função principal"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("3dPot Workflow Optimizer")
        print("Uso: python optimize_workflows.py")
        print("Otimiza automaticamente os workflows para melhor performance.")
        return
    
    optimizer = WorkflowOptimizer()
    optimizer.run_optimization()


if __name__ == "__main__":
    main()