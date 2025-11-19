"""
Testes unitários para CLI Core Utilities
Cobertura: Utilitários centralizados da CLI
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys


class TestCLICoreUtils:
    """Testes de utilitários core da CLI"""
    
    def test_core_utils_module_exists(self):
        """Testa existência do módulo core_utils"""
        import os
        assert os.path.exists("scripts/cli/core_utils.py")
    
    def test_execute_script_function_signature(self):
        """Testa assinatura da função execute_script"""
        from scripts.cli.core_utils import execute_script
        
        assert callable(execute_script)
        # Verificar que função aceita parâmetros esperados
        import inspect
        sig = inspect.signature(execute_script)
        params = list(sig.parameters.keys())
        
        assert 'module_path' in params
        assert 'script_name' in params
        assert 'description' in params
    
    def test_print_functions_exist(self):
        """Testa existência de funções de print formatado"""
        from scripts.cli import core_utils
        
        assert hasattr(core_utils, 'print_success')
        assert hasattr(core_utils, 'print_warning')
        assert hasattr(core_utils, 'print_error')
        assert hasattr(core_utils, 'print_info')
    
    def test_print_success(self, capsys):
        """Testa função print_success"""
        from scripts.cli.core_utils import print_success
        
        print_success("Test message")
        captured = capsys.readouterr()
        
        assert "✅" in captured.out
        assert "Test message" in captured.out
    
    def test_print_warning(self, capsys):
        """Testa função print_warning"""
        from scripts.cli.core_utils import print_warning
        
        print_warning("Warning message")
        captured = capsys.readouterr()
        
        assert "⚠️" in captured.out
        assert "Warning message" in captured.out
    
    def test_print_error(self, capsys):
        """Testa função print_error"""
        from scripts.cli.core_utils import print_error
        
        print_error("Error message")
        captured = capsys.readouterr()
        
        assert "❌" in captured.out
        assert "Error message" in captured.out
    
    def test_print_info(self, capsys):
        """Testa função print_info"""
        from scripts.cli.core_utils import print_info
        
        print_info("Info message")
        captured = capsys.readouterr()
        
        assert "💡" in captured.out
        assert "Info message" in captured.out
    
    def test_print_section(self, capsys):
        """Testa função print_section"""
        from scripts.cli.core_utils import print_section
        
        print_section("Test Section")
        captured = capsys.readouterr()
        
        assert "Test Section" in captured.out
        assert "=" in captured.out
    
    def test_get_project_root(self):
        """Testa função get_project_root"""
        from scripts.cli.core_utils import get_project_root
        
        root = get_project_root()
        
        assert isinstance(root, Path)
        assert root.exists()
        # Deve ter alguns arquivos/pastas do projeto
        assert (root / "scripts").exists() or (root / "backend").exists()
    
    def test_validate_dependencies_success(self):
        """Testa validação de dependências bem-sucedida"""
        from scripts.cli.core_utils import validate_dependencies
        
        # Testar com módulos padrão do Python
        result = validate_dependencies(['sys', 'os', 'pathlib'])
        
        assert result is True
    
    def test_validate_dependencies_failure(self, capsys):
        """Testa validação de dependências com falha"""
        from scripts.cli.core_utils import validate_dependencies
        
        # Testar com módulo inexistente
        result = validate_dependencies(['nonexistent_module_xyz123'])
        
        assert result is False
        captured = capsys.readouterr()
        assert "Dependências faltando" in captured.out or "❌" in captured.out
    
    def test_ensure_path_in_sys(self):
        """Testa função ensure_path_in_sys"""
        from scripts.cli.core_utils import ensure_path_in_sys, get_project_root
        
        test_path = get_project_root() / "test_temp_path"
        
        # Remover do sys.path se existir
        if str(test_path) in sys.path:
            sys.path.remove(str(test_path))
        
        # Adicionar usando função
        ensure_path_in_sys(test_path)
        
        # Verificar que está no sys.path
        assert str(test_path) in sys.path
        
        # Limpar
        if str(test_path) in sys.path:
            sys.path.remove(str(test_path))


class TestExecuteScriptFunction:
    """Testes da função execute_script"""
    
    def test_execute_script_with_missing_module(self, capsys):
        """Testa execute_script com módulo inexistente"""
        from scripts.cli.core_utils import execute_script
        
        result = execute_script(
            module_path="nonexistent.module",
            script_name="test_script",
            description="Test Description",
            fallback_command="python test.py"
        )
        
        assert result is False
        captured = capsys.readouterr()
        assert "⚠️" in captured.out or "❌" in captured.out
    
    def test_execute_script_import_error_handling(self, capsys):
        """Testa tratamento de erro de importação"""
        from scripts.cli.core_utils import execute_script
        
        result = execute_script(
            module_path="definitely.nonexistent.module.path",
            script_name="fake_script",
            description="Test Import Error"
        )
        
        assert result is False
        captured = capsys.readouterr()
        assert "⚠️" in captured.out or "❌" in captured.out
    
    def test_execute_script_general_exception(self, capsys):
        """Testa tratamento de exceção geral"""
        from scripts.cli.core_utils import execute_script
        
        # Tentar importar algo que existe mas vai falhar de outra forma
        result = execute_script(
            module_path="os",  # módulo existe
            script_name="nonexistent_attribute",  # mas atributo não
            description="Test Exception"
        )
        
        assert result is False
        captured = capsys.readouterr()
        # Deve ter alguma mensagem de erro
        assert len(captured.out) > 0
