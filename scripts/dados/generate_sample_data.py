#!/usr/bin/env python3
"""
3dPot Workflow Data Generator
Gera dados de exemplo para o dashboard de monitoring
Baseado na estrutura real dos workflows do projeto.
"""

import json
import random
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any


def generate_workflow_run(base_time: datetime, workflow_name: str) -> Dict[str, Any]:
    """Gera um run individual de workflow com dados realistas"""
    
    # Configurações específicas por tipo de workflow
    configs = {
        "CI Pipeline": {
            "duration_range": (120, 480),  # 2-8 minutos
            "success_rate": 0.85,
            "typical_fails": ["dependency_install", "test_timeout", "codecov_upload"]
        },
        "Python Tests": {
            "duration_range": (60, 180),  # 1-3 minutos
            "success_rate": 0.95,
            "typical_fails": ["test_assertion", "import_error", "timeout"]
        },
        "Code Quality": {
            "duration_range": (45, 120),  # 45s-2 minutos
            "success_rate": 0.90,
            "typical_fails": ["format_error", "lint_error", "security_scan"]
        },
        "Arduino Build": {
            "duration_range": (300, 900),  # 5-15 minutos
            "success_rate": 0.75,
            "typical_fails": ["compilation_error", "library_missing", "platform_install"]
        },
        "OpenSCAD 3D Models": {
            "duration_range": (30, 90),  # 30s-1.5 minutos
            "success_rate": 0.98,
            "typical_fails": ["syntax_error", "render_failed"]
        }
    }
    
    config = configs.get(workflow_name, {
        "duration_range": (60, 300),
        "success_rate": 0.80,
        "typical_fails": ["unknown_error"]
    })
    
    # Simular resultado do run
    is_success = random.random() < config["success_rate"]
    conclusion = "success" if is_success else random.choice([
        "failure", "cancelled", "timed_out"
    ])
    
    # Simular duração
    duration = random.randint(*config["duration_range"])
    
    # Simular informações do run
    run_info = {
        "id": random.randint(100000000, 999999999),
        "status": "completed",
        "conclusion": conclusion,
        "created_at": base_time.isoformat(),
        "updated_at": (base_time + timedelta(seconds=duration)).isoformat(),
        "duration_seconds": duration,
        "head_branch": random.choice(["main", "develop", "feature/new-monitor"]),
        "head_sha": ''.join([random.choice('0123456789abcdef') for _ in range(40)]),
        "html_url": f"https://github.com/dronreef2/3dPot/actions/runs/{random.randint(1000000, 9999999)}",
        "display_title": f"{workflow_name} - {random.choice(['Update', 'Fix', 'Add', 'Refactor'])[:20]}",
        "run_number": random.randint(30, 45)
    }
    
    return run_info


def generate_workflow_data(workflow_name: str, file_name: str) -> Dict[str, Any]:
    """Gera dados completos de um workflow"""
    
    # Gerar runs dos últimos dias
    now = datetime.now(timezone.utc)
    runs = []
    success_count = 0
    failure_count = 0
    total_duration = 0
    
    for i in range(10):  # Últimos 10 runs
        run_time = now - timedelta(hours=i*2, minutes=random.randint(0, 59))
        run = generate_workflow_run(run_time, workflow_name)
        runs.append(run)
        
        if run["conclusion"] == "success":
            success_count += 1
        elif run["conclusion"] in ["failure", "cancelled", "timed_out"]:
            failure_count += 1
        
        total_duration += run["duration_seconds"]
    
    # Calcular métricas
    total_runs = len(runs)
    success_rate = (success_count / total_runs) * 100 if total_runs > 0 else 0
    avg_duration = total_duration // total_runs if total_runs > 0 else 0
    
    return {
        "id": random.randint(1000000, 9999999),
        "name": workflow_name,
        "file": f".github/workflows/{file_name}",
        "state": "active",
        "total_runs": total_runs,
        "success_runs": success_count,
        "failure_runs": failure_count,
        "success_rate": round(success_rate, 1),
        "average_duration_seconds": avg_duration,
        "recent_runs": runs
    }


def generate_recommendations(workflows: List[Dict]) -> List[Dict]:
    """Gera recomendações baseadas nos dados dos workflows"""
    recommendations = []
    
    for workflow in workflows:
        # Verificar baixa taxa de sucesso
        if workflow["success_rate"] < 70:
            recommendations.append({
                "type": "reliability",
                "workflow": workflow["name"],
                "issue": f"Taxa de sucesso baixa ({workflow['success_rate']}%)",
                "recommendation": "Investigar falhas frequentes e implementar testes mais robustos"
            })
        
        # Verificar workflow lento
        if workflow["average_duration_seconds"] > 300:  # 5 minutos
            recommendations.append({
                "type": "performance",
                "workflow": workflow["name"],
                "issue": f"Duração média alta ({workflow['average_duration_seconds']}s)",
                "recommendation": "Implementar cache de dependências e paralelização"
            })
        
        # Verificar banyak falhas
        if workflow["failure_runs"] > workflow["success_runs"]:
            recommendations.append({
                "type": "reliability",
                "workflow": workflow["name"],
                "issue": f"Mais falhas que sucessos ({workflow['failure_runs']} vs {workflow['success_runs']})",
                "recommendation": "Priorizar correção dos testes e validação de código"
            })
    
    return recommendations


def generate_performance_metrics(workflows: List[Dict]) -> Dict[str, Any]:
    """Gera métricas de performance consolidadas"""
    
    if not workflows:
        return {}
    
    # Calcular métricas gerais
    total_workflows = len(workflows)
    healthy_workflows = sum(1 for w in workflows if w["success_rate"] >= 80)
    unhealthy_workflows = total_workflows - healthy_workflows
    average_success_rate = sum(w["success_rate"] for w in workflows) / total_workflows
    total_runs_analyzed = sum(w["total_runs"] for w in workflows)
    
    # Identificar melhor e pior performance
    workflows_with_runs = [w for w in workflows if w["total_runs"] > 0]
    
    performance = {}
    if workflows_with_runs:
        fastest = min(workflows_with_runs, key=lambda w: w["average_duration_seconds"])
        slowest = max(workflows_with_runs, key=lambda w: w["average_duration_seconds"])
        most_reliable = max(workflows_with_runs, key=lambda w: w["success_rate"])
        least_reliable = min(workflows_with_runs, key=lambda w: w["success_rate"])
        
        performance = {
            "fastest_workflow": {
                "name": fastest["name"],
                "average_duration": fastest["average_duration_seconds"]
            },
            "slowest_workflow": {
                "name": slowest["name"],
                "average_duration": slowest["average_duration_seconds"]
            },
            "most_reliable_workflow": {
                "name": most_reliable["name"],
                "success_rate": most_reliable["success_rate"]
            },
            "least_reliable_workflow": {
                "name": least_reliable["name"],
                "success_rate": least_reliable["success_rate"]
            }
        }
    
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "repository": "dronreef2/3dPot",
        "summary": {
            "total_workflows": total_workflows,
            "healthy_workflows": healthy_workflows,
            "unhealthy_workflows": unhealthy_workflows,
            "average_success_rate": round(average_success_rate, 1),
            "total_runs_analyzed": total_runs_analyzed
        },
        "performance": performance
    }


def main():
    """Gera dados de exemplo para o dashboard"""
    
    # Definir workflows
    workflows_config = [
        {"name": "CI Pipeline", "file": "ci.yml"},
        {"name": "Python Tests", "file": "python-tests.yml"},
        {"name": "Code Quality", "file": "code-quality.yml"},
        {"name": "Arduino Build", "file": "arduino-build.yml"},
        {"name": "OpenSCAD 3D Models", "file": "openscad.yml"}
    ]
    
    # Gerar dados dos workflows
    workflows = []
    for config in workflows_config:
        workflow_data = generate_workflow_data(config["name"], config["file"])
        workflows.append(workflow_data)
    
    # Gerar dados consolidados
    summary = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "repository": "dronreef2/3dPot",
        "total_workflows": len(workflows),
        "workflows": workflows
    }
    
    # Gerar métricas de performance
    metrics = generate_performance_metrics(workflows)
    recommendations = generate_recommendations(workflows)
    metrics["recommendations"] = recommendations
    
    # Criar dados finais
    output_data = {
        "summary": summary,
        "metrics": metrics
    }
    
    # Salvar em arquivo JSON
    output_file = "workflows_status.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Dados de exemplo gerados com sucesso!")
    print(f"📁 Arquivo: {output_file}")
    print(f"📊 Workflows: {len(workflows)}")
    print(f"💡 Recomendações: {len(recommendations)}")
    
    # Exibir resumo
    print(f"\n📈 Resumo dos Workflows:")
    for workflow in workflows:
        print(f"  • {workflow['name']}: {workflow['success_rate']}% "
              f"({workflow['success_runs']}/{workflow['total_runs']}) - "
              f"Avg: {workflow['average_duration_seconds']}s")
    
    if recommendations:
        print(f"\n💡 Recomendações:")
        for rec in recommendations:
            print(f"  • {rec['workflow']}: {rec['recommendation']}")


if __name__ == "__main__":
    main()