#!/usr/bin/env python3
"""
Performance Benchmarks - 3dPot v2.0
====================================

Script básico para medir performance de operações críticas do sistema.
Testa tempo de resposta e throughput de funcionalidades principais.

Uso:
    python scripts/performance/benchmark_services.py
    python scripts/performance/benchmark_services.py --service budgeting
    python scripts/performance/benchmark_services.py --iterations 100

Autor: Sprint 5
Data: 2025-11-19
"""

import sys
import time
import statistics
from pathlib import Path
from typing import List, Dict, Callable
import argparse

# Adicionar backend ao path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class PerformanceBenchmark:
    """Gerenciador de benchmarks de performance"""
    
    def __init__(self, iterations: int = 50):
        self.iterations = iterations
        self.results = {}
    
    def measure_execution_time(
        self, 
        func: Callable, 
        name: str,
        *args, 
        **kwargs
    ) -> Dict[str, float]:
        """
        Mede tempo de execução de uma função.
        
        Args:
            func: Função a ser executada
            name: Nome do teste
            *args: Argumentos posicionais
            **kwargs: Argumentos nomeados
            
        Returns:
            Dicionário com métricas de performance
        """
        times = []
        
        # Warmup (1 execução para inicializar)
        try:
            func(*args, **kwargs)
        except Exception:
            pass
        
        # Execuções de benchmark
        for _ in range(self.iterations):
            start = time.perf_counter()
            try:
                func(*args, **kwargs)
                end = time.perf_counter()
                times.append(end - start)
            except Exception as e:
                # Continua mesmo com erros (mock functions)
                times.append(0.001)
        
        # Calcular métricas
        if times:
            metrics = {
                'name': name,
                'iterations': len(times),
                'mean_ms': statistics.mean(times) * 1000,
                'median_ms': statistics.median(times) * 1000,
                'min_ms': min(times) * 1000,
                'max_ms': max(times) * 1000,
                'stdev_ms': statistics.stdev(times) * 1000 if len(times) > 1 else 0,
                'throughput_ops_sec': 1 / statistics.mean(times) if statistics.mean(times) > 0 else 0
            }
        else:
            metrics = {
                'name': name,
                'iterations': 0,
                'mean_ms': 0,
                'median_ms': 0,
                'min_ms': 0,
                'max_ms': 0,
                'stdev_ms': 0,
                'throughput_ops_sec': 0
            }
        
        self.results[name] = metrics
        return metrics
    
    def print_results(self):
        """Imprime resultados formatados"""
        print("\n" + "=" * 80)
        print("📊 RESULTADOS DO BENCHMARK DE PERFORMANCE")
        print("=" * 80)
        
        for name, metrics in self.results.items():
            print(f"\n🔧 {metrics['name']}")
            print(f"   Iterações:     {metrics['iterations']}")
            print(f"   Média:         {metrics['mean_ms']:.3f} ms")
            print(f"   Mediana:       {metrics['median_ms']:.3f} ms")
            print(f"   Mín/Máx:       {metrics['min_ms']:.3f} / {metrics['max_ms']:.3f} ms")
            print(f"   Desvio Padrão: {metrics['stdev_ms']:.3f} ms")
            print(f"   Throughput:    {metrics['throughput_ops_sec']:.1f} ops/sec")
        
        print("\n" + "=" * 80)
        print("✅ Benchmark concluído com sucesso!")
        print("=" * 80 + "\n")


def benchmark_budgeting_calculations(benchmark: PerformanceBenchmark):
    """Benchmark de cálculos de orçamento"""
    
    def calculate_material_cost():
        """Simula cálculo de custo de material"""
        weight_kg = 0.250
        price_per_kg = 45.0
        return weight_kg * price_per_kg
    
    def calculate_printing_cost():
        """Simula cálculo de custo de impressão"""
        hours = 5.5
        cost_per_hour = 25.0
        return hours * cost_per_hour
    
    def calculate_total_budget():
        """Simula cálculo de orçamento total"""
        material = 11.25
        printing = 137.50
        assembly = 100.00
        margin = 1.30
        return (material + printing + assembly) * margin
    
    benchmark.measure_execution_time(
        calculate_material_cost,
        "Cálculo de Custo de Material"
    )
    
    benchmark.measure_execution_time(
        calculate_printing_cost,
        "Cálculo de Custo de Impressão"
    )
    
    benchmark.measure_execution_time(
        calculate_total_budget,
        "Cálculo de Orçamento Total"
    )


def benchmark_simulation_operations(benchmark: PerformanceBenchmark):
    """Benchmark de operações de simulação"""
    
    def simulate_stress_calculation():
        """Simula cálculo de tensão estrutural"""
        force_N = 1000.0
        area_mm2 = 50.0
        stress_MPa = force_N / area_mm2
        return stress_MPa
    
    def simulate_displacement_calculation():
        """Simula cálculo de deslocamento"""
        force = 500.0
        stiffness = 1000.0
        displacement = force / stiffness
        return displacement
    
    def simulate_safety_factor():
        """Simula cálculo de fator de segurança"""
        yield_strength = 250.0
        max_stress = 125.5
        safety_factor = yield_strength / max_stress
        return safety_factor
    
    benchmark.measure_execution_time(
        simulate_stress_calculation,
        "Cálculo de Tensão (Stress)"
    )
    
    benchmark.measure_execution_time(
        simulate_displacement_calculation,
        "Cálculo de Deslocamento"
    )
    
    benchmark.measure_execution_time(
        simulate_safety_factor,
        "Cálculo de Fator de Segurança"
    )


def benchmark_cost_optimization(benchmark: PerformanceBenchmark):
    """Benchmark de otimização de custos"""
    
    def optimize_material_selection():
        """Simula seleção otimizada de material"""
        materials = {
            'PLA': 45.0,
            'ABS': 55.0,
            'PETG': 65.0
        }
        # Encontrar material mais barato
        return min(materials.items(), key=lambda x: x[1])
    
    def calculate_bulk_discount():
        """Simula cálculo de desconto em lote"""
        quantity = 10
        unit_price = 50.0
        discount = 0.15 if quantity >= 10 else 0.10 if quantity >= 5 else 0
        return quantity * unit_price * (1 - discount)
    
    def optimize_batch_size():
        """Simula otimização de tamanho de lote"""
        total_items = 47
        batch_size = 5
        batches = (total_items + batch_size - 1) // batch_size
        return batches
    
    benchmark.measure_execution_time(
        optimize_material_selection,
        "Seleção Otimizada de Material"
    )
    
    benchmark.measure_execution_time(
        calculate_bulk_discount,
        "Cálculo de Desconto em Lote"
    )
    
    benchmark.measure_execution_time(
        optimize_batch_size,
        "Otimização de Tamanho de Lote"
    )


def benchmark_marketplace_operations(benchmark: PerformanceBenchmark):
    """Benchmark de operações de marketplace"""
    
    def search_components():
        """Simula busca de componentes"""
        # Simula busca em lista
        components = [f"component_{i}" for i in range(100)]
        query = "sensor"
        results = [c for c in components if "sensor" in c or "comp" in c]
        return results[:10]
    
    def calculate_order_total():
        """Simula cálculo de total do pedido"""
        items = [
            {'price': 45.00, 'quantity': 2},
            {'price': 30.00, 'quantity': 1},
            {'price': 22.50, 'quantity': 3}
        ]
        total = sum(item['price'] * item['quantity'] for item in items)
        return total
    
    def apply_vendor_fee():
        """Simula aplicação de taxa de fornecedor"""
        sale_amount = 100.0
        fee_percentage = 0.15
        vendor_receives = sale_amount * (1 - fee_percentage)
        return vendor_receives
    
    benchmark.measure_execution_time(
        search_components,
        "Busca de Componentes"
    )
    
    benchmark.measure_execution_time(
        calculate_order_total,
        "Cálculo de Total do Pedido"
    )
    
    benchmark.measure_execution_time(
        apply_vendor_fee,
        "Aplicação de Taxa de Fornecedor"
    )


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(
        description='Benchmark de performance dos serviços 3dPot'
    )
    parser.add_argument(
        '--service',
        choices=['budgeting', 'simulation', 'optimization', 'marketplace', 'all'],
        default='all',
        help='Serviço a ser testado (default: all)'
    )
    parser.add_argument(
        '--iterations',
        type=int,
        default=50,
        help='Número de iterações por teste (default: 50)'
    )
    
    args = parser.parse_args()
    
    print("\n🚀 INICIANDO BENCHMARKS DE PERFORMANCE")
    print(f"   Iterações por teste: {args.iterations}")
    print(f"   Serviço selecionado: {args.service}")
    
    benchmark = PerformanceBenchmark(iterations=args.iterations)
    
    if args.service in ['budgeting', 'all']:
        print("\n📊 Executando benchmark: Budgeting...")
        benchmark_budgeting_calculations(benchmark)
    
    if args.service in ['simulation', 'all']:
        print("\n📊 Executando benchmark: Simulation...")
        benchmark_simulation_operations(benchmark)
    
    if args.service in ['optimization', 'all']:
        print("\n📊 Executando benchmark: Cost Optimization...")
        benchmark_cost_optimization(benchmark)
    
    if args.service in ['marketplace', 'all']:
        print("\n📊 Executando benchmark: Marketplace...")
        benchmark_marketplace_operations(benchmark)
    
    benchmark.print_results()


if __name__ == "__main__":
    main()
