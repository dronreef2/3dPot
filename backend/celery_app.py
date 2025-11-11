"""
Aplicação Celery para Processamento Assíncrono de Simulações
Tasks para executar simulações em background
"""

import os
import logging
from celery import Celery
from kombu import Queue
import uuid
from datetime import datetime, timedelta

# Configuração do Celery
CELERY_BROKER_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

# Criar aplicação Celery
celery_app = Celery(
    'simulation_tasks',
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=['backend.celery_app']
)

# Configurações do Celery
celery_app.conf.update(
    # Configurações de task
    task_serializer='pickle',
    accept_content=['pickle'],
    result_serializer='pickle',
    timezone='UTC',
    enable_utc=True,
    
    # Configurações de retry
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    
    # Configurações de rota
    task_routes={
        'backend.celery_app.run_simulation_task': {'queue': 'simulations'},
        'backend.celery_app.cancel_simulation_task': {'queue': 'simulations'},
        'backend.celery_app.cleanup_simulation_cache': {'queue': 'maintenance'},
    },
    
    # Configurações de fila
    task_default_queue='default',
    task_queues=(
        Queue('default'),
        Queue('simulations', routing_key='simulation.#'),
        Queue('maintenance', routing_key='maintenance.#'),
    ),
    
    # Configurações de timeout
    task_soft_time_limit=1800,  # 30 minutos
    task_time_limit=2100,       # 35 minutos (hard limit)
    
    # Configurações de retry
    task_annotations={
        'run_simulation_task': {
            'rate_limit': '5/m',  # Máximo 5 simulações por minuto por worker
            'time_limit': 2100,
            'soft_time_limit': 1800,
        },
        'cancel_simulation_task': {
            'rate_limit': '10/m',
        }
    },
    
    # Configurações de resultado
    result_expires=3600,  # Resultados expiram em 1 hora
    worker_send_task_events=False,
    task_send_sent_event=False,
)

logger = logging.getLogger(__name__)

# ========== TASKS DE SIMULAÇÃO ==========

@celery_app.task(bind=True, name='run_simulation_task')
def run_simulation_task(self, simulation_id: str, model_path: str, simulation_data: dict):
    """
    Task principal para executar simulação física
    
    Args:
        simulation_id: ID da simulação
        model_path: Caminho para o arquivo do modelo 3D
        simulation_data: Dados da simulação
    """
    try:
        logger.info(f"Iniciando simulação {simulation_id}")
        
        # Atualizar status da simulação
        update_simulation_status(simulation_id, "running", progress=10)
        
        # Importar serviço de simulação
        from backend.services.simulation_service import SimulationService
        from backend.core.database import SessionLocal
        from backend.models import Simulation, Model3D
        
        # Criar sessão do banco
        db = SessionLocal()
        
        try:
            # Atualizar progresso
            update_simulation_status(simulation_id, "running", progress=20)
            
            # Obter simulação do banco
            simulation = db.query(Simulation).filter(Simulation.id == simulation_id).first()
            if not simulation:
                raise ValueError(f"Simulação {simulation_id} não encontrada")
            
            # Atualizar informações de execução
            simulation.celery_task_id = self.request.id
            simulation.started_at = datetime.utcnow()
            simulation.status = "running"
            simulation.progress = 25
            db.commit()
            
            # Executar simulação
            simulation_service = SimulationService()
            result = simulation_service.execute_simulation_async(
                simulation_id=simulation_id,
                model_path=model_path,
                simulation_data=simulation_data
            )
            
            # Atualizar progresso
            update_simulation_status(simulation_id, "running", progress=80)
            
            if result.get("status") == "completed":
                # Salvar resultados
                simulation.results = result
                simulation.status = "completed"
                simulation.progress = 100
                simulation.completed_at = datetime.utcnow()
                
                # Calcular métricas
                calculate_and_save_metrics(simulation, result, db)
                
                db.commit()
                logger.info(f"Simulação {simulation_id} concluída com sucesso")
                
            else:
                # Simulação falhou
                simulation.status = "failed"
                simulation.error_message = result.get("error", "Erro desconhecido")
                simulation.completed_at = datetime.utcnow()
                db.commit()
                logger.error(f"Simulação {simulation_id} falhou: {simulation.error_message}")
                
        finally:
            db.close()
        
        return {
            "simulation_id": simulation_id,
            "status": "completed",
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Erro na tarefa de simulação {simulation_id}: {e}")
        
        # Atualizar status de erro
        try:
            update_simulation_status(simulation_id, "failed", error_message=str(e))
        except Exception as update_error:
            logger.error(f"Erro ao atualizar status: {update_error}")
        
        # Re-lançar exceção para Celery
        raise

@celery_app.task(name='cancel_simulation_task')
def cancel_simulation_task(simulation_id: str):
    """
    Task para cancelar simulação em andamento
    
    Args:
        simulation_id: ID da simulação
    """
    try:
        logger.info(f"Cancelando simulação {simulation_id}")
        
        from backend.core.database import SessionLocal
        from backend.models import Simulation
        
        db = SessionLocal()
        try:
            simulation = db.query(Simulation).filter(Simulation.id == simulation_id).first()
            if simulation:
                simulation.status = "cancelled"
                simulation.is_cancelled = True
                simulation.completed_at = datetime.utcnow()
                db.commit()
                logger.info(f"Simulação {simulation_id} cancelada com sucesso")
            else:
                logger.warning(f"Simulação {simulation_id} não encontrada para cancelamento")
                
        finally:
            db.close()
        
        return {"status": "cancelled", "simulation_id": simulation_id}
        
    except Exception as e:
        logger.error(f"Erro ao cancelar simulação {simulation_id}: {e}")
        raise

# ========== TASKS DE MANUTENÇÃO ==========

@celery_app.task(name='cleanup_simulation_cache')
def cleanup_simulation_cache():
    """
    Task para limpeza de cache expirado
    """
    try:
        logger.info("Iniciando limpeza de cache de simulações")
        
        from backend.services.simulation_service import SimulationService
        
        simulation_service = SimulationService()
        if simulation_service.redis_client:
            # Remover chaves expiradas
            cleaned_keys = simulation_service.redis_client.keys("simulation:*")
            expired_count = 0
            
            for key in cleaned_keys:
                ttl = simulation_service.redis_client.ttl(key)
                if ttl <= 0:
                    simulation_service.redis_client.delete(key)
                    expired_count += 1
            
            logger.info(f"Limpeza concluída: {expired_count} chaves removidas")
            return {"cleaned_keys": expired_count}
        else:
            logger.warning("Redis não disponível para limpeza")
            return {"cleaned_keys": 0}
            
    except Exception as e:
        logger.error(f"Erro na limpeza de cache: {e}")
        raise

@celery_app.task(name='cleanup_old_simulations')
def cleanup_old_simulations():
    """
    Task para limpeza de simulações antigas
    Remove simulações com mais de 30 dias
    """
    try:
        logger.info("Iniciando limpeza de simulações antigas")
        
        from backend.core.database import SessionLocal
        from backend.models import Simulation
        
        db = SessionLocal()
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=30)
            
            # Encontrar simulações antigas completadas
            old_simulations = db.query(Simulation).filter(
                Simulation.status.in_(["completed", "failed"]),
                Simulation.completed_at < cutoff_date
            ).all()
            
            deleted_count = 0
            for simulation in old_simulations:
                # Remover também os logs de execução
                from backend.models import SimulationExecutionLog
                logs = db.query(SimulationExecutionLog).filter(
                    SimulationExecutionLog.simulation_id == simulation.id
                ).all()
                
                for log in logs:
                    db.delete(log)
                
                # Remover simulação
                db.delete(simulation)
                deleted_count += 1
            
            db.commit()
            logger.info(f"Limpeza concluída: {deleted_count} simulações removidas")
            return {"deleted_simulations": deleted_count}
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Erro na limpeza de simulações: {e}")
        raise

# ========== TASKS DE MONITORAMENTO ==========

@celery_app.task(name='monitor_simulation_health')
def monitor_simulation_health():
    """
    Task para monitorar saúde das simulações
    Verifica simulações que estão rodando há muito tempo
    """
    try:
        from backend.core.database import SessionLocal
        from backend.models import Simulation
        
        db = SessionLocal()
        try:
            # Verificar simulações que estão rodando há mais de 30 minutos
            stale_threshold = datetime.utcnow() - timedelta(minutes=30)
            stale_simulations = db.query(Simulation).filter(
                Simulation.status == "running",
                Simulation.started_at < stale_threshold
            ).all()
            
            stale_count = 0
            for simulation in stale_simulations:
                # Marcar como falha se passaram mais de 45 minutos
                if simulation.started_at < (datetime.utcnow() - timedelta(minutes=45)):
                    simulation.status = "failed"
                    simulation.error_message = "Timeout na execução"
                    simulation.completed_at = datetime.utcnow()
                    stale_count += 1
            
            db.commit()
            
            if stale_count > 0:
                logger.warning(f"Monitoramento: {stale_count} simulações marcadas como timeout")
            
            return {"stale_simulations": stale_count}
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Erro no monitoramento: {e}")
        raise

# ========== FUNÇÕES AUXILIARES ==========

def update_simulation_status(simulation_id: str, status: str, progress: float = None, 
                           error_message: str = None):
    """
    Atualizar status da simulação no banco de dados
    
    Args:
        simulation_id: ID da simulação
        status: Novo status
        progress: Progresso (0-100)
        error_message: Mensagem de erro
    """
    try:
        from backend.core.database import SessionLocal
        from backend.models import Simulation
        
        db = SessionLocal()
        try:
            simulation = db.query(Simulation).filter(Simulation.id == simulation_id).first()
            if simulation:
                simulation.status = status
                if progress is not None:
                    simulation.progress = progress
                if error_message:
                    simulation.error_message = error_message
                simulation.updated_at = datetime.utcnow()
                db.commit()
            else:
                logger.warning(f"Simulação {simulation_id} não encontrada para atualização")
                
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Erro ao atualizar status da simulação {simulation_id}: {e}")

def calculate_and_save_metrics(simulation, result: dict, db):
    """
    Calcular e salvar métricas da simulação
    """
    try:
        if not result or result.get("status") != "completed":
            return
        
        metrics = {}
        sim_type = result.get("tipo")
        
        if sim_type == "drop_test":
            metrics = calculate_drop_test_metrics(result)
        elif sim_type == "stress_test":
            metrics = calculate_stress_test_metrics(result)
        elif sim_type == "motion":
            metrics = calculate_motion_test_metrics(result)
        elif sim_type == "fluid":
            metrics = calculate_fluid_test_metrics(result)
        
        # Salvar métricas na simulação
        simulation.metrics = metrics
        simulation.progress = 100
        
    except Exception as e:
        logger.error(f"Erro ao calcular métricas: {e}")

def calculate_drop_test_metrics(result: dict) -> dict:
    """Calcular métricas específicas do teste de queda"""
    try:
        testes = result.get("testes", [])
        if not testes:
            return {}
        
        # Calcular estatísticas básicas
        velocidades_impacto = [t.get("velocidade_impacto", 0) for t in testes]
        rebotes = [t.get("rebotes", 0) for t in testes]
        
        metrics = {
            "velocidade_impacto_media": sum(velocidades_impacto) / len(velocidades_impacto),
            "velocidade_impacto_max": max(velocidades_impacto) if velocidades_impacto else 0,
            "velocidade_impacto_min": min(velocidades_impacto) if velocidades_impacto else 0,
            "rebotes_medio": sum(rebotes) / len(rebotes) if rebotes else 0,
            "numero_testes": len(testes),
            "classificacao_resistencia": classify_drop_resistance(velocidades_impacto, rebotes)
        }
        
        return metrics
        
    except Exception as e:
        logger.error(f"Erro ao calcular métricas de queda: {e}")
        return {}

def calculate_stress_test_metrics(result: dict) -> dict:
    """Calcular métricas específicas do teste de stress"""
    try:
        testes = result.get("testes_forca", [])
        if not testes:
            return {}
        
        forcas = [t.get("forca", 0) for t in testes]
        deslocamentos = [t.get("deslocamento", 0) for t in testes]
        
        # Calcular rigidez (força/deslocamento)
        rigidez = 0
        if len(testes) > 1 and deslocamentos[-1] > 0:
            rigidez = forcas[-1] / deslocamentos[-1]
        
        metrics = {
            "forca_maxima": max(forcas) if forcas else 0,
            "deslocamento_maximo": max(deslocamentos) if deslocamentos else 0,
            "rigidez_calculada": rigidez,
            "ponto_ruptura": result.get("ponto_ruptura"),
            "classificacao_resistencia": classify_stress_resistance(max(forcas) if forcas else 0)
        }
        
        return metrics
        
    except Exception as e:
        logger.error(f"Erro ao calcular métricas de stress: {e}")
        return {}

def calculate_motion_test_metrics(result: dict) -> dict:
    """Calcular métricas específicas do teste de movimento"""
    try:
        trajetoria = result.get("trajetoria", [])
        if not trajetoria:
            return {}
        
        # Calcular energia total
        energia_total = sum(point.get("energia_potencial", 0) for point in trajetoria)
        
        metrics = {
            "energia_total": energia_total,
            "numero_pontos": len(trajetoria),
            "estabilidade": "estável"  # Simplificado
        }
        
        return metrics
        
    except Exception as e:
        logger.error(f"Erro ao calcular métricas de movimento: {e}")
        return {}

def calculate_fluid_test_metrics(result: dict) -> dict:
    """Calcular métricas específicas do teste de fluido"""
    try:
        resistencia = result.get("resistencia", [])
        metrics = result.get("metricas", {})
        
        # Adicionar classificação
        velocidade_terminal = metrics.get("velocidade_terminal", 0)
        coeficiente_arrasto = metrics.get("coeficiente_arrasto", 0.47)
        
        metrics["classificacao_aerodinamica"] = classify_aerodynamics(
            velocidade_terminal, coeficiente_arrasto
        )
        
        return metrics
        
    except Exception as e:
        logger.error(f"Erro ao calcular métricas de fluido: {e}")
        return {}

# ========== FUNÇÕES DE CLASSIFICAÇÃO ==========

def classify_drop_resistance(velocidades: list, rebotes: list) -> str:
    """Classificar resistência baseado nos testes de queda"""
    if not velocidades:
        return "indefinido"
    
    vel_media = sum(velocidades) / len(velocidades)
    rebotes_medio = sum(rebotes) / len(rebotes) if rebotes else 0
    
    if vel_media < 3.0 and rebotes_medio < 1.0:
        return "resistente"
    elif vel_media < 5.0 and rebotes_medio < 2.0:
        return "moderado"
    else:
        return "frágil"

def classify_stress_resistance(max_force: float) -> str:
    """Classificar resistência baseado no teste de stress"""
    if max_force > 5000:
        return "muito_resistente"
    elif max_force > 2000:
        return "resistente"
    elif max_force > 500:
        return "moderado"
    else:
        return "frágil"

def classify_aerodynamics(vel_terminal: float, coeficiente_arrasto: float) -> str:
    """Classificar aerodinâmica baseado no teste de fluido"""
    if vel_terminal < 5.0 and coeficiente_arrasto < 0.3:
        return "aerodinâmico"
    elif vel_terminal < 10.0 and coeficiente_arrasto < 0.5:
        return "moderado"
    else:
        return "arrasto_alto"

# ========== COMANDOS PARA WORKER ==========

@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    """
    Configurar tarefas periódicas
    """
    # Limpeza de cache a cada hora
    sender.add_periodic_task(3600.0, cleanup_simulation_cache.s())
    
    # Limpeza de simulações antigas a cada dia
    sender.add_periodic_task(86400.0, cleanup_old_simulations.s())
    
    # Monitoramento de saúde a cada 10 minutos
    sender.add_periodic_task(600.0, monitor_simulation_health.s())

if __name__ == '__main__':
    celery_app.start()