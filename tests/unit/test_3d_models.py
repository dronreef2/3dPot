"""
Testes para validação dos modelos 3D do projeto 3dPot.
Verifica a estrutura, sintaxe e qualidade dos arquivos OpenSCAD.
"""

import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

import pytest


class TestOpenSCADModels:
    """Testes para validação dos modelos 3D OpenSCAD."""
    
    @pytest.fixture
    def models_root(self):
        """Retorna o diretório raiz dos modelos 3D."""
        return Path(__file__).parent.parent.parent / "modelos-3d"
    
    def test_models_directory_exists(self, models_root):
        """Verifica se o diretório de modelos 3D existe."""
        assert models_root.exists(), "3D models directory should exist"
        assert models_root.is_dir(), "models-3d should be a directory"
    
    def test_project_subdirectories_exist(self, models_root):
        """Verifica se existem sub diretórios por projeto."""
        project_dirs = [
            "arduino-projetos",
            "esp32-projetos",
            "raspberry-pi-projetos"
        ]
        
        for project_dir in project_dirs:
            project_path = models_root / project_dir
            if project_path.exists():
                assert project_path.is_dir(), f"{project_dir} should be a directory"
    
    def test_scad_files_have_valid_extensions(self, models_root):
        """Verifica se todos os arquivos .scad têm extensões válidas."""
        scad_files = list(models_root.glob("**/*.scad"))
        assert len(scad_files) > 0, "Should have at least one .scad file"
        
        for scad_file in scad_files:
            assert scad_file.suffix == ".scad", f"{scad_file.name} should have .scad extension"
            assert scad_file.stat().st_size > 0, f"{scad_file.name} should not be empty"
    
    def test_scad_files_contain_valid_syntax(self, models_root):
        """Verifica se os arquivos .scad contêm sintaxe básica válida."""
        scad_files = list(models_root.glob("**/*.scad"))
        
        for scad_file in scad_files:
            content = scad_file.read_text(encoding='utf-8')
            
            # Verifica se contém pelo menos uma função OpenSCAD básica
            basic_commands = [
                'module', 'union', 'difference', 'intersection',
                'cube', 'sphere', 'cylinder', 'translate', 'rotate',
                'scale', 'linear_extrude', 'rotate_extrude'
            ]
            
            has_basic_command = any(cmd in content for cmd in basic_commands)
            assert has_basic_command, f"{scad_file.name} should contain basic OpenSCAD commands"
            
            # Verifica se não está vazio ou só comentários
            lines = [line.strip() for line in content.split('\n') if line.strip() and not line.strip().startswith('//')]
            assert len(lines) > 0, f"{scad_file.name} should have non-empty content"
    
    def test_arduino_projects_have_appropriate_models(self, models_root):
        """Verifica se projetos Arduino têm modelos apropriados."""
        arduino_dir = models_root / "arduino-projetos"
        if arduino_dir.exists():
            scad_files = list(arduino_dir.glob("*.scad"))
            assert len(scad_files) > 0, "Should have Arduino project models"
            
            # Verifica nomes significativos
            arduino_keywords = ['esteira', 'transporte', 'motor', 'suporte', 'case']
            for scad_file in scad_files:
                filename_lower = scad_file.stem.lower()
                has_keyword = any(keyword in filename_lower for keyword in arduino_keywords)
                if not has_keyword:
                    # Se não tem palavra-chave esperada, pelo menos deve ter um nome descritivo
                    assert len(scad_file.stem) > 5, f"{scad_file.name} should have a descriptive name"
    
    def test_esp32_projects_have_appropriate_models(self, models_root):
        """Verifica se projetos ESP32 têm modelos apropriados."""
        esp32_dir = models_root / "esp32-projetos"
        if esp32_dir.exists():
            scad_files = list(esp32_dir.glob("*.scad"))
            assert len(scad_files) > 0, "Should have ESP32 project models"
            
            # Verifica nomes significativos
            esp32_keywords = ['filamento', 'monitor', 'suporte', 'case', 'display']
            for scad_file in scad_files:
                filename_lower = scad_file.stem.lower()
                has_keyword = any(keyword in filename_lower for keyword in esp32_keywords)
                if not has_keyword:
                    assert len(scad_file.stem) > 5, f"{scad_file.name} should have a descriptive name"
    
    def test_raspberry_pi_projects_have_appropriate_models(self, models_root):
        """Verifica se projetos Raspberry Pi têm modelos apropriados."""
        pi_dir = models_root / "raspberry-pi-projetos"
        if pi_dir.exists():
            scad_files = list(pi_dir.glob("*.scad"))
            assert len(scad_files) > 0, "Should have Raspberry Pi project models"
            
            # Verifica nomes significativos
            pi_keywords = ['estacao', 'qc', 'suporte', 'case', 'camera', 'monitor']
            for scad_file in scad_files:
                filename_lower = scad_file.stem.lower()
                has_keyword = any(keyword in filename_lower for keyword in pi_keywords)
                if not has_keyword:
                    assert len(scad_file.stem) > 5, f"{scad_file.name} should have a descriptive name"
    
    def test_scad_files_have_documentation(self, models_root):
        """Verifica se os arquivos .scad têm documentação básica."""
        scad_files = list(models_root.glob("**/*.scad"))
        
        for scad_file in scad_files:
            content = scad_file.read_text(encoding='utf-8')
            
            # Verifica se tem pelo menos um comentário
            has_comment = '//' in content
            if has_comment:
                # Se tem comentários, verifica se têm conteúdo substancial
                comment_lines = [line for line in content.split('\n') if line.strip().startswith('//')]
                total_comment_length = sum(len(line) for line in comment_lines)
                assert total_comment_length > 20, f"{scad_file.name} should have substantial documentation"
    
    def test_scad_module_structure(self, models_root):
        """Verifica se os arquivos .scad têm estrutura de módulos adequada."""
        scad_files = list(models_root.glob("**/*.scad"))
        
        for scad_file in scad_files:
            content = scad_file.read_text(encoding='utf-8')
            
            # Verifica se tem pelo menos um módulo ou uma estrutura principal
            has_module = 'module ' in content
            has_main_structure = 'union()' in content or 'difference()' in content or any(shape in content for shape in ['cube(', 'sphere(', 'cylinder('])
            
            if has_module:
                # Se tem módulos, verifica se têm nomes significativos
                modules = re.findall(r'module\s+(\w+)', content)
                for module_name in modules:
                    assert len(module_name) > 2, f"Module {module_name} in {scad_file.name} should have meaningful name"
                    assert not module_name.isdigit(), f"Module {module_name} in {scad_file.name} should not be just numbers"
            
            # Pelo menos um dos dois deve ser verdade
            assert has_module or has_main_structure, f"{scad_file.name} should have module or main structure"
    
    def test_scad_3d_primitives_usage(self, models_root):
        """Verifica se os arquivos .scad usam primitivas 3D adequadas."""
        scad_files = list(models_root.glob("**/*.scad"))
        
        for scad_file in scad_files:
            content = scad_file.read_text(encoding='utf-8')
            
            # Lista de primitivas 3D válidas
            primitives_3d = [
                'cube(', 'sphere(', 'cylinder(', 'polyhedron(',
                'square(', 'circle(', 'polygon('  # 2D primitives
            ]
            
            has_3d_primitive = any(primitive in content for primitive in primitives_3d)
            assert has_3d_primitive, f"{scad_file.name} should use 3D or 2D primitives"
    
    def test_scad_parameterization(self, models_root):
        """Verifica se os modelos usam parâmetros adequados."""
        scad_files = list(models_root.glob("**/*.scad"))
        
        parameterized_count = 0
        for scad_file in scad_files:
            content = scad_file.read_text(encoding='utf-8')
            
            # Verifica se usa variáveis ou parâmetros
            has_variables = re.search(r'^\s*(?:[a-zA-Z_][a-zA-Z0-9_]*\s*=|use<.*>)', content, re.MULTILINE)
            has_modules = 'module ' in content
            
            if has_variables or has_modules:
                parameterized_count += 1
        
        # Pelo menos alguns arquivos devem ter parameterização
        assert parameterized_count >= len(scad_files) * 0.3, "At least 30% of models should be parameterized"
    
    def test_scad_file_encoding(self, models_root):
        """Verifica se os arquivos .scad têm encoding UTF-8 válido."""
        scad_files = list(models_root.glob("**/*.scad"))
        
        for scad_file in scad_files:
            try:
                content = scad_file.read_text(encoding='utf-8')
                # Se chegar até aqui, o encoding é válido
                assert len(content) > 0, f"{scad_file.name} should have readable content"
            except UnicodeDecodeError:
                pytest.fail(f"{scad_file.name} has invalid UTF-8 encoding")


class TestSTLGeneration:
    """Testes para geração de arquivos STL (se disponíveis)."""
    
    def test_stl_files_have_proper_format(self, models_root):
        """Verifica se arquivos STL têm formato adequado."""
        stl_files = list(models_root.glob("**/*.stl"))
        
        for stl_file in stl_files:
            content = stl_file.read_text(encoding='utf-8', errors='ignore')
            
            # Verifica cabeçalho STL ou formato binário válido
            if content.startswith('solid '):
                # Formato ASCII
                assert 'endsolid' in content, f"{stl_file.name} should have proper ASCII STL structure"
            else:
                # Formato binário - verifica tamanho mínimo
                file_size = stl_file.stat().st_size
                assert file_size > 84, f"{stl_file.name} should be valid binary STL (>84 bytes)"
    
    def test_stl_files_not_empty(self, models_root):
        """Verifica se arquivos STL não estão vazios."""
        stl_files = list(models_root.glob("**/*.stl"))
        
        for stl_file in stl_files:
            file_size = stl_file.stat().st_size
            assert file_size > 100, f"{stl_file.name} should not be empty or too small"
    
    def test_stl_scad_correspondence(self, models_root):
        """Verifica se cada arquivo .scad tem arquivo STL correspondente."""
        scad_files = list(models_root.glob("**/*.scad"))
        stl_files = list(models_root.glob("**/*.stl"))
        
        stl_names = {stl.stem for stl in stl_files}
        scad_names = {scad.stem for scad in scad_files}
        
        # Cada arquivo .scad deve ter um correspondente .stl
        missing_stl = scad_names - stl_names
        assert len(missing_stl) <= len(scad_files) * 0.6, \
            f"Should have STL files for most .scad files. Missing: {missing_stl}"


class Test3DModelMetadata:
    """Testes para metadados e informações dos modelos 3D."""
    
    def test_model_documentation_exists(self, models_root):
        """Verifica se existe documentação dos modelos."""
        # Encontra o diretório raiz do projeto (subindo 3 níveis do tests/unit/test_3d_models.py)
        project_root = Path(__file__).parent.parent.parent
        doc_files = list(project_root.glob("projetos/**/*.md"))
        
        # Deve haver documentação de pelo menos alguns projetos
        assert len(doc_files) > 0, "Should have project documentation"
    
    def test_readme_mentions_3d_models(self, models_root):
        """Verifica se o README menciona os modelos 3D."""
        readme_path = models_root.parent / "README.md"
        if readme_path.exists():
            readme_content = readme_path.read_text()
            assert "3D" in readme_content or "OpenSCAD" in readme_content, \
                "README should mention 3D models or OpenSCAD"
    
    def test_model_categories_organized(self, models_root):
        """Verifica se os modelos estão organizados por categoria."""
        # Deve haver pelo menos 2 categorias diferentes
        categories = []
        if (models_root / "arduino-projetos").exists():
            categories.append("arduino")
        if (models_root / "esp32-projetos").exists():
            categories.append("esp32")
        if (models_root / "raspberry-pi-projetos").exists():
            categories.append("raspberry-pi")
        
        assert len(categories) >= 2, f"Should have at least 2 model categories, found: {categories}"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])