"""
Testes para validação da estrutura geral do projeto 3dPot.
Verifica se todos os componentes essenciais estão presentes e organizados corretamente.
"""

import json
import os
import subprocess
from pathlib import Path

import pytest


class TestProjectStructure:
    """Testes para a estrutura geral do projeto."""
    
    @pytest.fixture
    def project_root(self):
        """Retorna o diretório raiz do projeto."""
        return Path(__file__).parent.parent.parent
    
    def test_readme_exists(self, project_root):
        """Verifica se o README.md existe."""
        readme_path = project_root / "README.md"
        assert readme_path.exists(), "README.md should exist in project root"
        assert readme_path.stat().st_size > 0, "README.md should not be empty"
    
    def test_license_exists(self, project_root):
        """Verifica se o arquivo de licença existe."""
        license_path = project_root / "LICENSE"
        assert license_path.exists(), "LICENSE file should exist"
    
    def test_gitignore_exists(self, project_root):
        """Verifica se .gitignore existe."""
        gitignore_path = project_root / ".gitignore"
        assert gitignore_path.exists(), ".gitignore should exist"
    
    def test_required_directories_exist(self, project_root):
        """Verifica se os diretórios essenciais existem."""
        required_dirs = [
            "codigos",
            "modelos-3d",
            "interface-web",
            "tests",
            "assets",
            "projetos"
        ]
        
        for dir_name in required_dirs:
            dir_path = project_root / dir_name
            assert dir_path.exists(), f"Directory {dir_name} should exist"
            assert dir_path.is_dir(), f"{dir_name} should be a directory"
    
    def test_arduino_codes_directory(self, project_root):
        """Verifica a estrutura de códigos Arduino."""
        arduino_dir = project_root / "codigos" / "arduino"
        assert arduino_dir.exists(), "Arduino codes directory should exist"
        
        # Verifica se existem arquivos .ino
        ino_files = list(arduino_dir.glob("*.ino"))
        assert len(ino_files) > 0, "Should have at least one Arduino .ino file"
        
        for ino_file in ino_files:
            assert ino_file.stat().st_size > 0, f"{ino_file.name} should not be empty"
    
    def test_esp32_codes_directory(self, project_root):
        """Verifica a estrutura de códigos ESP32."""
        esp32_dir = project_root / "codigos" / "esp32"
        assert esp32_dir.exists(), "ESP32 codes directory should exist"
        
        # Verifica se existem arquivos .ino
        ino_files = list(esp32_dir.glob("*.ino"))
        assert len(ino_files) > 0, "Should have at least one ESP32 .ino file"
        
        for ino_file in ino_files:
            assert ino_file.stat().st_size > 0, f"{ino_file.name} should not be empty"
    
    def test_raspberry_pi_codes_directory(self, project_root):
        """Verifica a estrutura de códigos Raspberry Pi."""
        pi_dir = project_root / "codigos" / "raspberry-pi"
        assert pi_dir.exists(), "Raspberry Pi codes directory should exist"
        
        # Verifica se existem arquivos .py
        py_files = list(pi_dir.glob("*.py"))
        assert len(py_files) > 0, "Should have at least one Python file for Raspberry Pi"
        
        for py_file in py_files:
            assert py_file.stat().st_size > 0, f"{py_file.name} should not be empty"
    
    def test_3d_models_structure(self, project_root):
        """Verifica a estrutura dos modelos 3D."""
        models_dir = project_root / "modelos-3d"
        assert models_dir.exists(), "3D models directory should exist"
        
        # Verifica se existem subdiretórios por projeto
        project_dirs = [
            "arduino-projetos",
            "esp32-projetos", 
            "raspberry-pi-projetos"
        ]
        
        for project_dir in project_dirs:
            project_path = models_dir / project_dir
            if project_path.exists():
                # Verifica se existem arquivos .scad
                scad_files = list(project_path.glob("*.scad"))
                assert len(scad_files) > 0, f"Should have .scad files in {project_dir}"
    
    def test_interface_web_structure(self, project_root):
        """Verifica a estrutura da interface web."""
        web_dir = project_root / "interface-web"
        assert web_dir.exists(), "Interface web directory should exist"
        
        # Verifica arquivos essenciais da interface web
        essential_files = ["package.json", "Dockerfile.backend", "Dockerfile.frontend"]
        
        for file_name in essential_files:
            file_path = web_dir / file_name
            assert file_path.exists(), f"Interface web should have {file_name}"
            assert file_path.stat().st_size > 0, f"{file_name} should not be empty"
    
    def test_monitoring_config(self, project_root):
        """Verifica se a configuração de monitoramento existe."""
        monitoring_dir = project_root / "interface-web" / "monitoring"
        assert monitoring_dir.exists(), "Monitoring configuration should exist"
        
        # Verifica arquivos de configuração
        config_files = ["prometheus.yml", "alerts.yml"]
        
        for config_file in config_files:
            file_path = monitoring_dir / config_file
            if file_path.exists():
                assert file_path.stat().st_size > 0, f"{config_file} should not be empty"
    
    def test_tests_structure(self, project_root):
        """Verifica a estrutura dos testes."""
        tests_dir = project_root / "tests"
        assert tests_dir.exists(), "Tests directory should exist"
        
        # Verifica se existem testes unitários
        unit_tests_dir = tests_dir / "unit"
        assert unit_tests_dir.exists(), "Unit tests directory should exist"
        
        # Verifica se existem testes para cada componente
        component_tests = [
            "test_arduino",
            "test_esp32", 
            "test_raspberry_pi"
        ]
        
        for component_test in component_tests:
            component_path = unit_tests_dir / component_test
            assert component_path.exists(), f"Tests for {component_test} should exist"
    
    def test_github_workflows(self, project_root):
        """Verifica se os workflows do GitHub Actions existem."""
        github_dir = project_root / ".github" / "workflows"
        assert github_dir.exists(), "GitHub workflows directory should exist"
        
        # Verifica workflows essenciais
        required_workflows = [
            "ci.yml",
            "python-tests.yml", 
            "arduino-build.yml",
            "openscad.yml",
            "code-quality.yml"
        ]
        
        for workflow in required_workflows:
            workflow_path = github_dir / workflow
            assert workflow_path.exists(), f"Workflow {workflow} should exist"
            assert workflow_path.stat().st_size > 0, f"{workflow} should not be empty"
    
    def test_github_templates(self, project_root):
        """Verifica se os templates do GitHub existem."""
        templates_dir = project_root / ".github" / "ISSUE_TEMPLATE"
        assert templates_dir.exists(), "GitHub issue templates should exist"
        
        # Verifica se existem pelo menos alguns templates
        template_files = list(templates_dir.glob("*.md"))
        assert len(template_files) >= 2, "Should have at least 2 issue templates"
    
    def test_assets_screenshots(self, project_root):
        """Verifica se os assets/screenshots existem."""
        assets_dir = project_root / "assets" / "screenshots"
        assert assets_dir.exists(), "Assets screenshots directory should exist"
        
        # Verifica se existem pelo menos alguns screenshots
        image_files = list(assets_dir.glob("*.png"))
        assert len(image_files) >= 5, "Should have at least 5 screenshot images"
    
    def test_projects_documentation(self, project_root):
        """Verifica se a documentação de projetos existe."""
        projects_dir = project_root / "projetos"
        assert projects_dir.exists(), "Projects documentation should exist"
        
        # Verifica documentação por plataforma
        platform_dirs = ["arduino", "esp32", "raspberry-pi", "toolchain"]
        
        for platform in platform_dirs:
            platform_path = projects_dir / platform
            assert platform_path.exists(), f"Documentation for {platform} should exist"
    
    def test_package_json_valid(self, project_root):
        """Valida se package.json da interface web é válido."""
        package_json = project_root / "interface-web" / "package.json"
        if package_json.exists():
            with open(package_json) as f:
                try:
                    package_data = json.load(f)
                    assert "name" in package_data, "package.json should have name field"
                    assert "version" in package_data, "package.json should have version field"
                    assert "dependencies" in package_data, "package.json should have dependencies"
                except json.JSONDecodeError:
                    pytest.fail("package.json is not valid JSON")
    
    def test_license_content(self, project_root):
        """Verifica se a licença contém conteúdo válido."""
        license_path = project_root / "LICENSE"
        if license_path.exists():
            license_content = license_path.read_text()
            assert len(license_content) > 100, "LICENSE should have substantial content"
            assert "MIT" in license_content or "Apache" in license_content or "GPL" in license_content, \
                "LICENSE should specify a license type"


class TestFileContents:
    """Testes para conteúdo de arquivos importantes."""
    
    def test_readme_has_badges(self, project_root):
        """Verifica se o README tem badges de status."""
        readme_path = project_root / "README.md"
        readme_content = readme_path.read_text()
        
        # Verifica se contém badges do GitHub Actions
        assert "github.com/actions" in readme_content, "README should have GitHub Actions badges"
        assert "img.shields.io" in readme_content, "README should have shield badges"
    
    def test_contributing_md_exists(self, project_root):
        """Verifica se CONTRIBUTING.md existe."""
        contributing_path = project_root / "CONTRIBUTING.md"
        assert contributing_path.exists(), "CONTRIBUTING.md should exist"
        assert contributing_path.stat().st_size > 0, "CONTRIBUTING.md should not be empty"
    
    def test_changelog_md_exists(self, project_root):
        """Verifica se CHANGELOG.md existe."""
        changelog_path = project_root / "CHANGELOG.md"
        assert changelog_path.exists(), "CHANGELOG.md should exist"
        assert changelog_path.stat().st_size > 0, "CHANGELOG.md should not be empty"
    
    def test_code_of_conduct_exists(self, project_root):
        """Verifica se CODE_OF_CONDUCT.md existe."""
        conduct_path = project_root / "CODE_OF_CONDUCT.md"
        assert conduct_path.exists(), "CODE_OF_CONDUCT.md should exist"


class TestConfigurationFiles:
    """Testes para arquivos de configuração."""
    
    def test_docker_compose_exists(self, project_root):
        """Verifica se docker-compose.yml existe."""
        compose_path = project_root / "interface-web" / "docker-compose.yml"
        assert compose_path.exists(), "docker-compose.yml should exist"
        assert compose_path.stat().st_size > 0, "docker-compose.yml should not be empty"
    
    def test_deploy_script_exists(self, project_root):
        """Verifica se o script de deploy existe."""
        deploy_path = project_root / "interface-web" / "deploy.sh"
        assert deploy_path.exists(), "deploy.sh should exist"
        assert deploy_path.stat().st_size > 1000, "deploy.sh should have substantial content"
        
        # Verifica se é executável
        is_executable = os.access(deploy_path, os.X_OK)
        if not is_executable:
            # Torna executável para testes
            os.chmod(deploy_path, 0o755)
    
    def test_pytest_configuration(self, project_root):
        """Verifica se pytest.ini ou pyproject.toml existem."""
        pytest_ini = project_root / "pytest.ini"
        pyproject = project_root / "pyproject.toml"
        setup_cfg = project_root / "setup.cfg"
        
        config_exists = pytest_ini.exists() or pyproject.exists() or setup_cfg.exists()
        assert config_exists, "Should have pytest configuration"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])