# Scripts de Demonstração do 3dPot

Este diretório contém scripts de demonstração e teste para diferentes funcionalidades do sistema 3dPot.

## 📋 Índice de Scripts

### 🎯 Demonstrações Principais

#### `demonstracao_sistema.py`
**Descrição:** Demonstração geral do sistema 3dPot  
**Uso:** `python scripts/demos/demonstracao_sistema.py`  
**O que faz:**
- Apresenta visão geral das funcionalidades
- Demonstra fluxo básico do sistema

#### `test-auth-system.py`
**Descrição:** Demonstração do sistema de autenticação  
**Uso:** `python scripts/demos/test-auth-system.py`  
**O que faz:**
- Testa login/logout
- Demonstra autenticação JWT
- Valida permissões de acesso

### 🤖 Integração com IA

#### `lgm_integration_example.py`
**Descrição:** Exemplo de integração com LGM (Large Geometry Model)  
**Uso:** `python scripts/demos/lgm_integration_example.py`  
**O que faz:**
- Demonstra geração de modelos 3D com IA
- Mostra pipeline de processamento LGM
- Exemplos de prompts e resultados

#### `teste-minimax-standalone.py`
**Descrição:** Teste standalone da integração Minimax  
**Uso:** `python scripts/demos/teste-minimax-standalone.py`  
**O que faz:**
- Testa API Minimax de forma isolada
- Demonstra conversação com IA
- Valida configurações e credenciais

#### `teste-rapido-minimax.py`
**Descrição:** Teste rápido do sistema Minimax  
**Uso:** `python scripts/demos/teste-rapido-minimax.py`  
**O que faz:**
- Validação rápida de configuração Minimax
- Teste de conectividade
- Verificação de resposta da API

### 🏭 Integração com Serviços Externos

#### `slant3d_integration.py`
**Descrição:** Integração com serviço de impressão Slant3D  
**Uso:** `python scripts/demos/slant3d_integration.py`  
**O que faz:**
- Demonstra envio de modelos para Slant3D
- Mostra cálculo de orçamentos
- Valida integração de produção

### 🎨 Sistema de Modelagem

#### `sistema_modelagem_lgm_integrado.py`
**Descrição:** Sistema completo de modelagem com LGM  
**Uso:** `python scripts/demos/sistema_modelagem_lgm_integrado.py`  
**O que faz:**
- Pipeline completo de modelagem
- Integração LGM + validação
- Geração e exportação de modelos

#### `teste-sistema-modelagem-sprint3.py`
**Descrição:** Testes do sistema de modelagem (Sprint 3)  
**Uso:** `python scripts/demos/teste-sistema-modelagem-sprint3.py`  
**O que faz:**
- Valida funcionalidades do Sprint 3
- Testa geração de modelos 3D
- Verifica exportação STL/OBJ

#### `teste-standalone-sprint3.py`
**Descrição:** Testes standalone do Sprint 3  
**Uso:** `python scripts/demos/teste-standalone-sprint3.py`  
**O que faz:**
- Testes isolados das features do Sprint 3
- Não requer backend rodando
- Valida componentes individuais

### 🌐 Servidores de Integração

#### `servidor_integracao.py`
**Descrição:** Servidor de integração para demonstrações  
**Uso:** `python scripts/demos/servidor_integracao.py`  
**O que faz:**
- Inicia servidor demo local
- Expõe endpoints de teste
- Facilita testes de integração

## 🚀 Como Usar

### Pré-requisitos

```bash
# Instalar dependências
pip install -r requirements.txt
pip install -r requirements-test.txt
```

### Executar uma Demonstração

```bash
# Exemplo: Testar autenticação
python scripts/demos/test-auth-system.py

# Exemplo: Demonstração Minimax
python scripts/demos/teste-rapido-minimax.py

# Exemplo: Integração LGM
python scripts/demos/lgm_integration_example.py
```

### Configuração de Variáveis de Ambiente

Alguns scripts requerem variáveis de ambiente configuradas:

```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Configure suas credenciais
# MINIMAX_API_KEY=sua_chave_aqui
# SLANT3D_API_KEY=sua_chave_aqui
# DATABASE_URL=postgresql://...
```

## 📝 Notas Importantes

### Scripts Legados

Alguns scripts podem estar marcados como **legados** ou **deprecated** se foram substituídos por versões mais novas. Verifique os comentários no início de cada arquivo.

### Scripts de Teste vs Demonstração

- **test-*.py**: Scripts focados em teste de funcionalidades específicas
- **teste-*.py**: Scripts de teste (nomenclatura em português)
- Outros: Scripts de demonstração geral

### Dependências Específicas

Alguns scripts podem ter dependências extras:
- `lgm_integration_example.py`: Requer bibliotecas de processamento 3D
- `slant3d_integration.py`: Requer credenciais Slant3D
- `teste-minimax-*.py`: Requer credenciais Minimax

## 🐛 Troubleshooting

### Erro de Importação

```bash
# Se encontrar erro de importação, execute do diretório raiz:
cd /caminho/para/3dPot
python scripts/demos/nome_do_script.py
```

### Erro de Conexão com Backend

```bash
# Certifique-se de que o backend está rodando:
cd backend
python -m uvicorn main:app --reload
```

### Erro de Credenciais

```bash
# Verifique suas variáveis de ambiente:
cat .env

# Configure as credenciais necessárias
```

## 📚 Documentação Adicional

- [README principal](../../README.md)
- [Guias de uso](../../docs/guias/)
- [Documentação da API](http://localhost:8000/docs) (quando o backend estiver rodando)

## 🤝 Contribuindo

Para adicionar novos scripts de demonstração:

1. Crie o script seguindo a nomenclatura existente
2. Adicione documentação no início do arquivo
3. Atualize este README.md
4. Teste o script antes de commitar

---

**Última atualização:** 2024-11-19  
**Versão:** 2.0
