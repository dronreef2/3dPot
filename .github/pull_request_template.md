# 📋 Pull Request Template - Projeto 3dPot

## 🎯 Visão Geral

**Motivação:** Breve descrição do problema que esta PR resolve ou melhoria que implementa.

**Exemplo:** 
> Resolver problema de conectividade WiFi do ESP32 em redes 2.4GHz específicas, implementando fallback automático para canais menos congestionados.

## 📊 Resumo das Mudanças

<!-- Descreva as principais mudanças de forma clara e concisa -->

### ✅ O que foi implementado:
- Nova funcionalidade X que resolve problema Y
- Melhoria na interface web com design responsivo
- Corrigido bug de calibração da célula de carga
- Adicionados testes unitários para componente Z

### ❌ O que NÃO foi alterado:
- Sistema de autenticação (mantido inalterado)
- Modelos 3D existentes (não modificados)
- APIs de integração externa (sem mudanças)

## 🔗 Issue Relacionada

Esta PR resolve ou está relacionada a:
- [ ] Fixes #[número] - Descrição do issue
- [ ] Closes #[número] - Descrição do issue
- [ ] Related to #[número] - Descrição do issue
- [ ] No issue relacionada

**Se não há issue relacionada, descreva o motivo:**
> Esta melhoria foi identificada durante testes internos e não estava documentada como issue.

## 🧪 Testes

### Testes Implementados
- [ ] **Testes unitários** adicionados/atualizados
- [ ] **Testes de integração** implementados
- [ ] **Testes manuais** realizados
- [ ] **Testes de hardware** concluídos

### Cenários Testados
- [ ] Configuração inicial do sistema
- [ ] Funcionamento com hardware específico
- [ ] Casos de erro e edge cases
- [ ] Performance e responsividade
- [ ] Compatibilidade com versões anteriores

### Hardware Testado
- [ ] ESP32 DevKit V1
- [ ] Arduino Uno/Nano
- [ ] Raspberry Pi 4
- [ ] Outro: ____________

**Resultados dos Testes:**
```
Resuma os resultados dos testes aqui...
Exemplo: Todos os testes passaram, 95% de cobertura
```

## 📁 Arquivos Modificados

<!-- Liste os principais arquivos alterados -->

### 🆕 Arquivos Criados
- `novo_arquivo.py` - Nova funcionalidade X
- `test_novo_arquivo.py` - Testes da nova funcionalidade
- `docs/nova_documentacao.md` - Documentação específica

### 🔄 Arquivos Modificados
- `README.md` - Atualizado Getting Started
- `codigos/esp32/monitor.ino` - Melhorado algoritmo de calibração
- `assets/screenshots/new_diagram.png` - Novo diagrama

### 🗑️ Arquivos Removidos
- `arquivo_obsoleto.py` - Funcionalidade migrada
- `old_docs/documentacao_antiga.md` - Documentação desnecessária

### 🎯 Principais Mudanças
1. **Feature/Bug Fix** - Impacto: [baixo/médio/alto]
2. **Code Refactoring** - Impacto: [baixo/médio/alto]
3. **Documentation** - Impacto: [baixo/médio/alto]

## 🖼️ Demonstrações

### Antes e Depois
**Screenshot/Imagem anterior:**
![Antes](link-para-imagem-antiga)

**Screenshot/Imagem atual:**
![Depois](link-para-imagem-nova)

### Demonstração em Vídeo
- [ ] Vídeo demonstrando a funcionalidade: [link]
- [ ] GIFs das principais mudanças: [link]

## 🔧 Configuração de Teste

### Hardware Necessário
- ESP32 + HX711 + célula de carga
- Arduino + motor NEMA17 + sensores
- Raspberry Pi 4 + câmera Pi

### Software Necessário
- Python 3.8+
- Arduino IDE 2.x
- PlatformIO (opcional)

### Passos para Testar
```bash
# 1. Clone e setup
git clone https://github.com/dronreef2/3dPot.git
cd 3dPot

# 2. Instale dependências
pip install -r requirements-test.txt

# 3. Execute testes
./run_tests.sh

# 4. Teste específico da PR
python -m pytest tests/unit/test_[arquivo].py -v
```

## 📋 Checklist de PR

### Código
- [ ] **Código segue padrões** do projeto (naming, estrutura)
- [ ] **Sem código duplicado** ou não utilizado
- [ ] **Comentários adequados** para funcionalidades complexas
- [ ] **Tratamento de erros** implementado
- [ ] **Performance otimizada** (se aplicável)

### Testes
- [ ] **Testes unitários** para nova funcionalidade
- [ ] **Testes de integração** quando aplicável
- [ ] **Cobertura de código** > 80% (se aplicável)
- [ ] **Testes passam** localmente
- [ ] **Casos extremos** testados

### Documentação
- [ ] **README.md atualizado** se necessário
- [ ] **Código autodocumentado** com comentários claros
- [ ] **Changelog** atualizado se aplicável
- [ ] **Documentação técnica** para funcionalidades complexas

### 3D Models (se aplicável)
- [ ] **Modelos OpenSCAD** validados
- [ ] **Parâmetros documentados** quando necessário
- [ ] **Arquivos .stl** gerados e testados
- [ ] **Compatibilidade** com impressoras comuns verificada

### Interface Web (se aplicável)
- [ ] **Design responsivo** em diferentes telas
- [ ] **Acessibilidade** básica (labels, alt text)
- [ ] **Cross-browser** compatibility
- [ ] **Performance** otimizada

## 🚀 Impacto da Mudança

### Funcionalidades
- **Adicionadas:** [lista de novas funcionalidades]
- **Modificadas:** [funcionalidades alteradas]
- **Removidas:** [funcionalidades obsoletas]

### Performance
- **Melhorias:** [ex: "Calibração 50% mais rápida"]
- **Degradação:** [se houver, detalhe mitigação]
- **Uso de memória:** [mudanças no consumo]

### Compatibilidade
- **Retrocompatibilidade:** [mantida/quebrada]
- **Migrations necessárias:** [se aplicável]
- **Dependências atualizadas:** [lista de mudanças]

## 🔄 Migrations/Break Changes

Se sua PR introduce mudanças que quebram compatibilidade:

**Migração Necessária:**
```bash
# Comandos para migrar de versão anterior
python scripts/migrate_v1_to_v2.py
```

**Mudanças Quebradas:**
- Configuração anterior não é mais válida
- API endpoints modificados
- Estrutura de dados alterada

**Backward Compatibility:**
- [ ] Mantida via configuração legacy
- [ ] Suporte removido (documentado)
- [ ] Script de migração disponível

## 📊 Métricas (Opcional)

Se aplicável, inclua métricas de impacto:

- **Tempo de execução:** [antes] → [depois]
- **Uso de memória:** [antes] → [depois]  
- **Tamanho do código:** [+/- X linhas]
- **Cobertura de testes:** [X%]
- **Performance de queries:** [X% melhoria]

## 🔍 Review Checklist

### Para Reviewers
- [ ] **Funcionalidade testada** em ambiente real
- [ ] **Código legível** e bem estruturado
- [ ] **Sem security issues** ou dependências problemáticas
- [ ] **Performance aceitável** para casos de uso
- [ ] **Documentação suficiente** para usuários

### Para Autor
- [ ] **Autoteste completo** realizado
- [ ] **Documentação atualizada** conforme necessário
- [ ] **Problemas conocidos** documentados
- [ ] **Roadmap de melhorias** identificado (se aplicável)

## 🎯 Próximos Passos

**Após esta PR ser mergeada:**
- [ ] Release notes preparadas
- [ ] Documentação de usuário atualizada
- [ ] Comunidade notificada (se mudança significativa)
- [ ] Monitoramento de issues nos próximos dias

**Melhorias futuras identificadas:**
- [ ] Funcionalidade X pode ser expandida
- [ ] Performance Y pode ser otimizada
- [ ] Interface Z pode ser melhorada

## 🏷️ Labels Sugeridas

- [ ] `bug` - Se corrige um problema
- [ ] `enhancement` - Se adiciona funcionalidade
- [ ] `documentation` - Se foca em documentação
- [ ] `good first issue` - Se simples para iniciantes
- [ ] `help wanted` - Se precisa de assistência
- [ ] `hardware` - Se envolve mudanças físicas
- [ ] `software` - Se foca em código
- [ ] `3d-models` - Se envolve modelos 3D

## 📝 Notas do Autor

**Decisões de design tomadas:**
- [X] Escolhida abordagem A ao invés de B porque [motivo]
- [X] Implementado X antes de Y porque [motivo]
- [ ] Trade-off aceito: [descrição] → [mitigação]

**Problemas conhecidos:**
- Interface ainda não otimizada para mobile
- Performance degrada com >100 dispositivos conectados
- Biblioteca X pode ser deprecada em versão futura

**Agradecimentos:**
- Agradecimentos especiais a [pessoa] por [contribuição específica]

---

## 🤝 Contribuição

Para mais informações sobre como contribuir, consulte:
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- [Wiki do Projeto](https://github.com/dronreef2/3dPot/wiki)

**Obrigado por contribuir com o 3dPot!** 🚀

---

<!--
Dicas para uma boa PR:
1. Seja específico sobre o que está mudando
2. Teste em diferentes configurações de hardware
3. Mantenha mudanças focadas e pequenas quando possível
4. Documente decisões de design importantes
5. Responda rapidamente a feedback dos reviewers
-->