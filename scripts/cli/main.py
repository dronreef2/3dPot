#!/usr/bin/env python3
"""
3dPot CLI - Ferramenta Unificada de Linha de Comando

Interface unificada para demos, validações e monitoramento do projeto 3dPot.

Uso:
    python -m scripts.cli.main <comando> [opções]
    
Ou diretamente:
    python scripts/cli/main.py <comando> [opções]

Comandos disponíveis:
    demo        - Executar demonstrações do sistema
    validate    - Executar validações de código e modelos
    monitor     - Monitorar workflows e sistema
    
Exemplos:
    python -m scripts.cli.main demo minimax
    python -m scripts.cli.main validate openscad
    python -m scripts.cli.main monitor workflows
"""

import sys
import argparse
from pathlib import Path

# Adicionar diretório raiz ao path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def setup_demo_subcommands(subparsers):
    """Configura subcomandos de demonstração."""
    demo_parser = subparsers.add_parser(
        'demo',
        help='Executar demonstrações do sistema'
    )
    
    demo_subparsers = demo_parser.add_subparsers(
        dest='demo_type',
        help='Tipo de demonstração'
    )
    
    # Demo: Minimax
    demo_subparsers.add_parser(
        'minimax',
        help='Demonstração de integração com Minimax M2'
    )
    
    # Demo: Modeling
    demo_subparsers.add_parser(
        'modeling',
        help='Demonstração do sistema de modelagem 3D'
    )
    
    # Demo: System
    demo_subparsers.add_parser(
        'system',
        help='Demonstração completa do sistema'
    )
    
    # Demo: LGM
    demo_subparsers.add_parser(
        'lgm',
        help='Demonstração de integração com LGM'
    )
    
    # Demo: Auth
    demo_subparsers.add_parser(
        'auth',
        help='Demonstração do sistema de autenticação'
    )


def setup_validate_subcommands(subparsers):
    """Configura subcomandos de validação."""
    validate_parser = subparsers.add_parser(
        'validate',
        help='Executar validações de código e modelos'
    )
    
    validate_subparsers = validate_parser.add_subparsers(
        dest='validate_type',
        help='Tipo de validação'
    )
    
    # Validate: OpenSCAD
    openscad_parser = validate_subparsers.add_parser(
        'openscad',
        help='Validar modelos OpenSCAD'
    )
    openscad_parser.add_argument(
        '--quick',
        action='store_true',
        help='Executar validação rápida'
    )
    
    # Validate: Syntax
    validate_subparsers.add_parser(
        'syntax',
        help='Validar sintaxe do código Python'
    )
    
    # Validate: Code Quality
    validate_subparsers.add_parser(
        'quality',
        help='Validar qualidade do código'
    )


def setup_monitor_subcommands(subparsers):
    """Configura subcomandos de monitoramento."""
    monitor_parser = subparsers.add_parser(
        'monitor',
        help='Monitorar workflows e sistema'
    )
    
    monitor_subparsers = monitor_parser.add_subparsers(
        dest='monitor_type',
        help='Tipo de monitoramento'
    )
    
    # Monitor: Workflows
    workflows_parser = monitor_subparsers.add_parser(
        'workflows',
        help='Monitorar workflows GitHub Actions'
    )
    workflows_parser.add_argument(
        '--optimize',
        action='store_true',
        help='Sugerir otimizações para workflows'
    )
    
    # Monitor: Performance
    monitor_subparsers.add_parser(
        'performance',
        help='Monitorar performance do sistema'
    )


def run_demo_minimax():
    """Executa demo do Minimax."""
    print("🚀 Executando demonstração Minimax M2...")
    print("=" * 60)
    
    try:
        # Importar e executar script de demo minimax
        from scripts.demos import teste_minimax_standalone
        
        # Se o módulo tem uma função main
        if hasattr(teste_minimax_standalone, 'main'):
            teste_minimax_standalone.main()
        else:
            print("⚠️  Script de demonstração Minimax não tem função main()")
            print("💡 Execute diretamente: python scripts/demos/teste-minimax-standalone.py")
    except ImportError as e:
        print(f"⚠️  Não foi possível importar demo Minimax: {e}")
        print("💡 Execute diretamente: python scripts/demos/teste-minimax-standalone.py")
    except Exception as e:
        print(f"❌ Erro ao executar demo: {e}")


def run_demo_modeling():
    """Executa demo de modelagem."""
    print("🚀 Executando demonstração de Modelagem 3D...")
    print("=" * 60)
    
    try:
        from scripts.demos import teste_sistema_modelagem_sprint3
        
        if hasattr(teste_sistema_modelagem_sprint3, 'main'):
            teste_sistema_modelagem_sprint3.main()
        else:
            print("⚠️  Script não tem função main()")
            print("💡 Execute: python scripts/demos/teste-sistema-modelagem-sprint3.py")
    except ImportError:
        print("⚠️  Demo de modelagem não encontrado")
        print("💡 Execute: python scripts/demos/teste-sistema-modelagem-sprint3.py")
    except Exception as e:
        print(f"❌ Erro: {e}")


def run_demo_system():
    """Executa demo do sistema completo."""
    print("🚀 Executando demonstração do Sistema Completo...")
    print("=" * 60)
    
    try:
        from scripts.demos import demonstracao_sistema
        
        if hasattr(demonstracao_sistema, 'main'):
            demonstracao_sistema.main()
        else:
            print("⚠️  Script não tem função main()")
            print("💡 Execute: python scripts/demos/demonstracao_sistema.py")
    except ImportError:
        print("⚠️  Demo do sistema não encontrado")
        print("💡 Execute: python scripts/demos/demonstracao_sistema.py")
    except Exception as e:
        print(f"❌ Erro: {e}")


def run_demo_lgm():
    """Executa demo do LGM."""
    print("🚀 Executando demonstração LGM...")
    print("=" * 60)
    
    try:
        from scripts.demos import lgm_integration_example
        
        if hasattr(lgm_integration_example, 'main'):
            lgm_integration_example.main()
        else:
            print("⚠️  Script não tem função main()")
            print("💡 Execute: python scripts/demos/lgm_integration_example.py")
    except ImportError:
        print("⚠️  Demo LGM não encontrado")
        print("💡 Execute: python scripts/demos/lgm_integration_example.py")
    except Exception as e:
        print(f"❌ Erro: {e}")


def run_demo_auth():
    """Executa demo de autenticação."""
    print("🚀 Executando demonstração de Autenticação...")
    print("=" * 60)
    
    try:
        from scripts.demos import test_auth_system
        
        if hasattr(test_auth_system, 'main'):
            test_auth_system.main()
        else:
            print("⚠️  Script não tem função main()")
            print("💡 Execute: python scripts/demos/test-auth-system.py")
    except ImportError:
        print("⚠️  Demo de autenticação não encontrado")
        print("💡 Execute: python scripts/demos/test-auth-system.py")
    except Exception as e:
        print(f"❌ Erro: {e}")


def run_validate_openscad(quick=False):
    """Executa validação de modelos OpenSCAD."""
    print("🔍 Validando modelos OpenSCAD...")
    print("=" * 60)
    
    script_name = "quick_openscad_check" if quick else "validate_openscad_models"
    
    try:
        if quick:
            from scripts.validacao import quick_openscad_check
            module = quick_openscad_check
        else:
            from scripts.validacao import validate_openscad_models
            module = validate_openscad_models
        
        if hasattr(module, 'main'):
            module.main()
        else:
            print(f"⚠️  Script {script_name} não tem função main()")
            print(f"💡 Execute: python scripts/validacao/{script_name}.py")
    except ImportError as e:
        print(f"⚠️  Validador não encontrado: {e}")
        print(f"💡 Execute: python scripts/validacao/{script_name}.py")
    except Exception as e:
        print(f"❌ Erro: {e}")


def run_validate_syntax():
    """Executa validação de sintaxe."""
    print("🔍 Validando sintaxe do código Python...")
    print("=" * 60)
    
    try:
        from scripts.validacao import syntax_validator
        
        if hasattr(syntax_validator, 'main'):
            syntax_validator.main()
        else:
            print("⚠️  Validador de sintaxe não tem função main()")
            print("💡 Execute: python scripts/validacao/syntax_validator.py")
    except ImportError:
        print("⚠️  Validador de sintaxe não encontrado")
        print("💡 Execute: python scripts/validacao/syntax_validator.py")
    except Exception as e:
        print(f"❌ Erro: {e}")


def run_validate_quality():
    """Executa validação de qualidade de código."""
    print("🔍 Validando qualidade do código...")
    print("=" * 60)
    
    try:
        from scripts.validacao import fix_code_quality
        
        if hasattr(fix_code_quality, 'main'):
            fix_code_quality.main()
        else:
            print("⚠️  Script não tem função main()")
            print("💡 Execute: python scripts/validacao/fix_code_quality.py")
    except ImportError:
        print("⚠️  Script de qualidade não encontrado")
        print("💡 Execute: python scripts/validacao/fix_code_quality.py")
    except Exception as e:
        print(f"❌ Erro: {e}")


def run_monitor_workflows(optimize=False):
    """Executa monitoramento de workflows."""
    print("📊 Monitorando workflows...")
    print("=" * 60)
    
    script = "optimize_workflows" if optimize else "workflow_monitor"
    
    try:
        if optimize:
            from scripts.monitoramento import optimize_workflows
            module = optimize_workflows
        else:
            from scripts.monitoramento import workflow_monitor
            module = workflow_monitor
        
        if hasattr(module, 'main'):
            module.main()
        else:
            print(f"⚠️  Script {script} não tem função main()")
            print(f"💡 Execute: python scripts/monitoramento/{script}.py")
    except ImportError as e:
        print(f"⚠️  Monitor não encontrado: {e}")
        print(f"💡 Execute: python scripts/monitoramento/{script}.py")
    except Exception as e:
        print(f"❌ Erro: {e}")


def run_monitor_performance():
    """Executa monitoramento de performance."""
    print("📊 Monitorando performance...")
    print("=" * 60)
    
    try:
        from scripts import performance_monitor
        
        if hasattr(performance_monitor, 'main'):
            performance_monitor.main()
        else:
            print("⚠️  Monitor de performance não tem função main()")
            print("💡 Execute: python scripts/performance_monitor.py")
    except ImportError:
        print("⚠️  Monitor de performance não encontrado")
        print("💡 Execute: python scripts/performance_monitor.py")
    except Exception as e:
        print(f"❌ Erro: {e}")


def main():
    """Função principal da CLI."""
    parser = argparse.ArgumentParser(
        description='3dPot CLI - Ferramenta Unificada de Linha de Comando',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  %(prog)s demo minimax          # Demo de integração Minimax
  %(prog)s demo modeling         # Demo de modelagem 3D
  %(prog)s validate openscad     # Validar modelos OpenSCAD
  %(prog)s validate openscad --quick  # Validação rápida OpenSCAD
  %(prog)s monitor workflows     # Monitorar workflows
  %(prog)s monitor workflows --optimize  # Otimizar workflows
        """
    )
    
    subparsers = parser.add_subparsers(
        dest='command',
        help='Comando a executar',
        required=True
    )
    
    # Configurar subcomandos
    setup_demo_subcommands(subparsers)
    setup_validate_subcommands(subparsers)
    setup_monitor_subcommands(subparsers)
    
    # Parse argumentos
    args = parser.parse_args()
    
    # Executar comando apropriado
    try:
        if args.command == 'demo':
            if args.demo_type == 'minimax':
                run_demo_minimax()
            elif args.demo_type == 'modeling':
                run_demo_modeling()
            elif args.demo_type == 'system':
                run_demo_system()
            elif args.demo_type == 'lgm':
                run_demo_lgm()
            elif args.demo_type == 'auth':
                run_demo_auth()
            else:
                print(f"❌ Tipo de demo desconhecido: {args.demo_type}")
                return 1
                
        elif args.command == 'validate':
            if args.validate_type == 'openscad':
                run_validate_openscad(quick=getattr(args, 'quick', False))
            elif args.validate_type == 'syntax':
                run_validate_syntax()
            elif args.validate_type == 'quality':
                run_validate_quality()
            else:
                print(f"❌ Tipo de validação desconhecido: {args.validate_type}")
                return 1
                
        elif args.command == 'monitor':
            if args.monitor_type == 'workflows':
                run_monitor_workflows(optimize=getattr(args, 'optimize', False))
            elif args.monitor_type == 'performance':
                run_monitor_performance()
            else:
                print(f"❌ Tipo de monitoramento desconhecido: {args.monitor_type}")
                return 1
        
        print("\n✅ Comando concluído com sucesso!")
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Operação cancelada pelo usuário")
        return 130
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
