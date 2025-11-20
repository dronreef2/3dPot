# Guia Rápido - Framework Adapter

Este guia permite que você comece a usar o Framework Adapter em menos de 5 minutos.

---

## ⚡ Início Rápido (5 minutos)

### Passo 1: Prepare as Informações do Seu Projeto

Tenha em mãos:
- URL do repositório
- Stack tecnológico (ex: "Python/FastAPI", "Node/Express")
- Objetivo do projeto (1-2 frases)
- Estado aproximado de:
  - Testes
  - Observabilidade
  - Segurança
  - Documentação

### Passo 2: Execute o Framework Adapter

```bash
cd scripts/framework-adapter
python framework_adapter.py
```

### Passo 3: Responda as Perguntas

O script irá guiá-lo:

```
URL do repositório alvo: https://github.com/seu-usuario/seu-projeto
Stack tecnológico: Python/FastAPI
Objetivos do projeto: API REST para gestão de tarefas
Cobertura de testes: ~40%
Observabilidade: logs básicos
Segurança: JWT básico
Documentação: mínima
```

### Passo 4: Revise o Output

Arquivos gerados em `./framework-output/`:
- `FRAMEWORK-APLICADO.md` - **LEIA ESTE PRIMEIRO**
- `prompts/sprint-1-*.txt` - Prompts prontos para usar

### Passo 5: Execute Sua Primeira Sprint

1. Abra `FRAMEWORK-APLICADO.md`
2. Leia a seção "Roadmap Sugerido"
3. Copie o prompt da Sprint 1
4. Cole no GitHub Copilot / ChatGPT / Claude
5. Siga as instruções da IA

---

## 📋 Respostas Comuns por Tipo de Projeto

### Projeto Novo (MVP)

```
Cobertura de testes: sem testes
Observabilidade: nenhuma
Segurança: mínima
Documentação: mínima
```

**Resultado:** Roadmap focado em fundação (estrutura → testes → CI)

---

### Projeto em Desenvolvimento

```
Cobertura de testes: ~50%
Observabilidade: logs básicos
Segurança: JWT básico
Documentação: moderada
```

**Resultado:** Roadmap focado em completar testes + observabilidade

---

### Projeto em Produção

```
Cobertura de testes: ~70%
Observabilidade: logs + métricas básicas
Segurança: JWT + RBAC
Documentação: extensa
```

**Resultado:** Roadmap focado em hardening + DR + operações

---

## 🎯 Fluxo de Trabalho Típico

```
1. Executar Framework Adapter (5 min)
   ↓
2. Ler FRAMEWORK-APLICADO.md (10 min)
   ↓
3. Completar checklist pré-sprint (30 min)
   ↓
4. Escolher primeira sprint (5 min)
   ↓
5. Copiar prompt adaptado (1 min)
   ↓
6. Executar com IA (variável)
   ↓
7. Revisar e aplicar código (variável)
   ↓
8. Validar com testes (15-30 min)
   ↓
9. Documentar sprint (15 min)
   ↓
10. Repetir para próxima sprint
```

---

## 🚀 Atalhos por Linguagem/Stack

### Python/FastAPI

```bash
python framework_adapter.py \
  --stack "Python/FastAPI + PostgreSQL" \
  --test-coverage "~40%" \
  --observability "logs básicos" \
  --security "JWT básico" \
  --documentation "mínima"
```

### Node.js/Express

```bash
python framework_adapter.py \
  --stack "Node.js/Express + MongoDB" \
  --test-coverage "sem testes" \
  --observability "nenhuma" \
  --security "mínima" \
  --documentation "mínima"
```

### Java/Spring Boot

```bash
python framework_adapter.py \
  --stack "Java/Spring Boot + MySQL" \
  --test-coverage "~60%" \
  --observability "logs estruturados + métricas" \
  --security "OAuth2 + RBAC" \
  --documentation "moderada"
```

### Go

```bash
python framework_adapter.py \
  --stack "Go + PostgreSQL" \
  --test-coverage "~50%" \
  --observability "logs básicos" \
  --security "JWT + rate limiting" \
  --documentation "moderada"
```

---

## ❓ Perguntas Frequentes

### "Não sei minha cobertura de testes exata"

Use aproximações:
- "sem testes" - se < 10%
- "~30%" - se tem alguns testes
- "~50%" - se metade dos módulos testados
- "~70%" - se maioria testada
- "~85%" - se quase tudo testado

### "O que significa 'logs básicos'?"

- **Nenhuma:** Sem logging estruturado, apenas prints
- **Logs básicos:** Console.log / print / logging básico
- **Avançada:** Logs estruturados (JSON) + métricas

### "Quanto tempo leva cada sprint?"

Varia por projeto, mas tipicamente:
- Sprint 1 (Estrutura): 1-2 dias
- Sprint 2 (Testes): 3-5 dias
- Sprints 6-9: 2-3 dias cada

### "Posso pular sprints?"

Sim, mas com cuidado:
- ✅ Pode pular se já tiver implementado
- ⚠️ Não pule testes (Sprint 2-5)
- ⚠️ Não pule estrutura (Sprint 1) se desorganizado

---

## 🎓 Próximos Passos

Após executar o Framework Adapter:

1. **Leia a documentação completa:**
   - [README.md](./README.md)
   - [EXEMPLOS.md](./EXEMPLOS.md)

2. **Explore o framework original:**
   - [AI-SPRINT-FRAMEWORK.md](../../docs/arquitetura/AI-SPRINT-FRAMEWORK.md)
   - [AI-SPRINT-PROMPTS.md](../../docs/arquitetura/AI-SPRINT-PROMPTS.md)

3. **Siga o playbook:**
   - [ENG-PLAYBOOK-IA.md](../../docs/arquitetura/ENG-PLAYBOOK-IA.md)

---

## 📞 Precisa de Ajuda?

- 📖 Leia [EXEMPLOS.md](./EXEMPLOS.md) para casos de uso detalhados
- 📚 Consulte [README.md](./README.md) para documentação completa
- 🔍 Veja o [framework completo](../../docs/arquitetura/AI-SPRINT-FRAMEWORK.md)

---

**Tempo total para começar:** < 5 minutos  
**Primeira sprint:** 1-5 dias (dependendo do projeto)  
**Production-ready:** 2-4 semanas (seguindo todas as sprints)
