# 🔄 GitHub Actions Workflows - 3dPot

Este diretório contém os workflows de **CI/CD (Continuous Integration/Continuous Deployment)** para o projeto 3dPot. Os workflows automatizam a validação, teste e qualidade do código.

## 🗂️ Workflows Disponíveis

### **1. CI/CD Principal** (`ci.yml`)
- **Trigger**: Push, Pull Request, Schedule (diário às 2h UTC)
- **Purpose**: Pipeline completo de validação
- **Jobs**:
  - ✅ Python Tests (3.8-3.11 matrix)
  - ✅ Arduino Code Validation
  - ✅ OpenSCAD 3D Model Validation
  - ✅ Documentation Build
  - ✅ Security Scan (Trivy + Semgrep)
  - ✅ Package & Release (main branch only)

### **2. Python Tests** (`python-tests.yml`)
- **Trigger**: Push, Pull Request, Schedule (diário às 1h UTC)
- **Purpose**: Testes unitários Python com coverage
- **Badge URL**: `https://img.shields.io/github/actions/workflow/status/dronreef2/3dPot/python-tests.yml?label=Python%20Tests`

### **3. Code Quality** (`code-quality.yml`)
- **Trigger**: Push, Pull Request
- **Purpose**: Validação de formatação e qualidade
- **Tools**: Black, isort, flake8, MyPy, Bandit, Safety
- **Badge URL**: `https://img.shields.io/github/actions/workflow/status/dronreef2/3dPot/code-quality.yml?label=Code%20Quality`

### **4. OpenSCAD Validation** (`openscad.yml`)
- **Trigger**: Push, Pull Request, Schedule (domingo às 3h UTC)
- **Purpose**: Validação dos modelos 3D OpenSCAD
- **Badge URL**: `https://img.shields.io/github/actions/workflow/status/dronreef2/3dPot/openscad.yml?label=3D%20Models`

### **5. Arduino Build** (`arduino-build.yml`)
- **Trigger**: Push, Pull Request, Schedule (a cada 6h)
- **Purpose**: Compilação dos códigos Arduino/ESP32
- **Badge URL**: `https://img.shields.io/github/actions/workflow/status/dronreef2/3dPot/arduino-build.yml?label=Arduino%20Build`

## 🎯 Badges para README.md

### **Badges Principais**
```markdown
[![CI Pipeline](https://img.shields.io/github/actions/workflow/status/dronreef2/3dPot/ci.yml?label=CI%20Pipeline&style=flat-square)](https://github.com/dronreef2/3dPot/actions/workflows/ci.yml)
[![Python Tests](https://img.shields.io/github/actions/workflow/status/dronreef2/3dPot/python-tests.yml?label=Python%20Tests&style=flat-square)](https://github.com/dronreef2/3dPot/actions)
[![Code Quality](https://img.shields.io/github/actions/workflow/status/dronreef2/3dPot/code-quality.yml?label=Code%20Quality&style=flat-square)](https://github.com/dronreef2/3dPot/actions)
```

### **Badges Técnicos**
```markdown
[![3D Models](https://img.shields.io/github/actions/workflow/status/dronreef2/3dPot/openscad.yml?label=3D%20Models&style=flat)](https://github.com/dronreef2/3dPot/actions)
[![Arduino Build](https://img.shields.io/github/actions/workflow/status/dronreef2/3dPot/arduino-build.yml?label=Arduino%20Build&style=flat)](https://github.com/dronreef2/3dPot/actions)
```

## 🚀 Ativação dos Workflows

### **Pré-requisitos**
1. **GitHub Token com permissões `workflow`**
2. **Branch `main` ou `develop`**
3. **Arquivos na pasta `.github/workflows/`**

### **Passos de Ativação**
```bash
# 1. Fazer commit dos workflows
git add .github/workflows/
git commit -m "feat: Add GitHub Actions workflows

- ci.yml: Main CI/CD pipeline
- python-tests.yml: Python testing
- code-quality.yml: Code quality checks  
- openscad.yml: 3D model validation
- arduino-build.yml: Arduino code compilation

🚀 Enables automated testing and validation"

# 2. Push para ativar workflows
git push origin main

# 3. Verificar no GitHub Actions
# https://github.com/dronreef2/3dPot/actions
```

## 📊 Status dos Jobs

### **Status Possible**
- 🟢 **success** (passou)
- 🔴 **failure** (falhou)
- 🟡 **cancelled** (cancelado)
- ⚪ **skipped** (pulado)

### **Durations Esperadas**
- **Python Tests**: 3-5 minutos
- **Code Quality**: 1-2 minutos
- **OpenSCAD Validation**: 2-3 minutos
- **Arduino Build**: 5-8 minutos
- **CI/CD Completo**: 10-15 minutos

## 🔧 Personalização

### **Modificar Triggers**
```yaml
on:
  push:
    branches: [ main, develop ]  # Adicionar/remover branches
  pull_request:
    branches: [ main ]          # Branches para PR
  schedule:
    - cron: '0 2 * * *'         # Cron schedule
```

### **Adicionar Steps**
```yaml
steps:
  - name: Checkout code
    uses: actions/checkout@v4
  
  - name: Custom script
    run: |
      # Seu script personalizado
      echo "Custom step"
```

### **Modificar Python Version Matrix**
```yaml
strategy:
  matrix:
    python-version: [3.8, 3.9, '3.10', '3.11', '3.12']  # Adicionar versões
```

## 📈 Monitoring e Debugging

### **Acessar Logs**
1. **GitHub Actions**: https://github.com/dronreef2/3dPot/actions
2. **Workflow Runs**: Clicar no run específico
3. **Job Details**: Expandir job para ver logs
4. **Step Logs**: Clicar em steps individuais

### **Common Issues**

#### **Token Insuficiente**
```
Error: Resource not accessible by integration
```
**Solução**: Atualizar token com permissão `workflow`

#### **Dependencies Missing**
```
Error: Package not found
```
**Solução**: Verificar `requirements.txt` ou `pyproject.toml`

#### **Compilation Errors**
```
Error: Compilation failed
```
**Solução**: Verificar sintaxe Arduino/OpenSCAD

### **Debugging Commands**
```bash
# Testar localmente
python -m pytest tests/
black --check .
flake8 .
mypy src/

# Testar OpenSCAD
openscad -o output.stl model.scad

# Testar Arduino
arduino-cli compile --fqbn arduino:avr:uno code.ino
```

## 🔒 Security

### **Secrets Used**
- `GITHUB_TOKEN`: Automatic token for API access
- `CODECOV_TOKEN`: For coverage reporting
- `SEMGREP_APP_TOKEN`: For security scanning

### **Security Best Practices**
- ✅ **No secrets in code**: Usar GitHub Secrets
- ✅ **Minimal permissions**: Apenas permissões necessárias
- ✅ **Dependency scanning**: Trivy + Semgrep
- ✅ **Code analysis**: Bandit + Safety

## 📋 Checklist de Implementação

- [ ] **1. Atualizar GitHub Token** com permissões workflow
- [ ] **2. Verificar workflows** em `.github/workflows/`
- [ ] **3. Fazer commit e push** dos workflows
- [ ] **4. Verificar primeira execução** (pode demorar 5-10 min)
- [ ] **5. Adicionar badges ao README** com URLs corretos
- [ ] **6. Testar todos os jobs** individualmente
- [ ] **7. Configurar notifications** (opcional)
- [ ] **8. Atualizar TODO.md** marcando como completo

## 🎉 Resultado Final

Com os workflows ativos, o projeto 3dPot terá:

- ✅ **CI/CD automatizado** para validação contínua
- ✅ **Badges de status** no README mostrando qualidade
- ✅ **Testes automáticos** em múltiplas versões Python
- ✅ **Validação de código** Arduino, OpenSCAD, Python
- ✅ **Security scanning** automático
- ✅ **Releases automatizados** no main branch
- ✅ **Documentação gerada** automaticamente

---

**💡 Importante**: Uma vez ativados, os workflows rodarão automaticamente em cada push/PR, mantendo a qualidade do código e validando todas as alterações antes do merge.