#!/usr/bin/env python3
"""
Framework Adapter - Apply AI-Driven Sprint Framework to Other Repositories

This tool helps you adapt the 3dPot AI-Sprint Framework to your own repository
by analyzing your project's current state and generating customized:
- Sprint roadmap (4-6 sprints)
- Adapted prompts (ready to use with AI assistants)
- Pre-sprint checklist
"""

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ProjectState:
    """Represents the current state of a target project."""
    repo_url: str
    stack: str
    objectives: str
    test_coverage: str
    observability: str
    security: str
    documentation: str


@dataclass
class SprintRecommendation:
    """Represents a recommended sprint."""
    number: int
    name: str
    focus: str
    objectives: List[str]
    deliverables: List[str]
    duration: str
    priority: str  # "HIGH", "MEDIUM", "LOW"


class FrameworkAdapter:
    """Main class for adapting the AI-Sprint Framework to target repositories."""
    
    # Sprint definitions from the framework
    SPRINT_DEFINITIONS = {
        1: {
            "name": "Reorganização e Estrutura",
            "focus": "Estabelecer estrutura clara e navegável",
            "typical_objectives": [
                "Auditar estrutura atual de diretórios",
                "Propor nova estrutura hierárquica",
                "Mover arquivos para locais apropriados",
                "Atualizar imports e referências",
                "Criar/atualizar README e STRUCTURE.md"
            ],
            "typical_deliverables": [
                "Estrutura de diretórios clara e documentada",
                "Redução de arquivos na raiz (>70%)",
                "README.md e STRUCTURE.md atualizados",
                "MIGRATION_GUIDE.md (se aplicável)"
            ],
            "duration": "1-2 dias",
            "dependencies": []
        },
        2: {
            "name": "Testes Básicos de Unidade",
            "focus": "Estabelecer base sólida de testes para componentes críticos",
            "typical_objectives": [
                "Mapear serviços/módulos críticos sem testes",
                "Priorizar por criticidade de negócio",
                "Criar testes unitários para top 5-7 módulos",
                "Configurar coverage reporting",
                "Estabelecer threshold mínimo (70%)"
            ],
            "typical_deliverables": [
                "150+ testes unitários novos",
                "Cobertura de 5+ módulos críticos",
                "Coverage report configurado",
                "Documentação de padrões de teste",
                "Threshold de cobertura no CI"
            ],
            "duration": "3-5 dias",
            "dependencies": [1]
        },
        3: {
            "name": "Integração + CLI",
            "focus": "Consolidar testes de integração e criar ferramentas CLI",
            "typical_objectives": [
                "Auditar testes de integração existentes",
                "Consolidar testes duplicados",
                "Criar CLI unificada para demos/ferramentas",
                "Implementar testes E2E para fluxos críticos (2-5)",
                "Documentar comandos CLI"
            ],
            "typical_deliverables": [
                "Testes de integração consolidados",
                "CLI unificada com 8-10 comandos",
                "5-10 testes E2E básicos",
                "Documentação de CLI",
                "Testes da CLI"
            ],
            "duration": "2-3 dias",
            "dependencies": [2]
        },
        4: {
            "name": "Cobertura Ampliada + CI",
            "focus": "Expandir cobertura de testes e automatizar verificações",
            "typical_objectives": [
                "Cobrir módulos secundários com testes",
                "Expandir testes E2E (mais 5-10 fluxos)",
                "Adicionar testes para CLI",
                "Configurar CI/CD com testes, coverage e linting",
                "Estabelecer políticas de merge (CI deve passar)"
            ],
            "typical_deliverables": [
                "80-120 novos testes unitários",
                "3-5 novos fluxos E2E",
                "20-30 testes CLI",
                "CI/CD com jobs separados",
                "Coverage threshold enforced"
            ],
            "duration": "3-4 dias",
            "dependencies": [3]
        },
        5: {
            "name": "Qualidade Final",
            "focus": "Atingir 100% de cobertura de serviços e estabelecer métricas",
            "typical_objectives": [
                "Cobrir TODOS os serviços restantes",
                "Implementar testes de performance/carga (básicos)",
                "Refinar CLI com utilitários centralizados",
                "Expandir E2E para cenários avançados",
                "Estabelecer roadmap para Release Candidate"
            ],
            "typical_deliverables": [
                "100% dos serviços com testes",
                "Framework de performance básico",
                "3-5 novos fluxos E2E avançados",
                "Utilitários CLI centralizados",
                "Relatório de qualidade"
            ],
            "duration": "2-3 dias",
            "dependencies": [4]
        },
        6: {
            "name": "Observabilidade",
            "focus": "Implementar logging estruturado, métricas e tracing",
            "typical_objectives": [
                "Implementar logging estruturado (JSON + console)",
                "Adicionar métricas Prometheus (HTTP, serviços, erros)",
                "Implementar request IDs para rastreamento",
                "Criar middleware de logging automático",
                "Configurar formatadores por ambiente (dev/prod)"
            ],
            "typical_deliverables": [
                "Logging estruturado implementado",
                "Métricas Prometheus básicas",
                "Request ID em todos os logs",
                "Middleware de logging automático",
                "Endpoint /metrics",
                "Documentação de observabilidade"
            ],
            "duration": "2-3 dias",
            "dependencies": [5]
        },
        7: {
            "name": "Segurança Base",
            "focus": "Implementar controles de segurança essenciais",
            "typical_objectives": [
                "Implementar rate limiting (token bucket)",
                "Adicionar audit logging para ações críticas",
                "Fortalecer gestão de secrets (.env, variáveis)",
                "Implementar/melhorar RBAC",
                "Configurar limites por endpoint"
            ],
            "typical_deliverables": [
                "Rate limiting implementado",
                "Audit logging para ações críticas",
                "Gestão segura de secrets",
                "RBAC funcional",
                "Testes de segurança (40+)",
                "Documentação de segurança"
            ],
            "duration": "2-3 dias",
            "dependencies": [6]
        },
        8: {
            "name": "Hardening e Escala",
            "focus": "Preparar para escala horizontal e hardening de segurança",
            "typical_objectives": [
                "Implementar rate limiting distribuído (Redis)",
                "Adicionar RBAC granular com ownership",
                "Criar CI/CD security gates (SAST, dependency scanning)",
                "Adicionar métricas de segurança",
                "Documentar runbook operacional (inicial)"
            ],
            "typical_deliverables": [
                "Rate limiting distribuído",
                "RBAC granular",
                "Security gates no CI/CD",
                "Métricas de segurança",
                "Runbook operacional inicial",
                "Testes de hardening"
            ],
            "duration": "2-3 dias",
            "dependencies": [7]
        },
        9: {
            "name": "Operações, DR e MFA",
            "focus": "Completar preparação para produção com MFA e DR",
            "typical_objectives": [
                "Implementar MFA/2FA (TOTP)",
                "Criar scripts de backup automatizados",
                "Criar scripts de restore com validação",
                "Implementar distributed tracing (trace_id)",
                "Criar operations runbook completo (500+ linhas)",
                "Executar security scans finais"
            ],
            "typical_deliverables": [
                "MFA/2FA implementado",
                "Scripts de backup/restore",
                "Distributed tracing (trace_id)",
                "Operations runbook (500+ linhas)",
                "Security scans executados",
                "Documentação de DR",
                "Testes de MFA e DR"
            ],
            "duration": "3-4 dias",
            "dependencies": [8]
        }
    }
    
    def __init__(self, project_state: ProjectState):
        self.project_state = project_state
    
    def estimate_current_stage(self) -> Dict[str, any]:
        """
        Estimate which sprint stage the project is currently at based on the state.
        
        Returns:
            Dict containing estimated stage and reasoning
        """
        state = self.project_state
        score = 0
        stage_info = {
            "estimated_stage": "Sprint 1-2",
            "reasoning": [],
            "completed_sprints": [],
            "recommended_start": 1
        }
        
        # Analyze test coverage
        coverage_lower = state.test_coverage.lower()
        if "sem testes" in coverage_lower or "0%" in coverage_lower:
            score += 0
            stage_info["reasoning"].append("Sem testes ou cobertura mínima - precisa começar com Sprint 2")
        elif any(x in coverage_lower for x in ["40%", "50%", "60%"]):
            score += 2
            stage_info["completed_sprints"].append(1)
            stage_info["reasoning"].append("Cobertura básica (40-60%) - Sprint 2 em andamento ou próxima")
        elif any(x in coverage_lower for x in ["70%", "80%", "85%"]):
            score += 5
            stage_info["completed_sprints"].extend([1, 2, 3, 4])
            stage_info["reasoning"].append("Boa cobertura (70-85%) - Sprints 2-4 provavelmente completas")
        
        # Analyze observability
        obs_lower = state.observability.lower()
        if "avançada" in obs_lower or "completa" in obs_lower:
            score += 3
            stage_info["completed_sprints"].append(6)
            stage_info["reasoning"].append("Observabilidade avançada - Sprint 6 completa")
        elif "logs" in obs_lower and ("métricas" in obs_lower or "metrics" in obs_lower):
            score += 2
            stage_info["reasoning"].append("Observabilidade parcial - Sprint 6 em andamento")
        elif "básica" in obs_lower or "logs básicos" in obs_lower:
            score += 0
            stage_info["reasoning"].append("Observabilidade básica - Sprint 6 necessária")
        else:
            stage_info["reasoning"].append("Observabilidade inexistente - Sprint 6 altamente recomendada")
        
        # Analyze security
        sec_lower = state.security.lower()
        if "mfa" in sec_lower or "2fa" in sec_lower:
            score += 4
            stage_info["completed_sprints"].extend([7, 8, 9])
            stage_info["reasoning"].append("Segurança avançada com MFA - Sprints 7-9 completas ou em andamento")
        elif "rbac" in sec_lower or "rate limit" in sec_lower:
            score += 3
            stage_info["completed_sprints"].extend([7, 8])
            stage_info["reasoning"].append("Segurança intermediária (RBAC/rate limiting) - Sprint 7-8 em andamento")
        elif "jwt" in sec_lower or "auth" in sec_lower:
            score += 1
            stage_info["reasoning"].append("Autenticação básica - Sprints 7-8 necessárias")
        else:
            stage_info["reasoning"].append("Segurança mínima - Sprints 7-9 altamente recomendadas")
        
        # Analyze documentation
        doc_lower = state.documentation.lower()
        if "extensa" in doc_lower or "completa" in doc_lower:
            score += 1
            stage_info["reasoning"].append("Documentação extensa")
        elif "moderada" in doc_lower:
            score += 0.5
            stage_info["reasoning"].append("Documentação moderada - pode melhorar")
        else:
            stage_info["reasoning"].append("Documentação mínima - precisa melhorar ao longo das sprints")
        
        # Determine stage based on score
        if score <= 1:
            stage_info["estimated_stage"] = "Sprint 1-2"
            stage_info["recommended_start"] = 1
        elif score <= 3:
            stage_info["estimated_stage"] = "Sprint 2-3"
            stage_info["recommended_start"] = 2
        elif score <= 5:
            stage_info["estimated_stage"] = "Sprint 3-5"
            stage_info["recommended_start"] = 3
        elif score <= 7:
            stage_info["estimated_stage"] = "Sprint 5-6"
            stage_info["recommended_start"] = 6
        else:
            stage_info["estimated_stage"] = "Sprint 7-9"
            stage_info["recommended_start"] = 7
        
        return stage_info
    
    def generate_roadmap(self, num_sprints: int = 6) -> List[SprintRecommendation]:
        """
        Generate a customized roadmap of recommended sprints.
        
        Args:
            num_sprints: Number of sprints to recommend (default: 6)
        
        Returns:
            List of SprintRecommendation objects
        """
        stage_info = self.estimate_current_stage()
        start_sprint = stage_info["recommended_start"]
        completed = set(stage_info["completed_sprints"])
        
        recommendations = []
        sprint_num = 1
        
        # Always include Sprint 1 if not completed
        if 1 not in completed:
            sprint_data = self.SPRINT_DEFINITIONS[1]
            recommendations.append(SprintRecommendation(
                number=sprint_num,
                name=sprint_data["name"],
                focus=sprint_data["focus"],
                objectives=sprint_data["typical_objectives"],
                deliverables=sprint_data["typical_deliverables"],
                duration=sprint_data["duration"],
                priority="HIGH"
            ))
            sprint_num += 1
        
        # Add test-related sprints (2-5) if needed
        if self.project_state.test_coverage.lower() in ["desconhecida", "sem testes", "0%", "baixa"]:
            for i in [2, 3, 4, 5]:
                if i not in completed and sprint_num <= num_sprints:
                    sprint_data = self.SPRINT_DEFINITIONS[i]
                    priority = "HIGH" if i == 2 else "MEDIUM"
                    recommendations.append(SprintRecommendation(
                        number=sprint_num,
                        name=sprint_data["name"],
                        focus=sprint_data["focus"],
                        objectives=sprint_data["typical_objectives"],
                        deliverables=sprint_data["typical_deliverables"],
                        duration=sprint_data["duration"],
                        priority=priority
                    ))
                    sprint_num += 1
        
        # Add observability sprint if needed
        if 6 not in completed and sprint_num <= num_sprints:
            obs_lower = self.project_state.observability.lower()
            if "nenhuma" in obs_lower or "básica" in obs_lower or "logs básicos" in obs_lower:
                sprint_data = self.SPRINT_DEFINITIONS[6]
                recommendations.append(SprintRecommendation(
                    number=sprint_num,
                    name=sprint_data["name"],
                    focus=sprint_data["focus"],
                    objectives=sprint_data["typical_objectives"],
                    deliverables=sprint_data["typical_deliverables"],
                    duration=sprint_data["duration"],
                    priority="HIGH"
                ))
                sprint_num += 1
        
        # Add security sprints if needed
        if 7 not in completed and sprint_num <= num_sprints:
            sec_lower = self.project_state.security.lower()
            if "mínima" in sec_lower or "jwt básico" in sec_lower or "básica" in sec_lower:
                sprint_data = self.SPRINT_DEFINITIONS[7]
                recommendations.append(SprintRecommendation(
                    number=sprint_num,
                    name=sprint_data["name"],
                    focus=sprint_data["focus"],
                    objectives=sprint_data["typical_objectives"],
                    deliverables=sprint_data["typical_deliverables"],
                    duration=sprint_data["duration"],
                    priority="MEDIUM"
                ))
                sprint_num += 1
        
        # Add hardening and operations if room
        for i in [8, 9]:
            if i not in completed and sprint_num <= num_sprints:
                sprint_data = self.SPRINT_DEFINITIONS[i]
                recommendations.append(SprintRecommendation(
                    number=sprint_num,
                    name=sprint_data["name"],
                    focus=sprint_data["focus"],
                    objectives=sprint_data["typical_objectives"],
                    deliverables=sprint_data["typical_deliverables"],
                    duration=sprint_data["duration"],
                    priority="LOW"
                ))
                sprint_num += 1
        
        return recommendations[:num_sprints]
    
    def adapt_prompt(self, sprint_number: int) -> str:
        """
        Adapt a sprint prompt template with the project-specific information.
        
        Args:
            sprint_number: Which sprint to adapt (1-9)
        
        Returns:
            Adapted prompt ready to use with AI
        """
        if sprint_number not in self.SPRINT_DEFINITIONS:
            raise ValueError(f"Invalid sprint number: {sprint_number}")
        
        sprint = self.SPRINT_DEFINITIONS[sprint_number]
        state = self.project_state
        
        # Base prompt structure
        prompt = f"""Você é um assistente sênior de engenharia especializado em {sprint['name'].lower()}.

[CONTEXTO]
Repositório: {state.repo_url}
Stack principal: {state.stack}
Objetivos do projeto: {state.objectives}

Estado atual do repositório:
- Cobertura de testes: {state.test_coverage}
- Observabilidade: {state.observability}
- Segurança: {state.security}
- Documentação: {state.documentation}

[OBJETIVO DA SPRINT]
{sprint['focus']}

[TAREFAS QUE VOCÊ DEVE EXECUTAR]

"""
        
        # Add objectives as tasks
        for idx, obj in enumerate(sprint['typical_objectives'], 1):
            prompt += f"{idx}. {obj}\n"
        
        # Add deliverables section
        prompt += "\n[ENTREGÁVEIS ESPERADOS]\n\n"
        for deliv in sprint['typical_deliverables']:
            prompt += f"- {deliv}\n"
        
        # Add sprint-specific instructions
        if sprint_number == 1:
            prompt += f"""
[INSTRUÇÕES ESPECÍFICAS]
- Analisar estrutura atual do repositório
- Identificar arquivos desorganizados na raiz
- Propor hierarquia de diretórios apropriada para {state.stack}
- Usar git mv para preservar histórico
- Atualizar todos os imports e referências
- Validar que build/testes continuam funcionando

[RESTRIÇÕES]
- NÃO quebrar funcionalidade existente
- NÃO modificar lógica de negócio
- PRESERVAR histórico do git
- Manter compatibilidade com CI/CD existente
"""
        
        elif sprint_number == 2:
            prompt += f"""
[INSTRUÇÕES ESPECÍFICAS]
- Identificar os 5-7 módulos mais críticos do projeto
- Criar testes unitários abrangentes usando o framework de testes padrão para {state.stack}
- Atingir cobertura mínima de 70%
- Configurar coverage reporting
- Documentar padrões de teste

[RESTRIÇÕES]
- NÃO modificar código de produção (exceto para testabilidade)
- USAR mocks/stubs para dependências externas
- NÃO criar testes que dependam de serviços externos reais
- Tempo de execução < 1 minuto
"""
        
        elif sprint_number == 6:
            prompt += """
[INSTRUÇÕES ESPECÍFICAS]
- Implementar logging estruturado (JSON para prod, console para dev)
- Adicionar request_id para correlação de requisições
- Configurar endpoint /metrics com métricas Prometheus
- Criar middleware de logging automático
- Suportar configuração via variáveis de ambiente

[RESTRIÇÕES]
- NÃO logar dados sensíveis (passwords, tokens)
- NÃO logar health checks
- Performance overhead < 5ms por requisição
- Formato JSON deve ser parseable
"""
        
        elif sprint_number == 7:
            prompt += """
[INSTRUÇÕES ESPECÍFICAS]
- Implementar rate limiting usando algoritmo Token Bucket
- Criar audit logging para ações críticas (login, mudanças de permissão, etc.)
- Implementar/melhorar RBAC com roles apropriados
- Validar que secrets vêm de variáveis de ambiente
- Criar testes de segurança abrangentes (40+ testes)

[RESTRIÇÕES]
- NÃO expor informações sensíveis em erros
- Audit logs NUNCA modificáveis/deletáveis
- RBAC deve ser fail-safe (negar por padrão)
- 0 secrets hardcoded
"""
        
        # Add format and success metrics
        prompt += f"""
[FORMATO DE SAÍDA]
1. Plano de implementação detalhado
2. Código implementado (arquivos completos)
3. Testes criados
4. Documentação atualizada
5. Comandos para validar as mudanças

[MÉTRICAS DE SUCESSO]
- Duração estimada: {sprint['duration']}
- Todos os entregáveis implementados
- Testes passando
- Build funcionando
- Zero regressões
"""
        
        return prompt
    
    def generate_checklist(self) -> str:
        """
        Generate a pre-sprint checklist based on ENG-PLAYBOOK-IA.md
        
        Returns:
            Markdown formatted checklist
        """
        checklist = f"""# Checklist: Pronto para Usar IA neste Repositório

**Repositório:** {self.project_state.repo_url}
**Stack:** {self.project_state.stack}
**Data:** {datetime.now().strftime("%Y-%m-%d")}

---

## 📋 Pré-requisitos Essenciais

### 1. Documentação Básica
- [ ] README existe e descreve claramente o objetivo do projeto
- [ ] README contém instruções de instalação
- [ ] README documenta como executar o projeto localmente
- [ ] LICENSE file presente (se aplicável)

### 2. Ambiente de Desenvolvimento
- [ ] Ambiente de dev é reproduzível (Docker/devcontainer OU instruções claras)
- [ ] Dependências estão documentadas (requirements.txt, package.json, etc.)
- [ ] Variáveis de ambiente necessárias estão documentadas (.env.example)
- [ ] Instruções de setup são testadas e funcionam

### 3. Controle de Versão
- [ ] Repositório Git configurado
- [ ] .gitignore apropriado para o stack
- [ ] Histórico de commits limpo (sem secrets)
- [ ] Branch principal protegida (ou planejamento para isso)

### 4. Testes e Qualidade
- [ ] Framework de testes configurado (pytest, jest, JUnit, etc.)
- [ ] Testes básicos existem e rodam (mesmo que poucos)
- [ ] Comando para executar testes está documentado
- [ ] Testes passam localmente

### 5. CI/CD
- [ ] CI básico configurado (GitHub Actions, GitLab CI, etc.) OU
- [ ] Plano claro para configurar CI na Sprint 4
- [ ] Build automatizado funciona (se aplicável)

### 6. Estrutura de Código
- [ ] Código fonte separado de testes e documentação
- [ ] Estrutura de diretórios é compreensível
- [ ] Convenções de nomenclatura são consistentes
- [ ] Código principal está em um diretório identificável (src/, backend/, etc.)

### 7. Segurança Básica
- [ ] Sem secrets hardcoded no código
- [ ] Configurações sensíveis vêm de variáveis de ambiente
- [ ] .gitignore inclui arquivos sensíveis (.env, credentials, etc.)

### 8. Acessos e Permissões
- [ ] Você tem acesso de escrita ao repositório
- [ ] Você pode criar branches e PRs
- [ ] Você pode configurar/modificar CI/CD

### 9. Backup e Recuperação
- [ ] Código está versionado e com backup (GitHub/GitLab)
- [ ] Existe um ambiente de teste/staging OU
- [ ] Planejamento para criar ambiente de teste

### 10. Conhecimento do Projeto
- [ ] Você entende o propósito geral do projeto
- [ ] Você sabe quais são os módulos/serviços críticos
- [ ] Você tem contato com stakeholders (se necessário)
- [ ] Você conhece as limitações/restrições do projeto

---

## 🚦 Critérios de Pronto

**Mínimo para começar (Sprint 1-2):**
- ✅ Itens 1, 2, 3, 4, 6, 7, 8 completos

**Recomendado para sprints avançadas (Sprint 6+):**
- ✅ TODOS os itens acima completos

---

## 📝 Notas Adicionais

### Estado Atual do Repositório
- **Cobertura de testes:** {self.project_state.test_coverage}
- **Observabilidade:** {self.project_state.observability}
- **Segurança:** {self.project_state.security}
- **Documentação:** {self.project_state.documentation}

### Recomendações
"""
        
        # Add specific recommendations based on state
        if "sem testes" in self.project_state.test_coverage.lower():
            checklist += "\n- ⚠️ **Crítico:** Configure framework de testes antes de Sprint 2"
        
        if "nenhuma" in self.project_state.observability.lower():
            checklist += "\n- 📊 Prepare infraestrutura de logging para Sprint 6"
        
        if "mínima" in self.project_state.security.lower():
            checklist += "\n- 🔐 Revise práticas de segurança antes de Sprint 7"
        
        checklist += """

### Próximos Passos
1. Complete todos os itens marcados como necessários
2. Revise o roadmap de sprints gerado
3. Adapte os prompts para suas necessidades específicas
4. Execute a primeira sprint seguindo o framework

---

**Lembre-se:** Este checklist é baseado nas melhores práticas do AI-SPRINT Framework.
Adaptações podem ser necessárias para seu contexto específico.
"""
        
        return checklist


def generate_output_document(adapter: FrameworkAdapter, output_dir: Path):
    """
    Generate the complete output document with all sections.
    
    Args:
        adapter: FrameworkAdapter instance
        output_dir: Directory to save output files
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate all components
    stage_info = adapter.estimate_current_stage()
    roadmap = adapter.generate_roadmap(num_sprints=6)
    checklist = adapter.generate_checklist()
    
    # Main document
    main_doc = f"""# Aplicação do AI-Sprint Framework ao Repositório

**Repositório Alvo:** {adapter.project_state.repo_url}
**Stack:** {adapter.project_state.stack}
**Data de Análise:** {datetime.now().strftime("%Y-%m-%d %H:%M")}

---

## 📊 1. Estágio Estimado do Repositório

### Análise do Estado Atual

**Estágio Estimado:** {stage_info['estimated_stage']}

**Sprints Recomendadas para Começar:** Sprint {stage_info['recommended_start']}

### Raciocínio da Análise

"""
    
    for reasoning in stage_info['reasoning']:
        main_doc += f"- {reasoning}\n"
    
    if stage_info['completed_sprints']:
        main_doc += f"\n**Sprints Provavelmente Completas:** {', '.join(map(str, sorted(stage_info['completed_sprints'])))}\n"
    
    # Roadmap section
    main_doc += f"""

---

## 🗺️ 2. Roadmap Sugerido de Sprints

Baseado na análise do estado atual, recomendamos as seguintes {len(roadmap)} sprints:

"""
    
    for sprint in roadmap:
        main_doc += f"""### Sprint {sprint.number}: {sprint.name} [Prioridade: {sprint.priority}]

**Foco:** {sprint.focus}

**Duração Estimada:** {sprint.duration}

**Objetivos Principais:**
"""
        for obj in sprint.objectives[:5]:  # Limit to top 5 for readability
            main_doc += f"- {obj}\n"
        
        main_doc += "\n**Principais Entregáveis:**\n"
        for deliv in sprint.deliverables[:5]:  # Limit to top 5
            main_doc += f"- {deliv}\n"
        
        main_doc += "\n"
    
    # Sequence diagram
    main_doc += """### Sequência Recomendada

```
"""
    for i, sprint in enumerate(roadmap, 1):
        arrow = "    ↓" if i < len(roadmap) else ""
        main_doc += f"Sprint {i}: {sprint.name}\n{arrow}\n"
    
    main_doc += "```\n"
    
    # Adapted prompts section
    main_doc += """

---

## 🤖 3. Prompts Adaptados (Prontos para Uso)

Os prompts abaixo estão customizados para seu repositório e podem ser copiados
diretamente para seu assistente de IA (GitHub Copilot, ChatGPT, Claude, etc.).

"""
    
    # Generate prompts for top 3 priority sprints
    priority_sprints = sorted(roadmap, key=lambda x: {"HIGH": 0, "MEDIUM": 1, "LOW": 2}[x.priority])[:3]
    
    for sprint_rec in priority_sprints:
        # Find original sprint number
        original_sprint_num = None
        for num, data in adapter.SPRINT_DEFINITIONS.items():
            if data["name"] == sprint_rec.name:
                original_sprint_num = num
                break
        
        if original_sprint_num:
            prompt = adapter.adapt_prompt(original_sprint_num)
            main_doc += f"""### Prompt para Sprint {sprint_rec.number}: {sprint_rec.name}

```
{prompt}
```

---

"""
    
    # Checklist section
    main_doc += f"""

## ✅ 4. Checklist "Pronto para Usar IA neste Repositório"

{checklist}

---

## 📚 Recursos Adicionais

### Documentos do Framework (neste repositório)
- `docs/arquitetura/AI-SPRINT-FRAMEWORK.md` - Framework completo com 9 sprints
- `docs/arquitetura/AI-SPRINT-PROMPTS.md` - Todos os prompts reutilizáveis
- `docs/arquitetura/ENG-PLAYBOOK-IA.md` - Playbook de engenharia com IA

### Como Usar Este Documento
1. **Revise o estágio estimado** e confirme se faz sentido para seu projeto
2. **Ajuste o roadmap** se necessário (adicionar/remover/reordenar sprints)
3. **Use os prompts adaptados** diretamente com seu assistente de IA
4. **Complete o checklist** antes de iniciar as sprints
5. **Execute uma sprint por vez**, validando resultados antes de prosseguir
6. **Documente seu progresso** criando relatórios de sprint

### Dicas de Sucesso
- ✅ Comece sempre pela Sprint 1 se seu código estiver desorganizado
- ✅ Não pule a fase de testes (Sprints 2-5) - é a base para tudo
- ✅ Valide continuamente: execute testes após cada mudança
- ✅ Documente aprendizados em relatórios de sprint
- ✅ Itere nos prompts se os resultados não forem satisfatórios

---

**Gerado por:** Framework Adapter v1.0
**Baseado em:** 3dPot AI-Sprint Framework (Sprints 1-9)
"""
    
    # Save main document
    main_file = output_dir / "FRAMEWORK-APLICADO.md"
    with open(main_file, 'w', encoding='utf-8') as f:
        f.write(main_doc)
    
    print(f"✅ Documento principal salvo em: {main_file}")
    
    # Save individual prompt files
    prompts_dir = output_dir / "prompts"
    prompts_dir.mkdir(exist_ok=True)
    
    for sprint_rec in priority_sprints:
        original_sprint_num = None
        for num, data in adapter.SPRINT_DEFINITIONS.items():
            if data["name"] == sprint_rec.name:
                original_sprint_num = num
                break
        
        if original_sprint_num:
            prompt = adapter.adapt_prompt(original_sprint_num)
            prompt_file = prompts_dir / f"sprint-{sprint_rec.number}-{sprint_rec.name.lower().replace(' ', '-')}.txt"
            with open(prompt_file, 'w', encoding='utf-8') as f:
                f.write(prompt)
            print(f"✅ Prompt salvo em: {prompt_file}")
    
    print(f"\n🎉 Todos os documentos foram gerados com sucesso em: {output_dir}")
    print(f"\n📖 Próximo passo: Leia {main_file} e comece sua primeira sprint!")


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Framework Adapter - Aplique o AI-Sprint Framework ao seu repositório",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:

  # Modo interativo
  python framework_adapter.py

  # Modo direto com parâmetros
  python framework_adapter.py --repo-url "https://github.com/user/my-project" --stack "Python/FastAPI + PostgreSQL" --objectives "API REST para e-commerce" --test-coverage "30 percent" --observability "logs básicos" --security "JWT básico" --documentation "mínima" --output ./output

Para mais informações, consulte:
  - docs/arquitetura/AI-SPRINT-FRAMEWORK.md
  - docs/arquitetura/AI-SPRINT-PROMPTS.md
  - docs/arquitetura/ENG-PLAYBOOK-IA.md
"""
    )
    
    parser.add_argument('--repo-url', help='URL do repositório alvo')
    parser.add_argument('--stack', help='Stack tecnológico (ex: Python/FastAPI, Node/Express)')
    parser.add_argument('--objectives', help='Objetivos do projeto')
    parser.add_argument('--test-coverage', help='Cobertura de testes atual (ex: 40 percent, sem testes)')
    parser.add_argument('--observability', help='Estado de observabilidade (ex: nenhuma, logs básicos)')
    parser.add_argument('--security', help='Estado de segurança (ex: mínima, JWT básico)')
    parser.add_argument('--documentation', help='Estado de documentação (ex: mínima, moderada)')
    parser.add_argument('--output', default='./framework-output', help='Diretório de saída (padrão: ./framework-output)')
    
    args = parser.parse_args()
    
    # Interactive mode if not all args provided
    if not all([args.repo_url, args.stack, args.objectives, args.test_coverage, 
                args.observability, args.security, args.documentation]):
        print("=" * 70)
        print("Framework Adapter - Aplicação do AI-Sprint Framework")
        print("=" * 70)
        print("\nVocê será guiado para fornecer informações sobre seu repositório alvo.\n")
        
        repo_url = args.repo_url or input("URL do repositório alvo: ").strip()
        stack = args.stack or input("Stack tecnológico (ex: Python/FastAPI, Node/Express): ").strip()
        objectives = args.objectives or input("Objetivos do projeto: ").strip()
        
        print("\nEstado atual do repositório:")
        test_coverage = args.test_coverage or input("  Cobertura de testes (ex: ~40%, sem testes, desconhecida): ").strip()
        observability = args.observability or input("  Observabilidade (ex: nenhuma, logs básicos, avançada): ").strip()
        security = args.security or input("  Segurança (ex: mínima, JWT básico, RBAC + MFA): ").strip()
        documentation = args.documentation or input("  Documentação (ex: mínima, moderada, extensa): ").strip()
        
        output_dir = args.output
    else:
        repo_url = args.repo_url
        stack = args.stack
        objectives = args.objectives
        test_coverage = args.test_coverage
        observability = args.observability
        security = args.security
        documentation = args.documentation
        output_dir = args.output
    
    # Create project state
    project_state = ProjectState(
        repo_url=repo_url,
        stack=stack,
        objectives=objectives,
        test_coverage=test_coverage,
        observability=observability,
        security=security,
        documentation=documentation
    )
    
    # Create adapter and generate output
    print("\n" + "=" * 70)
    print("Analisando repositório e gerando documentos...")
    print("=" * 70 + "\n")
    
    adapter = FrameworkAdapter(project_state)
    generate_output_document(adapter, Path(output_dir))


if __name__ == "__main__":
    main()
