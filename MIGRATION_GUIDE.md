# Guia de Migração - Reorganização do Repositório 3dPot

## 🎯 Objetivo

Este documento ajuda contribuidores existentes a migrar seu trabalho após a reorganização estrutural do repositório 3dPot realizada em novembro de 2024.

## 📊 Resumo das Mudanças

### Movimentações de Arquivos

#### Documentação (96 arquivos movidos)
```
Raiz → docs/sprints/        (21 arquivos SPRINT*, PLANO-SPRINT*, etc.)
Raiz → docs/relatorios/     (35 arquivos RELATORIO*, RESUMO*, ENTREGA*, etc.)
Raiz → docs/validacao/      (18 arquivos CI_*, VALIDATION_*, etc.)
Raiz → docs/arquitetura/    (11 arquivos ARQUITETURA*, TODO.md, etc.)
Raiz → docs/guias/          (13 arquivos README-*, GUIA-*, etc.)
```

#### Testes (12 arquivos movidos)
```
Raiz → tests/integration/           (7 arquivos: test_*.py, teste_*.py)
Raiz → scripts/demos/               (5 arquivos de teste standalone)
```

#### Scripts (18 arquivos movidos)
```
Raiz → scripts/validacao/           (5 arquivos de validação)
Raiz → scripts/dados/               (1 arquivo de geração de dados)
Raiz → scripts/monitoramento/       (2 arquivos de monitoramento)
Raiz → scripts/demos/               (10 arquivos de demonstração/integração)
```

#### Frontend (3 arquivos movidos)
```
Raiz → frontend/demos/              (3 arquivos HTML de demonstração)
```

#### Outputs (6 arquivos movidos)
```
Raiz → outputs/relatorios/          (4 arquivos JSON de validação)
Raiz → outputs/                     (2 arquivos JSON de status)
```

## 🔧 Como Atualizar Seu Código

### 1. Atualizar Imports em Python

#### Antes:
```python
# Importando de testes na raiz
from test_integration import test_basic_integration

# Importando scripts na raiz
from validate_openscad_models import validate_model
```

#### Depois:
```python
# Importando de tests/integration/
from tests.integration.test_integration import test_basic_integration

# Importando de scripts/validacao/
from scripts.validacao.validate_openscad_models import validate_model
```

### 2. Atualizar Caminhos de Arquivos

#### Antes:
```python
# Carregando relatório da raiz
with open('validation_report.json', 'r') as f:
    data = json.load(f)

# Executando script de validação
subprocess.run(['python', 'validate_openscad_models.py'])
```

#### Depois:
```python
# Carregando relatório de outputs/
with open('outputs/relatorios/validation_report.json', 'r') as f:
    data = json.load(f)

# Executando script de validação
subprocess.run(['python', 'scripts/validacao/validate_openscad_models.py'])
```

### 3. Atualizar Links de Documentação

#### Antes (em arquivos Markdown):
```markdown
Para mais detalhes, veja [SPRINT1-CONCLUIDO.md](SPRINT1-CONCLUIDO.md)
Consulte o [TODO.md](TODO.md) para próximas tarefas
```

#### Depois:
```markdown
Para mais detalhes, veja [SPRINT1-CONCLUIDO.md](docs/sprints/SPRINT1-CONCLUIDO.md)
Consulte o [TODO.md](docs/arquitetura/TODO.md) para próximas tarefas
```

### 4. Atualizar Configurações de CI/CD

Se você tem workflows customizados que referenciam arquivos movidos:

#### Antes:
```yaml
- name: Validate models
  run: python validate_openscad_models.py
  
- name: Run integration tests
  run: pytest test_integration.py
```

#### Depois:
```yaml
- name: Validate models
  run: python scripts/validacao/validate_openscad_models.py
  
- name: Run integration tests
  run: pytest tests/integration/test_integration.py
```

### 5. Atualizar Scripts Shell

#### Antes:
```bash
#!/bin/bash
python validate_openscad_models.py
python test_integration.py
cat validation_report.json
```

#### Depois:
```bash
#!/bin/bash
python scripts/validacao/validate_openscad_models.py
pytest tests/integration/test_integration.py
cat outputs/relatorios/validation_report.json
```

## 📝 Checklist de Migração

Use este checklist para garantir que seu código está atualizado:

- [ ] **Atualizei minha branch local**
  ```bash
  git checkout main
  git pull origin main
  ```

- [ ] **Verifiquei imports Python**
  - [ ] Testes movidos de raiz para `tests/integration/`
  - [ ] Scripts movidos de raiz para `scripts/*/`
  - [ ] Atualizei todos os imports afetados

- [ ] **Verifiquei caminhos de arquivos**
  - [ ] Relatórios JSON agora em `outputs/`
  - [ ] Documentação agora em `docs/*/`
  - [ ] Atualizei caminhos hardcoded

- [ ] **Verifiquei links de documentação**
  - [ ] Links para documentos markdown atualizados
  - [ ] Links relativos corrigidos

- [ ] **Executei testes localmente**
  ```bash
  pytest tests/
  ```

- [ ] **Verifiquei workflows de CI/CD**
  - [ ] GitHub Actions atualizadas (se aplicável)
  - [ ] Scripts de deployment atualizados (se aplicável)

- [ ] **Atualizei .gitignore se necessário**
  - `outputs/` agora é ignorado

## 🗺️ Mapa de Localização Rápida

### Onde encontrar cada tipo de arquivo:

| Tipo de Arquivo | Localização Antiga | Localização Nova |
|-----------------|-------------------|------------------|
| Testes de integração | Raiz (`test_*.py`) | `tests/integration/` |
| Testes unitários | `tests/unit/` | `tests/unit/` (sem mudança) |
| Scripts de validação | Raiz | `scripts/validacao/` |
| Scripts de demo | Raiz | `scripts/demos/` |
| Scripts de dados | Raiz | `scripts/dados/` |
| Scripts de monitoramento | Raiz | `scripts/monitoramento/` |
| Documentação de sprint | Raiz | `docs/sprints/` |
| Relatórios | Raiz | `docs/relatorios/` |
| Guias | Raiz | `docs/guias/` |
| Arquitetura | Raiz | `docs/arquitetura/` |
| Validação CI | Raiz | `docs/validacao/` |
| Demos HTML | Raiz | `frontend/demos/` |
| Relatórios JSON | Raiz | `outputs/relatorios/` |

## 🚨 Problemas Comuns

### Problema 1: Import Error
```
ModuleNotFoundError: No module named 'test_integration'
```

**Solução**: Atualize o import para incluir o caminho completo:
```python
from tests.integration.test_integration import ...
```

### Problema 2: FileNotFoundError
```
FileNotFoundError: [Errno 2] No such file or directory: 'validation_report.json'
```

**Solução**: Atualize o caminho para o novo local:
```python
'outputs/relatorios/validation_report.json'
```

### Problema 3: Testes não são descobertos pelo pytest
```
collected 0 items
```

**Solução**: Certifique-se de que:
1. Os testes estão em `tests/integration/` ou `tests/unit/`
2. Os arquivos começam com `test_` ou terminam com `_test.py`
3. Execute `pytest tests/` ao invés de especificar arquivos individuais

### Problema 4: Links quebrados em documentação
```
[Link] referencia arquivo que não existe
```

**Solução**: Atualize links relativos para refletir a nova estrutura:
- Documentação agora está em subpastas de `docs/`
- Use caminhos relativos a partir da localização do arquivo markdown

## 🔄 Rebase de Branches

Se você tem branches em desenvolvimento:

```bash
# 1. Certifique-se de que main está atualizado
git checkout main
git pull origin main

# 2. Vá para sua branch
git checkout minha-branch

# 3. Faça rebase com main
git rebase main

# 4. Resolva conflitos se houver
# Os conflitos provavelmente serão em imports ou caminhos de arquivo

# 5. Execute testes
pytest tests/

# 6. Force push se necessário (cuidado!)
git push --force-with-lease origin minha-branch
```

## 📞 Suporte

Se você encontrar problemas não cobertos por este guia:

1. **Verifique o STRUCTURE.md** para entender a nova organização
2. **Consulte a documentação** em `docs/guias/`
3. **Abra uma issue** no GitHub com:
   - Descrição do problema
   - Código ou configuração afetada
   - Mensagem de erro (se houver)

## 📚 Recursos Adicionais

- [STRUCTURE.md](STRUCTURE.md) - Estrutura completa do repositório
- [README.md](README.md) - Documentação principal
- [CONTRIBUTING.md](CONTRIBUTING.md) - Guia de contribuição
- [docs/arquitetura/TODO.md](docs/arquitetura/TODO.md) - Tarefas pendentes

## ✅ Próximos Passos

Após concluir a migração:

1. Execute todos os testes localmente
2. Verifique se seu código funciona corretamente
3. Faça commit das mudanças necessárias
4. Atualize a documentação do seu código se necessário
5. Continue contribuindo! 🚀

---

**Data da Reorganização**: Novembro 2024  
**Versão do Guia**: 1.0
