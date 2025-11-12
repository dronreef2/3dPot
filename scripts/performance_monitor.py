#!/usr/bin/env python3
"""
Performance Monitoring Script for 3D Pot Platform - Sprint 7
Monitora métricas críticas de performance e geração de alertas
"""

import asyncio
import aiohttp
import asyncio_mqtt
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from prometheus_client import start_http_server, Gauge, Counter, Histogram
import redis
import psycopg2
from sqlalchemy import create_engine
import docker
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Estrutura para armazenar métricas de performance"""
    timestamp: datetime
    api_response_time: float
    database_query_time: float
    memory_usage: float
    cpu_usage: float
    active_connections: int
    error_rate: float
    throughput: float

class PrometheusMetrics:
    """Métricas Prometheus para monitoramento"""
    
    # API Metrics
    api_response_time = Histogram('api_response_time_seconds', 'API response time in seconds',
                                 ['endpoint', 'method', 'status_code'])
    api_requests_total = Counter('api_requests_total', 'Total API requests',
                                ['endpoint', 'method', 'status_code'])
    api_errors_total = Counter('api_errors_total', 'Total API errors',
                              ['endpoint', 'error_type'])
    
    # Database Metrics
    db_connection_pool_in_use = Gauge('db_connections_in_use', 'Database connections in use')
    db_connection_pool_max = Gauge('db_connections_max', 'Max database connections')
    db_query_duration = Histogram('db_query_duration_seconds', 'Database query duration',
                                 ['query_type'])
    
    # Application Metrics
    active_sessions = Gauge('active_sessions_total', 'Total active user sessions')
    memory_usage_bytes = Gauge('memory_usage_bytes', 'Memory usage in bytes')
    cpu_usage_percent = Gauge('cpu_usage_percent', 'CPU usage percentage')
    disk_usage_percent = Gauge('disk_usage_percent', 'Disk usage percentage')
    
    # Business Metrics
    conversations_active = Gauge('conversations_active', 'Active conversations')
    models_generating = Gauge('models_generating', 'Models currently generating')
    print_jobs_active = Gauge('print_jobs_active', 'Active print jobs')
    renders_queue_size = Gauge('renders_queue_size', 'Cloud rendering queue size')
    
    # WebSocket Metrics
    websocket_connections = Gauge('websocket_connections_total', 'Active WebSocket connections')
    websocket_messages_per_second = Counter('websocket_messages_total', 'WebSocket messages total',
                                           ['message_type'])

class PerformanceMonitor:
    """Monitor principal de performance da plataforma"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.api_base_url = config['api_base_url']
        self.db_url = config['database_url']
        self.redis_url = config['redis_url']
        self.alert_thresholds = config.get('alert_thresholds', {})
        
        # Initialize connections
        self.engine = create_engine(self.db_url)
        self.redis_client = redis.from_url(self.redis_url)
        
        # Initialize Docker client
        self.docker_client = docker.from_env()
        
        # Metrics
        self.metrics = PrometheusMetrics()
        
        # Monitoring intervals
        self.monitoring_intervals = {
            'api_health': 30,      # 30 seconds
            'database_perf': 60,   # 1 minute
            'system_metrics': 60,  # 1 minute
            'business_metrics': 120, # 2 minutes
            'docker_stats': 180    # 3 minutes
        }
    
    async def monitor_api_health(self):
        """Monitora saúde da API em tempo real"""
        while True:
            try:
                endpoints = [
                    {'path': '/health', 'method': 'GET'},
                    {'path': '/api/projects', 'method': 'GET'},
                    {'path': '/api/conversations', 'method': 'POST'},
                    {'path': '/api/modeling/generate', 'method': 'POST'},
                    {'path': '/api/printing/jobs', 'method': 'POST'},
                    {'path': '/ws', 'method': 'WEBSOCKET'}
                ]
                
                for endpoint in endpoints:
                    start_time = time.time()
                    
                    try:
                        async with aiohttp.ClientSession() as session:
                            if endpoint['method'] == 'GET':
                                async with session.get(
                                    f"{self.api_base_url}{endpoint['path']}",
                                    timeout=aiohttp.ClientTimeout(total=10)
                                ) as response:
                                    duration = time.time() - start_time
                                    status_code = response.status
                                    
                            elif endpoint['method'] == 'POST':
                                async with session.post(
                                    f"{self.api_base_url}{endpoint['path']}",
                                    json={'test': True},
                                    timeout=aiohttp.ClientTimeout(total=30)
                                ) as response:
                                    duration = time.time() - start_time
                                    status_code = response.status
                                    
                            # Record metrics
                            self.metrics.api_response_time.labels(
                                endpoint=endpoint['path'],
                                method=endpoint['method'],
                                status_code=status_code
                            ).observe(duration)
                            
                            self.metrics.api_requests_total.labels(
                                endpoint=endpoint['path'],
                                method=endpoint['method'],
                                status_code=status_code
                            ).inc()
                            
                            if status_code >= 400:
                                self.metrics.api_errors_total.labels(
                                    endpoint=endpoint['path'],
                                    error_type=f"status_{status_code}"
                                ).inc()
                    
                    except Exception as e:
                        duration = time.time() - start_time
                        logger.error(f"API health check failed for {endpoint['path']}: {e}")
                        
                        self.metrics.api_errors_total.labels(
                            endpoint=endpoint['path'],
                            error_type="timeout_or_connection_error"
                        ).inc()
                
                await asyncio.sleep(self.monitoring_intervals['api_health'])
                
            except Exception as e:
                logger.error(f"API health monitoring error: {e}")
                await asyncio.sleep(10)
    
    async def monitor_database_performance(self):
        """Monitora performance do banco de dados"""
        while True:
            try:
                # Test basic connectivity
                start_time = time.time()
                with self.engine.connect() as conn:
                    conn.execute("SELECT 1")
                    db_response_time = time.time() - start_time
                
                self.metrics.db_query_duration.labels(query_type='health_check').observe(db_response_time)
                
                # Get connection pool stats
                pool = self.engine.pool
                in_use = pool.checkedout()
                max_connections = pool.size()
                
                self.metrics.db_connection_pool_in_use.set(in_use)
                self.metrics.db_connection_pool_max.set(max_connections)
                
                # Get database-specific metrics
                with self.engine.connect() as conn:
                    # Active connections
                    result = conn.execute("""
                        SELECT count(*) FROM pg_stat_activity 
                        WHERE state = 'active'
                    """)
                    active_connections = result.scalar()
                    
                    # Database size
                    result = conn.execute("""
                        SELECT pg_database_size(current_database())
                    """)
                    db_size = result.scalar()
                    
                    # Slow queries
                    result = conn.execute("""
                        SELECT count(*) FROM pg_stat_activity 
                        WHERE state = 'active' 
                        AND now() - query_start > interval '5 seconds'
                    """)
                    slow_queries = result.scalar()
                
                # Check for slow queries
                if slow_queries > 0:
                    logger.warning(f"Found {slow_queries} slow queries")
                    self.metrics.api_errors_total.labels(
                        endpoint='database',
                        error_type='slow_queries'
                    ).inc(slow_queries)
                
                await asyncio.sleep(self.monitoring_intervals['database_perf'])
                
            except Exception as e:
                logger.error(f"Database monitoring error: {e}")
                self.metrics.api_errors_total.labels(
                    endpoint='database',
                    error_type='monitoring_error'
                ).inc()
                await asyncio.sleep(30)
    
    async def monitor_system_metrics(self):
        """Monitora métricas do sistema (CPU, memória, disco)"""
        while True:
            try:
                import psutil
                
                # CPU usage
                cpu_percent = psutil.cpu_percent(interval=1)
                self.metrics.cpu_usage_percent.set(cpu_percent)
                
                # Memory usage
                memory = psutil.virtual_memory()
                memory_percent = memory.percent
                memory_bytes = memory.used
                self.metrics.memory_usage_bytes.set(memory_bytes)
                
                # Disk usage
                disk = psutil.disk_usage('/')
                disk_percent = (disk.used / disk.total) * 100
                self.metrics.disk_usage_percent.set(disk_percent)
                
                # Check thresholds and alert
                if cpu_percent > self.alert_thresholds.get('cpu_critical', 90):
                    logger.critical(f"Critical CPU usage: {cpu_percent}%")
                
                if memory_percent > self.alert_thresholds.get('memory_critical', 85):
                    logger.critical(f"Critical memory usage: {memory_percent}%")
                
                if disk_percent > self.alert_thresholds.get('disk_critical', 85):
                    logger.critical(f"Critical disk usage: {disk_percent}%")
                
                await asyncio.sleep(self.monitoring_intervals['system_metrics'])
                
            except Exception as e:
                logger.error(f"System metrics monitoring error: {e}")
                await asyncio.sleep(30)
    
    async def monitor_business_metrics(self):
        """Monitora métricas de negócio específicas da plataforma"""
        while True:
            try:
                with self.engine.connect() as conn:
                    # Active conversations
                    result = conn.execute("""
                        SELECT count(*) FROM conversations 
                        WHERE status = 'active' AND updated_at > now() - interval '1 hour'
                    """)
                    active_conversations = result.scalar()
                    self.metrics.conversations_active.set(active_conversations)
                    
                    # Models generating
                    result = conn.execute("""
                        SELECT count(*) FROM model_generation_jobs 
                        WHERE status IN ('pending', 'processing')
                    """)
                    models_generating = result.scalar()
                    self.metrics.models_generating.set(models_generating)
                    
                    # Active print jobs
                    result = conn.execute("""
                        SELECT count(*) FROM print_jobs 
                        WHERE status IN ('queued', 'printing')
                    """)
                    print_jobs = result.scalar()
                    self.metrics.print_jobs_active.set(print_jobs)
                    
                    # Rendering queue size
                    result = conn.execute("""
                        SELECT count(*) FROM render_jobs 
                        WHERE status = 'pending'
                    """)
                    render_queue = result.scalar()
                    self.metrics.renders_queue_size.set(render_queue)
                
                # Get session count from Redis
                active_sessions = self.redis_client.dbsize()
                self.metrics.active_sessions.set(active_sessions)
                
                await asyncio.sleep(self.monitoring_intervals['business_metrics'])
                
            except Exception as e:
                logger.error(f"Business metrics monitoring error: {e}")
                await asyncio.sleep(30)
    
    async def monitor_docker_containers(self):
        """Monitora status dos containers Docker"""
        while True:
            try:
                containers = self.docker_client.containers.list()
                
                for container in containers:
                    try:
                        stats = container.stats(stream=False)
                        
                        # Container-specific metrics could be added here
                        cpu_percent = calculate_cpu_percent(stats)
                        memory_usage = stats['memory_stats'].get('usage', 0)
                        
                        if container.name in ['3dpot-api', '3dpot-websocket']:
                            # Log container health
                            health_status = container.attrs['State']['Health']['Status'] if 'Health' in container.attrs['State'] else 'unknown'
                            
                            if health_status != 'healthy':
                                logger.warning(f"Container {container.name} health: {health_status}")
                                self.metrics.api_errors_total.labels(
                                    endpoint=f"container_{container.name}",
                                    error_type="unhealthy"
                                ).inc()
                    
                    except Exception as e:
                        logger.error(f"Error getting stats for container {container.name}: {e}")
                
                await asyncio.sleep(self.monitoring_intervals['docker_stats'])
                
            except Exception as e:
                logger.error(f"Docker monitoring error: {e}")
                await asyncio.sleep(60)
    
    async def run_monitoring(self):
        """Executa todos os monitors simultaneamente"""
        logger.info("Starting performance monitoring...")
        
        # Start Prometheus metrics server
        start_http_server(8001)
        logger.info("Prometheus metrics server started on port 8001")
        
        # Create monitoring tasks
        tasks = [
            asyncio.create_task(self.monitor_api_health()),
            asyncio.create_task(self.monitor_database_performance()),
            asyncio.create_task(self.monitor_system_metrics()),
            asyncio.create_task(self.monitor_business_metrics()),
            asyncio.create_task(self.monitor_docker_containers())
        ]
        
        try:
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
        except Exception as e:
            logger.error(f"Monitoring error: {e}")

def calculate_cpu_percent(stats):
    """Calcula percentual de CPU baseado nas stats do Docker"""
    cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - stats['precpu_stats']['cpu_usage']['total_usage']
    system_delta = stats['cpu_stats']['system_cpu_usage'] - stats['precpu_stats']['system_cpu_usage']
    
    if system_delta > 0:
        return (cpu_delta / system_delta) * len(stats['cpu_stats']['cpu_usage']['percpu_usage']) * 100.0
    return 0

async def main():
    """Função principal"""
    config = {
        'api_base_url': 'http://localhost:8000',
        'database_url': 'postgresql://3dpot:password@localhost:5432/3dpot_prod',
        'redis_url': 'redis://localhost:6379/0',
        'alert_thresholds': {
            'cpu_critical': 90,
            'memory_critical': 85,
            'disk_critical': 85,
            'api_response_time': 1.0  # seconds
        }
    }
    
    monitor = PerformanceMonitor(config)
    await monitor.run_monitoring()

if __name__ == "__main__":
    asyncio.run(main())