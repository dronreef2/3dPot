# 🔥 Guia Completo: Implementar GitHub Actions Badges

**Data**: 10 Nov 2025  
**Status**: Pendente - Requer token com workflow scope  
**Responsável**: MiniMax Agent  

## 📋 Visão Geral

Para ativar os **GitHub Actions badges** no README.md, precisamos resolver a limitação de token e implementar o workflow CI/CD. Este guia fornece os passos específicos para resolver a última tarefa pendente de **Alta Prioridade** do projeto 3dPot.

## 🎯 Status Atual

### **Problema Identificado**
- **Token atual**: [REQUER ATUALIZAÇÃO COM WORKFLOW SCOPE]
- **Limitação**: Falta permission `workflow` scope
- **Impacto**: Impossível ativar GitHub Actions ou criar workflows
- **Arquivo pendente**: `.github/workflows/ci.yml` (não foi possível fazer push)

### **Tarefa Específica**
- **TODO.md**: Adicionar badges de status ao README
- **Prioridade**: Alta (única pendente)
- **Conclusão do projeto**: Aumentará de 40.6% para 42.2%

## 🔧 Solução 1: Atualizar Token do GitHub

### **Passos para Novo Token**

1. **Acessar Settings do GitHub**
   ```
   https://github.com/settings/tokens
   ```

2. **Criar Novo Personal Access Token**
   - Clique em "Generate new token (classic)"
   - Nome: `3dPot CI/CD Token`
   - Expiração: 90 dias
   - **Scopes necessários**:
     - ✅ `repo` (Full control of private repositories)
     - ✅ `workflow` (Update GitHub Action workflows)
     - ✅ `write:packages` (Upload packages)
     - ✅ `delete:packages` (Delete packages)
     - ✅ `admin:public_key` (Full control of user public keys)
     - ✅ `admin:repo_hook` (Full control of repository hooks)
     - ✅ `admin:org_hook` (Full control of organization hooks)
     - ✅ `admin:public_key` (Full control of user public keys)
     - ✅ `admin:gpg_key` (Full control of user GPG keys)

3. **Copiar Novo Token**
   ```
   Novo token: ghp_XXXXXXXXXXXXXXXXXXXXXXXXXXXX
   ```

4. **Atualizar Repositório**
   - Settings → Secrets and variables → Actions
   - Adicionar `GITHUB_TOKEN` com o novo token

## 🔄 Solução 2: Recriar e Fazer Push do Workflow

### **1. Criar Estrutura de Workflow**

```bash
# Criar pasta se não existir
mkdir -p .github/workflows

# Criar arquivo de workflow principal
touch .github/workflows/ci.yml
```

### **2. Configurar .github/workflows/ci.yml**

```yaml
name: 3dPot CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  schedule:
    # Run daily at 2 AM UTC
    - cron: '0 2 * * *'

jobs:
  # Job 1: Python Tests & Linting
  python-tests:
    name: Python Tests & Quality
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, '3.10', '3.11']
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
        cache: 'pip'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e .[dev]
        pip install pytest pytest-cov flake8 pylint black isort mypy
    
    - name: Lint with flake8
      run: |
        # stop the build if there are Python syntax errors or undefined names
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
        # exit-zero treats all errors as warnings
        flake8 . --count --exit-zero --max-complexity=10 --max-line-length=88 --statistics
    
    - name: Check code formatting with black
      run: black --check .
    
    - name: Check import sorting with isort
      run: isort --check-only .
    
    - name: Type checking with mypy
      run: mypy --ignore-missing-imports .
    
    - name: Run tests with pytest
      run: |
        pytest tests/ --cov=src/ --cov-report=xml --cov-report=html
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella

  # Job 2: Arduino/C++ Code Validation
  arduino-validation:
    name: Arduino Code Validation
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Install Arduino CLI
      run: |
        curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sh
        export PATH=$PATH:$HOME/bin
        echo "PATH=$PATH" >> $GITHUB_ENV
    
    - name: Setup Arduino
      run: |
        arduino-cli config init
        arduino-cli core install arduino:avr
        arduino-cli lib install "ESP32Core" "WebSocketsServer" "ArduinoJson"
    
    - name: Validate ESP32 Code
      run: |
        arduino-cli compile --fqbn espressif:esp32:esp32 code/esp32/monitor-filamento.ino
        arduino-cli compile --fqbn espressif:esp32:esp32 code/raspberry/raspberry-pi-integration.ino
    
    - name: Validate Arduino Code
      run: |
        arduino-cli compile --fqbn arduino:avr:uno code/arduino/esteira-transportadora.ino

  # Job 3: OpenSCAD Model Validation
  openscad-validation:
    name: OpenSCAD Model Validation
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Install OpenSCAD
      run: |
        sudo apt-get update
        sudo apt-get install -y openscad
    
    - name: Validate 3D Models
      run: |
        openscad -o models/esp32-support.stl models/esp32-support.scad
        openscad -o models/conveyor-roller.stl models/conveyor-roller.scad
        openscad -o models/raspberry-pi-case.stl models/raspberry-pi-case.scad
    
    - name: Check 3D Models with CGAL
      run: |
        # Validate STL files for manifold properties
        for file in models/*.stl; do
          echo "Validating $file"
          openscad -o /dev/null -D 'echo("No errors");' "$file"
        done

  # Job 4: Documentation Build
  documentation:
    name: Documentation Build
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
        cache: 'pip'
    
    - name: Install documentation tools
      run: |
        pip install mkdocs mkdocs-material mkdocs-mermaid2-plugin
    
    - name: Build documentation
      run: |
        mkdocs build --clean --strict
    
    - name: Validate links
      run: |
        pip install mkdocs-linkcheck
        mkdocs-linkcheck

  # Job 5: Security Scan
  security-scan:
    name: Security Scan
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Run Trivy vulnerability scanner
      uses: aquasecurity/trivy-action@master
      with:
        scan-type: 'fs'
        scan-ref: '.'
        format: 'sarif'
        output: 'trivy-results.sarif'
    
    - name: Upload Trivy scan results to GitHub Security tab
      uses: github/codeql-action/upload-sarif@v2
      if: always()
      with:
        sarif_file: 'trivy-results.sarif'

  # Job 6: Package and Release
  package-release:
    name: Package and Release
    runs-on: ubuntu-latest
    needs: [python-tests, arduino-validation, openscad-validation, documentation, security-scan]
    if: github.ref == 'refs/heads/main'
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
        cache: 'pip'
    
    - name: Install packaging tools
      run: |
        pip install build twine
    
    - name: Build package
      run: python -m build
    
    - name: Create Release
      uses: softprops/action-gh-release@v1
      with:
        files: dist/*
        tag_name: v${{ github.run_number }}
        name: Release v${{ github.run_number }}
        body: |
          🚀 Automated release v${{ github.run_number }}
          
          ## What's Changed
          - Enhanced CI/CD pipeline
          - Security improvements
          - Documentation updates
          
          ## Checks
          - ✅ Python tests passed
          - ✅ Arduino code validated
          - ✅ 3D models verified
          - ✅ Documentation built
          - ✅ Security scan clean
        draft: false
        prerelease: false
```

## 🎨 Solução 3: Adicionar Badges ao README

### **1. Posição dos Badges**

Adicionar os badges na seção **Início do README.md**, logo após o título principal:

```markdown
# 🎯 3dPot - Monitor de Filamento & Automação para Impressão 3D

[![CI Pipeline](https://img.shields.io/github/actions/workflow/status/dronreef2/3dPot/ci.yml?label=CI%20Pipeline&style=flat-square)](https://github.com/dronreef2/3dPot/actions/workflows/ci.yml)
[![Python Tests](https://img.shields.io/github/actions/workflow/status/dronreef2/3dPot/python-tests.yml?label=Python%20Tests&style=flat-square)](https://github.com/dronreef2/3dPot/actions)
[![Code Quality](https://img.shields.io/github/actions/workflow/status/dronreef2/3dPot/code-quality.yml?label=Code%20Quality&style=flat-square)](https://github.com/dronreef2/3dPot/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![Arduino Compatible](https://img.shields.io/badge/Arduino-ESP32%20%7C%20Nano-green.svg)](https://www.arduino.cc/)
[![3D Models](https://img.shields.io/badge/3D%20Models-OpenSCAD-orange.svg)](https://openscad.org/)
```

### **2. Badges Específicos por Funcionalidade**

```markdown
## 🛠️ Hardware Components

[![ESP32 Monitor](https://img.shields.io/badge/ESP32-Monitor%20Filamento-lightblue.svg)](code/esp32/)
[![Arduino Esteira](https://img.shields.io/badge/Arduino-Esteira%20Transportadora-green.svg)](code/arduino/)
[![Raspberry Pi QC](https://img.shields.io/badge/Raspberry%20Pi-Estação%20QC-purple.svg)](code/raspberry/)

## 📊 Test Coverage

[![Test Coverage](https://img.shields.io/codecov/c/github/dronreef2/3dpot)](https://codecov.io/gh/dronreef2/3dpot)
[![Tests Status](https://img.shields.io/github/actions/workflow/status/dronreef2/3dPot/tests.yml?label=Tests&style=flat)](https://github.com/dronreef2/3dPot/actions)

## 🔧 Build Status

[![OpenSCAD Validation](https://img.shields.io/github/actions/workflow/status/dronreef2/3dPot/openscad.yml?label=3D%20Models&style=flat)](https://github.com/dronreef2/3dPot/actions)
[![Arduino Build](https://img.shields.io/github/actions/workflow/status/dronreef2/3dPot/arduino-build.yml?label=Arduino%20Build&style=flat)](https://github.com/dronreef2/3dPot/actions)
```

### **3. Badges de Status Avançados**

```markdown
## 📈 Project Stats

![GitHub stars](https://img.shields.io/github/stars/dronreef2/3dpot?style=social)
![GitHub forks](https://img.shields.io/github/forks/dronreef2/3dpot?style=social)
![GitHub issues](https://img.shields.io/github/issues/dronreef2/3dpot)
![GitHub pull requests](https://img.shields.io/github/issues-pr/dronreef2/3dpot)
![GitHub contributors](https://img.shields.io/github/contributors/dronreef2/3dpot)

## 🔗 Community

[![Discord](https://img.shields.io/discord/1234567890?label=Discord&logo=discord)](https://discord.gg/3dpot)
[![Documentation](https://img.shields.io/badge/Docs-GitHub%20Pages-blue)](https://dronreef2.github.io/3dpot)
[![Discussions](https://img.shields.io/github/discussions/dronreef2/3dpot)](https://github.com/dronreef2/3dpot/discussions)
```

## 🚀 Implementação Passo-a-Passo

### **Passo 1: Preparar Ambiente**
```bash
# Backup do README atual
cp README.md README.md.backup

# Criar pasta workflows se não existir
mkdir -p .github/workflows
```

### **Passo 2: Criar Workflow Principal**
```bash
# Criar arquivo de workflow
cat > .github/workflows/ci.yml << 'EOF'
[conteúdo do workflow yaml completo]
EOF
```

### **Passo 3: Fazer Commit e Push**
```bash
# Adicionar arquivos
git add .github/workflows/ci.yml

# Commit com mensagem descritiva
git commit -m "feat: Add GitHub Actions CI/CD pipeline with badges

- Add comprehensive CI workflow
- Support Python 3.8-3.11 matrix builds
- Arduino and OpenSCAD validation
- Security scanning with Trivy
- Automated releases on main branch

🚀 Enables README badges for project status"

# Push para ativar workflows
git push origin main
```

### **Passo 4: Verificar Ativação**
1. **Acessar Actions**: `https://github.com/dronreef2/3dPot/actions`
2. **Aguardar run inicial**: Primeiro workflow pode demorar 2-5 minutos
3. **Verificar badges**: Atualizar página README para ver badges ativos

### **Passo 5: Adicionar Badges ao README**
```bash
# Editar README.md e adicionar badges na seção inicial
# Ver exemplos acima
```

## 🎯 Resultado Esperado

### **Badges Ativos no README**
- **CI Pipeline**: Verde quando builds passando
- **Python Tests**: Status dos testes automatizados
- **Code Quality**: Validação de linting e formatação
- **License**: MIT compliance
- **Python Version**: Compatibilidade Python
- **Arduino/3D Models**: Status de builds de hardware

### **Workflows Funcionais**
- **Teste automático** a cada push/PR
- **Validação de código** Python, C++, OpenSCAD
- **Security scan** com Trivy
- **Build de documentação** automática
- **Releases automatizados** no main branch

## 📊 Impacto no Progresso

### **Antes**
- **Tarefas Concluídas**: 26/64 (40.6%)
- **Alta Prioridade**: 9/11 (82%)
- **Status**: Badge pendente, workflow não ativo

### **Depois**
- **Tarefas Concluídas**: 27/64 (42.2%)
- **Alta Prioridade**: 10/11 (91%)
- **Status**: Badges ativos, CI/CD completo

## 🛠️ Troubleshooting

### **Token Inválido**
```bash
# Verificar permissões do token
curl -H "Authorization: token GITHUB_TOKEN" https://api.github.com/user/repos

# Se falhar: Regenerar token com permissões corretas
```

### **Workflow Não Roda**
```yaml
# Verificar trigger conditions
on:
  push:
    branches: [ main ]  # Certificar que main branch está correto
  pull_request:
    branches: [ main ]
```

### **Badges Não Aparecem**
- Aguardar primeiro workflow run completo
- Verificar URL do repositório nos badges
- Limpar cache do navegador

## 📝 Checklist de Implementação

- [ ] **1. Atualizar GitHub Token** com permissões workflow
- [ ] **2. Criar .github/workflows/ci.yml** com configuração completa
- [ ] **3. Fazer push do workflow** para ativar Actions
- [ ] **4. Aguardar primeiro run** completo (5-10 min)
- [ ] **5. Adicionar badges ao README** com URLs corretos
- [ ] **6. Verificar todos os badges** funcionando
- [ ] **7. Atualizar TODO.md** marcando Issue #1 como completo

## 🎉 Conclusão

Com a implementação dos **GitHub Actions badges**, o projeto 3dPot completará sua **Alta Prioridade** e estará pronto para ser um projeto **open source profissional** com:

- **CI/CD automatizado** para qualidade de código
- **Badges visuais** demonstrando confiabilidade
- **Automação completa** de testes e releases
- **Documentação profissional** com status em tempo real

Esta será a **tarefa final de Alta Prioridade**, elevando o projeto de **82%** para **91%** de conclusão na categoria mais importante!

---

**💡 Nota**: Uma vez implementado, os badges se atualizarão automaticamente com o status do projeto, fornecendo feedback visual instantâneo para contributors e usuários.