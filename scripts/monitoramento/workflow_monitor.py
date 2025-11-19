#!/usr/bin/env python3
"""
3dPot Workflow Monitor
Script para consultar o status dos workflows do GitHub Actions
e gerar dados para o dashboard de monitoring.
"""

import json
import os
import sys
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import argparse

try:
    import requests
except ImportError:
    print("❌ Error: requests library not found. Install with: pip install requests")
    sys.exit(1)


class GitHubWorkflowMonitor:
    """Monitor para workflows do GitHub Actions"""
    
    def __init__(self, token: str, owner: str, repo: str):
        self.token = token
        self.owner = owner
        self.repo = repo
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "3dPot-Workflow-Monitor"
        }
    
    def get_workflows(self) -> List[Dict[str, Any]]:
        """Obtém a lista de todos os workflows"""
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/actions/workflows"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            return data.get("workflows", [])
        except requests.RequestException as e:
            print(f"❌ Error fetching workflows: {e}")
            return []
    
    def get_workflow_runs(self, workflow_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Obtém os runs de um workflow específico"""
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/actions/workflows/{workflow_id}/runs"
        params = {"per_page": limit, "page": 1}
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("workflow_runs", [])
        except requests.RequestException as e:
            print(f"❌ Error fetching workflow runs for {workflow_id}: {e}")
            return []
    
    def get_workflow_run_duration(self, run: Dict[str, Any]) -> int:
        """Calcula a duração de um run em segundos"""
        created_at = run.get("created_at")
        updated_at = run.get("updated_at")
        
        if not created_at or not updated_at:
            return 0
        
        try:
            created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            updated = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
            return int((updated - created).total_seconds())
        except:
            return 0
    
    def get_workflow_status_summary(self) -> Dict[str, Any]:
        """Gera um resumo completo do status dos workflows"""
        workflows = self.get_workflows()
        summary = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "repository": f"{self.owner}/{self.repo}",
            "total_workflows": len(workflows),
            "workflows": []
        }
        
        for workflow in workflows:
            workflow_id = workflow.get("id")
            workflow_name = workflow.get("name", "Unknown")
            workflow_file = workflow.get("path", "")
            
            runs = self.get_workflow_runs(str(workflow_id), limit=10)
            
            # Análise dos últimos runs
            recent_runs = []
            success_count = 0
            failure_count = 0
            total_duration = 0
            
            for run in runs:
                run_status = run.get("status", "unknown")
                run_conclusion = run.get("conclusion", "unknown")
                duration = self.get_workflow_run_duration(run)
                total_duration += duration
                
                if run_conclusion == "success":
                    success_count += 1
                elif run_conclusion in ["failure", "cancelled", "timed_out"]:
                    failure_count += 1
                
                run_info = {
                    "id": run.get("id"),
                    "status": run_status,
                    "conclusion": run_conclusion,
                    "created_at": run.get("created_at"),
                    "updated_at": run.get("updated_at"),
                    "duration_seconds": duration,
                    "head_branch": run.get("head_branch"),
                    "head_sha": run.get("head_sha")[:8] if run.get("head_sha") else "",
                    "html_url": run.get("html_url"),
                    "display_title": run.get("display_title", ""),
                    "run_number": run.get("run_number")
                }
                recent_runs.append(run_info)
            
            # Cálculo da média de duração
            avg_duration = total_duration // len(runs) if runs else 0
            
            workflow_summary = {
                "id": workflow_id,
                "name": workflow_name,
                "file": workflow_file,
                "state": workflow.get("state", "active"),
                "total_runs": len(runs),
                "success_runs": success_count,
                "failure_runs": failure_count,
                "success_rate": round((success_count / len(runs)) * 100, 1) if runs else 0,
                "average_duration_seconds": avg_duration,
                "recent_runs": recent_runs
            }
            
            summary["workflows"].append(workflow_summary)
        
        return summary
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Gera métricas de performance dos workflows"""
        summary = self.get_workflow_status_summary()
        
        metrics = {
            "timestamp": summary["timestamp"],
            "repository": summary["repository"],
            "summary": {
                "total_workflows": summary["total_workflows"],
                "healthy_workflows": 0,
                "unhealthy_workflows": 0,
                "average_success_rate": 0,
                "total_runs_analyzed": 0
            },
            "performance": {
                "fastest_workflow": None,
                "slowest_workflow": None,
                "most_reliable_workflow": None,
                "least_reliable_workflow": None
            },
            "recommendations": []
        }
        
        if not summary["workflows"]:
            return metrics
        
        # Calcular métricas gerais
        total_workflows = len(summary["workflows"])
        total_success_rates = []
        total_runs = 0
        
        for workflow in summary["workflows"]:
            if workflow["success_rate"] >= 80:
                metrics["summary"]["healthy_workflows"] += 1
            else:
                metrics["summary"]["unhealthy_workflows"] += 1
            
            total_success_rates.append(workflow["success_rate"])
            total_runs += workflow["total_runs"]
        
        metrics["summary"]["average_success_rate"] = round(
            sum(total_success_rates) / len(total_success_rates), 1
        ) if total_success_rates else 0
        metrics["summary"]["total_runs_analyzed"] = total_runs
        
        # Identificar melhor e pior performance
        workflows_with_runs = [w for w in summary["workflows"] if w["total_runs"] > 0]
        
        if workflows_with_runs:
            # Workflow mais rápido
            fastest = min(workflows_with_runs, key=lambda w: w["average_duration_seconds"])
            metrics["performance"]["fastest_workflow"] = {
                "name": fastest["name"],
                "average_duration": fastest["average_duration_seconds"]
            }
            
            # Workflow mais lento
            slowest = max(workflows_with_runs, key=lambda w: w["average_duration_seconds"])
            metrics["performance"]["slowest_workflow"] = {
                "name": slowest["name"],
                "average_duration": slowest["average_duration_seconds"]
            }
            
            # Workflow mais confiável
            most_reliable = max(workflows_with_runs, key=lambda w: w["success_rate"])
            metrics["performance"]["most_reliable_workflow"] = {
                "name": most_reliable["name"],
                "success_rate": most_reliable["success_rate"]
            }
            
            # Workflow menos confiável
            least_reliable = min(workflows_with_runs, key=lambda w: w["success_rate"])
            metrics["performance"]["least_reliable_workflow"] = {
                "name": least_reliable["name"],
                "success_rate": least_reliable["success_rate"]
            }
        
        # Gerar recomendações
        self._generate_recommendations(metrics, summary)
        
        return metrics
    
    def _generate_recommendations(self, metrics: Dict, summary: Dict):
        """Gera recomendações baseadas na análise dos dados"""
        recommendations = []
        
        # Verificar workflows com baixa taxa de sucesso
        for workflow in summary["workflows"]:
            if workflow["success_rate"] < 70:
                recommendations.append({
                    "type": "reliability",
                    "workflow": workflow["name"],
                    "issue": f"Taxa de sucesso baixa ({workflow['success_rate']}%)",
                    "recommendation": "Investigar falhas frequentes e implementar testes mais robustos"
                })
        
        # Verificar workflows lentos
        for workflow in summary["workflows"]:
            if workflow["average_duration_seconds"] > 300:  # 5 minutos
                recommendations.append({
                    "type": "performance",
                    "workflow": workflow["name"],
                    "issue": f"Duração média alta ({workflow['average_duration_seconds']}s)",
                    "recommendation": "Implementar cache de dependências e paralelização"
                })
        
        # Verificar se há workflows não executados recentemente
        for workflow in summary["workflows"]:
            if workflow["total_runs"] == 0:
                recommendations.append({
                    "type": "configuration",
                    "workflow": workflow["name"],
                    "issue": "Workflow não foi executado recentemente",
                    "recommendation": "Verificar triggers de workflow e configuração de branches"
                })
        
        metrics["recommendations"] = recommendations


def format_duration(seconds: int) -> str:
    """Formata duração em segundos para formato legível"""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        return f"{minutes}m {remaining_seconds}s"
    else:
        hours = seconds // 3600
        remaining_minutes = (seconds % 3600) // 60
        return f"{hours}h {remaining_minutes}m"


def main():
    parser = argparse.ArgumentParser(description="3dPot Workflow Monitor")
    parser.add_argument("--token", required=True, help="GitHub Personal Access Token")
    parser.add_argument("--owner", required=True, help="Repository owner")
    parser.add_argument("--repo", required=True, help="Repository name")
    parser.add_argument("--output", help="Output JSON file path", default="workflows_status.json")
    parser.add_argument("--format", choices=["json", "summary"], default="summary",
                       help="Output format")
    
    args = parser.parse_args()
    
    # Criar monitor
    monitor = GitHubWorkflowMonitor(args.token, args.owner, args.repo)
    
    # Obter dados
    if args.format == "summary":
        print("🔍 Collecting workflow data...")
        data = monitor.get_workflow_status_summary()
        metrics = monitor.get_performance_metrics()
        
        # Exibir resumo
        print(f"\n📊 3dPot Workflow Status Summary")
        print(f"Repository: {data['repository']}")
        print(f"Timestamp: {data['timestamp']}")
        print(f"Total Workflows: {data['total_workflows']}")
        print(f"Healthy Workflows: {metrics['summary']['healthy_workflows']}")
        print(f"Success Rate: {metrics['summary']['average_success_rate']}%")
        
        print(f"\n📈 Individual Workflow Status:")
        for workflow in data["workflows"]:
            status_emoji = "✅" if workflow["success_rate"] >= 80 else "⚠️" if workflow["success_rate"] >= 50 else "❌"
            print(f"  {status_emoji} {workflow['name']}: {workflow['success_rate']}% "
                  f"({workflow['success_runs']}/{workflow['total_runs']}) - "
                  f"Avg: {format_duration(workflow['average_duration_seconds'])}")
        
        print(f"\n💡 Recommendations:")
        for rec in metrics["recommendations"][:5]:  # Mostrar apenas as primeiras 5
            print(f"  • {rec['workflow']}: {rec['recommendation']}")
        
        # Salvar dados completos
        output_data = {
            "summary": data,
            "metrics": metrics
        }
        
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Detailed data saved to: {args.output}")
        
    else:
        # Formato JSON completo
        data = monitor.get_workflow_status_summary()
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"JSON data saved to: {args.output}")


if __name__ == "__main__":
    main()