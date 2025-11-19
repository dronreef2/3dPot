#!/usr/bin/env python3
"""
Load Testing Simulation - 3dPot v2.0
=====================================

Simula carga no sistema para testar comportamento sob múltiplas requisições.
Útil para identificar gargalos e limites de performance.

Uso:
    python scripts/performance/load_test.py
    python scripts/performance/load_test.py --users 50 --duration 30

Autor: Sprint 5
Data: 2025-11-19
"""

import sys
import time
import threading
import statistics
from pathlib import Path
from typing import List, Dict
import argparse
from datetime import datetime, timedelta

# Adicionar backend ao path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class LoadTest:
    """Gerenciador de testes de carga"""
    
    def __init__(self, num_users: int, duration_seconds: int):
        self.num_users = num_users
        self.duration = duration_seconds
        self.results = []
        self.lock = threading.Lock()
        self.start_time = None
        self.end_time = None
    
    def simulate_user_request(self, user_id: int):
        """
        Simula requisição de um usuário.
        
        Args:
            user_id: ID do usuário simulado
        """
        start = time.perf_counter()
        
        # Simular diferentes tipos de operações
        operations = [
            self._simulate_budget_calculation,
            self._simulate_search_operation,
            self._simulate_data_processing
        ]
        
        # Executar operação aleatória
        import random
        operation = random.choice(operations)
        
        try:
            operation()
            success = True
            error = None
        except Exception as e:
            success = False
            error = str(e)
        
        end = time.perf_counter()
        response_time = (end - start) * 1000  # ms
        
        with self.lock:
            self.results.append({
                'user_id': user_id,
                'timestamp': time.time(),
                'response_time_ms': response_time,
                'success': success,
                'error': error
            })
    
    def _simulate_budget_calculation(self):
        """Simula cálculo de orçamento"""
        material_cost = 0.250 * 45.0
        printing_cost = 5.5 * 25.0
        assembly_cost = 2.0 * 50.0
        total = (material_cost + printing_cost + assembly_cost) * 1.30
        time.sleep(0.001)  # Simular latência
        return total
    
    def _simulate_search_operation(self):
        """Simula operação de busca"""
        items = [f"item_{i}" for i in range(1000)]
        query = "sensor"
        results = [item for item in items if "sensor" in item or "item" in item]
        time.sleep(0.002)  # Simular latência
        return results[:20]
    
    def _simulate_data_processing(self):
        """Simula processamento de dados"""
        data = list(range(500))
        processed = [x * 2 for x in data if x % 2 == 0]
        time.sleep(0.0015)  # Simular latência
        return sum(processed)
    
    def run_user_simulation(self, user_id: int):
        """
        Executa simulação de um usuário por toda a duração do teste.
        
        Args:
            user_id: ID do usuário
        """
        end_time = time.time() + self.duration
        
        while time.time() < end_time:
            self.simulate_user_request(user_id)
            # Pequeno delay entre requisições (simular think time)
            time.sleep(0.1)
    
    def run(self):
        """Executa teste de carga com múltiplos usuários"""
        print(f"\n🚀 INICIANDO TESTE DE CARGA")
        print(f"   Usuários simultâneos: {self.num_users}")
        print(f"   Duração: {self.duration}s")
        print(f"   Início: {datetime.now().strftime('%H:%M:%S')}")
        
        self.start_time = time.time()
        
        # Criar threads para cada usuário
        threads = []
        for user_id in range(self.num_users):
            thread = threading.Thread(
                target=self.run_user_simulation,
                args=(user_id,)
            )
            threads.append(thread)
            thread.start()
        
        # Aguardar conclusão de todas as threads
        for thread in threads:
            thread.join()
        
        self.end_time = time.time()
        
        print(f"   Fim: {datetime.now().strftime('%H:%M:%S')}")
        print(f"   ✅ Teste concluído!\n")
    
    def analyze_results(self):
        """Analisa e exibe resultados do teste de carga"""
        if not self.results:
            print("❌ Nenhum resultado para analisar")
            return
        
        # Calcular métricas
        response_times = [r['response_time_ms'] for r in self.results]
        successes = [r for r in self.results if r['success']]
        failures = [r for r in self.results if not r['success']]
        
        total_requests = len(self.results)
        success_rate = (len(successes) / total_requests * 100) if total_requests > 0 else 0
        
        duration = self.end_time - self.start_time
        throughput = total_requests / duration if duration > 0 else 0
        
        # Imprimir resultados
        print("=" * 80)
        print("📊 RESULTADOS DO TESTE DE CARGA")
        print("=" * 80)
        
        print("\n📈 Métricas Gerais:")
        print(f"   Total de requisições:  {total_requests}")
        print(f"   Requisições bem-sucedidas: {len(successes)}")
        print(f"   Requisições com erro:  {len(failures)}")
        print(f"   Taxa de sucesso:       {success_rate:.2f}%")
        print(f"   Throughput:            {throughput:.2f} req/s")
        
        print("\n⏱️  Tempo de Resposta:")
        print(f"   Média:         {statistics.mean(response_times):.3f} ms")
        print(f"   Mediana:       {statistics.median(response_times):.3f} ms")
        print(f"   Mínimo:        {min(response_times):.3f} ms")
        print(f"   Máximo:        {max(response_times):.3f} ms")
        print(f"   Desvio Padrão: {statistics.stdev(response_times):.3f} ms")
        
        # Percentis
        sorted_times = sorted(response_times)
        p50 = sorted_times[int(len(sorted_times) * 0.50)]
        p90 = sorted_times[int(len(sorted_times) * 0.90)]
        p95 = sorted_times[int(len(sorted_times) * 0.95)]
        p99 = sorted_times[int(len(sorted_times) * 0.99)]
        
        print("\n📊 Percentis:")
        print(f"   P50 (mediana): {p50:.3f} ms")
        print(f"   P90:           {p90:.3f} ms")
        print(f"   P95:           {p95:.3f} ms")
        print(f"   P99:           {p99:.3f} ms")
        
        # Recomendações
        print("\n💡 Análise:")
        if statistics.mean(response_times) < 100:
            print("   ✅ Tempo de resposta médio excelente (< 100ms)")
        elif statistics.mean(response_times) < 500:
            print("   ⚠️  Tempo de resposta médio aceitável (< 500ms)")
        else:
            print("   ❌ Tempo de resposta médio alto (> 500ms)")
        
        if success_rate >= 99:
            print("   ✅ Taxa de sucesso excelente (>= 99%)")
        elif success_rate >= 95:
            print("   ⚠️  Taxa de sucesso aceitável (>= 95%)")
        else:
            print("   ❌ Taxa de sucesso baixa (< 95%)")
        
        if throughput >= 100:
            print("   ✅ Throughput alto (>= 100 req/s)")
        elif throughput >= 50:
            print("   ⚠️  Throughput médio (>= 50 req/s)")
        else:
            print("   ❌ Throughput baixo (< 50 req/s)")
        
        print("\n" + "=" * 80 + "\n")


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(
        description='Teste de carga para sistema 3dPot'
    )
    parser.add_argument(
        '--users',
        type=int,
        default=10,
        help='Número de usuários simultâneos (default: 10)'
    )
    parser.add_argument(
        '--duration',
        type=int,
        default=10,
        help='Duração do teste em segundos (default: 10)'
    )
    
    args = parser.parse_args()
    
    # Validações
    if args.users < 1:
        print("❌ Número de usuários deve ser >= 1")
        return
    
    if args.duration < 1:
        print("❌ Duração deve ser >= 1 segundo")
        return
    
    # Executar teste de carga
    load_test = LoadTest(
        num_users=args.users,
        duration_seconds=args.duration
    )
    
    load_test.run()
    load_test.analyze_results()


if __name__ == "__main__":
    main()
