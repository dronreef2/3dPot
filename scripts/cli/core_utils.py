"""
CLI Core Utilities - 3dPot v2.0
================================

Módulo de utilidades compartilhadas para a CLI.
Centraliza lógica comum para evitar duplicação.

Autor: Sprint 5
Data: 2025-11-19
"""

import sys
from pathlib import Path
from typing import Optional, Callable


def execute_script(
    module_path: str,
    script_name: str,
    description: str,
    fallback_command: Optional[str] = None
) -> bool:
    """
    Executa um script de forma padronizada.
    
    Args:
        module_path: Caminho do módulo (ex: "scripts.demos")
        script_name: Nome do script (ex: "teste_minimax_standalone")
        description: Descrição da operação
        fallback_command: Comando alternativo caso falhe
        
    Returns:
        True se executou com sucesso, False caso contrário
    """
    print(f"🚀 Executando {description}...")
    print("=" * 60)
    
    try:
        # Importar módulo dinamicamente
        module = __import__(module_path, fromlist=[script_name])
        script_module = getattr(module, script_name, None)
        
        if script_module is None:
            raise ImportError(f"Script {script_name} não encontrado em {module_path}")
        
        # Executar função main se existir
        if hasattr(script_module, 'main'):
            script_module.main()
            return True
        else:
            print(f"⚠️  Script {script_name} não tem função main()")
            if fallback_command:
                print(f"💡 Execute diretamente: {fallback_command}")
            return False
            
    except ImportError as e:
        print(f"⚠️  Não foi possível importar {script_name}: {e}")
        if fallback_command:
            print(f"💡 Execute diretamente: {fallback_command}")
        return False
    except Exception as e:
        print(f"❌ Erro ao executar {script_name}: {e}")
        return False


def print_success(message: str):
    """Imprime mensagem de sucesso formatada."""
    print(f"✅ {message}")


def print_warning(message: str):
    """Imprime mensagem de aviso formatada."""
    print(f"⚠️  {message}")


def print_error(message: str):
    """Imprime mensagem de erro formatada."""
    print(f"❌ {message}")


def print_info(message: str):
    """Imprime mensagem informativa formatada."""
    print(f"💡 {message}")


def print_section(title: str, width: int = 60):
    """Imprime cabeçalho de seção."""
    print("\n" + "=" * width)
    print(title)
    print("=" * width)


def validate_dependencies(dependencies: list) -> bool:
    """
    Valida se dependências necessárias estão disponíveis.
    
    Args:
        dependencies: Lista de nomes de módulos
        
    Returns:
        True se todas dependências estão disponíveis
    """
    missing = []
    
    for dep in dependencies:
        try:
            __import__(dep)
        except ImportError:
            missing.append(dep)
    
    if missing:
        print_error(f"Dependências faltando: {', '.join(missing)}")
        print_info("Instale com: pip install " + " ".join(missing))
        return False
    
    return True


def get_project_root() -> Path:
    """Retorna o diretório raiz do projeto."""
    return Path(__file__).parent.parent.parent


def ensure_path_in_sys(path: Path):
    """Garante que um caminho está no sys.path."""
    path_str = str(path)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)
