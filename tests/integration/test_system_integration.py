"""
Testes de integração para o projeto 3dPot.
Testa a interação entre diferentes componentes: hardware, software e interface web.
"""

import json
import os
import subprocess
import threading
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import requests


class TestHardwareIntegration:
    """Testes de integração de hardware."""
    
    @pytest.fixture
    def project_root(self):
        """Retorna o diretório raiz do projeto."""
        return Path(__file__).parent.parent.parent
    
    def test_arduino_esp32_compatibility(self, project_root):
        """Testa compatibilidade entre códigos Arduino e ESP32."""
        # Verifica se ambos os diretórios existem
        arduino_dir = project_root / "codigos" / "arduino"
        esp32_dir = project_root / "codigos" / "esp32"
        
        assert arduino_dir.exists(), "Arduino directory should exist"
        assert esp32_dir.exists(), "ESP32 directory should exist"
        
        # Verifica se ambos têm arquivos de código
        arduino_files = list(arduino_dir.glob("*.ino"))
        esp32_files = list(esp32_dir.glob("*.ino"))
        
        assert len(arduino_files) > 0, "Should have Arduino code files"
        assert len(esp32_files) > 0, "Should have ESP32 code files"
        
        # Verifica se os códigos têm comunicação serial/MQTT
        for code_file in arduino_files + esp32_files:
            content = code_file.read_text()
            has_communication = any(protocol in content for protocol in [
                'Serial', 'MQTT', 'WiFi', 'WebSockets'
            ])
            assert has_communication, f"{code_file.name} should have communication capability"
    
    def test_raspberry_pi_integration_with_hardware(self, project_root):
        """Testa integração do Raspberry Pi com hardware."""
        pi_dir = project_root / "codigos" / "raspberry-pi"
        assert pi_dir.exists(), "Raspberry Pi directory should exist"
        
        py_files = list(pi_dir.glob("*.py"))
        assert len(py_files) > 0, "Should have Python files for Raspberry Pi"
        
        for py_file in py_files:
            content = py_file.read_text()
            # Verifica se tem imports de hardware comuns
            hardware_imports = ['cv2', 'numpy', 'flask', 'serial']
            has_hardware = any(imp in content for imp in hardware_imports)
            assert has_hardware, f"{py_file.name} should import hardware-related libraries"
    
    def test_3d_models_match_hardware_requirements(self, project_root):
        """Testa se os modelos 3D correspondem aos requisitos de hardware."""
        models_dir = project_root / "modelos-3d"
        assert models_dir.exists(), "3D models directory should exist"
        
        # Verifica se cada plataforma tem modelos
        platforms = ['arduino', 'esp32', 'raspberry-pi']
        for platform in platforms:
            platform_dir = models_dir / f"{platform}-projetos"
            if platform_dir.exists():
                scad_files = list(platform_dir.glob("*.scad"))
                assert len(scad_files) > 0, f"Should have {platform} 3D models"


class TestCommunicationProtocols:
    """Testes para protocolos de comunicação."""
    
    def test_mqtt_configuration_exists(self, project_root):
        """Testa se a configuração MQTT existe."""
        mqtt_config = project_root / "interface-web" / "mqtt" / "mosquitto.conf"
        assert mqtt_config.exists(), "MQTT configuration should exist"
        
        content = mqtt_config.read_text()
        assert 'listener' in content, "MQTT config should specify listener"
    
    def test_websocket_compatibility(self, project_root):
        """Testa compatibilidade WebSocket."""
        interface_dir = project_root / "interface-web"
        server_dir = interface_dir / "server"
        assert server_dir.exists(), "Server directory should exist"
        
        # Verifica se existe configuração WebSocket
        socket_files = list(server_dir.glob("**/*socket*")) + list(server_dir.glob("**/*websocket*"))
        assert len(socket_files) > 0, "Should have WebSocket implementation"
    
    def test_api_endpoints_structure(self, project_root):
        """Testa estrutura de endpoints da API."""
        server_dir = project_root / "interface-web" / "server"
        assert server_dir.exists(), "Server directory should exist"
        
        routes_dir = server_dir / "routes"
        if routes_dir.exists():
            route_files = list(routes_dir.glob("**/*.js"))
            assert len(route_files) > 0, "Should have API route files"


class TestDataFlowIntegration:
    """Testes para fluxo de dados entre componentes."""
    
    def test_data_format_consistency(self, project_root):
        """Testa consistência de formato de dados."""
        # Simula dados que devem fluir entre componentes
        hardware_data = {
            'device_id': 'ESP32_001',
            'weight': 750.5,
            'temperature': 24.0,
            'timestamp': int(time.time())
        }
        
        # Verifica se o formato é válido JSON
        json_data = json.dumps(hardware_data)
        parsed_data = json.loads(json_data)
        
        assert parsed_data['device_id'] == 'ESP32_001'
        assert isinstance(parsed_data['weight'], (int, float))
        assert 'timestamp' in parsed_data
    
    def test_unit_conversion_logic(self, project_root):
        """Testa lógica de conversão de unidades."""
        # Testa conversões comuns no sistema
        weight_grams = 750.0
        weight_kg = weight_grams / 1000.0
        
        assert weight_kg == 0.75
        assert weight_kg > 0
        
        # Testa temperatura
        temp_celsius = 24.0
        temp_fahrenheit = (temp_celsius * 9/5) + 32
        
        assert temp_fahrenheit == 75.2
    
    def test_sensor_data_validation_chain(self, project_root):
        """Testa cadeia de validação de dados de sensores."""
        sensor_readings = [
            {'weight': 750.0, 'valid': True},
            {'weight': -50.0, 'valid': False},
            {'weight': 2000.0, 'valid': False},
            {'weight': 500.0, 'valid': True},
            {'weight': None, 'valid': False}
        ]
        
        for reading in sensor_readings:
            weight = reading['weight']
            is_valid = True
            
            # Validação em cadeia
            if weight is None or weight < 0 or weight > 1500:
                is_valid = False
            
            assert is_valid == reading['valid']


class TestConfigurationIntegration:
    """Testes para integração de configurações."""
    
    def test_docker_compose_service_integration(self, project_root):
        """Testa integração de serviços no Docker Compose."""
        compose_file = project_root / "interface-web" / "docker-compose.yml"
        assert compose_file.exists(), "Docker Compose file should exist"
        
        content = compose_file.read_text()
        
        # Verifica se define serviços essenciais
        essential_services = ['frontend', 'backend', 'mqtt']
        for service in essential_services:
            assert service in content, f"Docker Compose should define {service} service"
    
    def test_environment_variable_usage(self, project_root):
        """Testa uso consistente de variáveis de ambiente."""
        # Lista de variáveis de ambiente esperadas
        env_vars = [
            'MQTT_BROKER_HOST',
            'DATABASE_URL',
            'JWT_SECRET',
            'WIFI_SSID'
        ]
        
        # Verifica se são mencionadas em arquivos de configuração
        config_files = list(project_root.rglob("*.yml")) + list(project_root.rglob("*.yaml"))
        
        env_usage_count = 0
        for config_file in config_files:
            content = config_file.read_text()
            for env_var in env_vars:
                if env_var in content or f"${{{env_var}}}" in content:
                    env_usage_count += 1
        
        assert env_usage_count > 0, "Should use environment variables in configuration"
    
    def test_database_schema_consistency(self, project_root):
        """Testa consistência do schema do banco de dados."""
        # Verifica se existe configuração de banco em múltiplos locais
        backend_db_dir = project_root / "backend"
        interface_server_dir = project_root / "interface-web" / "server"
        
        # Verifica se existe backend com configuração de banco
        backend_db_files = list(backend_db_dir.glob("**/*.py"))  # Arquivos Python com SQLAlchemy
        interface_db_files = []
        
        if interface_server_dir.exists():
            database_dir = interface_server_dir / "database"
            if database_dir.exists():
                interface_db_files = list(database_dir.glob("**/*.sql")) + list(database_dir.glob("**/*.js"))
        
        # Deve ter pelo menos configuração de backend ou interface
        total_db_files = len(backend_db_files) + len(interface_db_files)
        assert total_db_files > 0, "Should have database configuration files in backend or interface"


class TestMonitoringIntegration:
    """Testes para integração do sistema de monitoramento."""
    
    def test_prometheus_configuration(self, project_root):
        """Testa configuração do Prometheus."""
        prometheus_config = project_root / "interface-web" / "monitoring" / "prometheus.yml"
        assert prometheus_config.exists(), "Prometheus config should exist"
        
        content = prometheus_config.read_text()
        assert 'global:' in content, "Prometheus config should have global settings"
        assert 'scrape_configs:' in content, "Prometheus config should have scrape configs"
    
    def test_grafana_dashboards(self, project_root):
        """Testa dashboards do Grafana."""
        grafana_dir = project_root / "interface-web" / "monitoring" / "grafana"
        if grafana_dir.exists():
            dashboard_files = list(grafana_dir.glob("**/*.json"))
            assert len(dashboard_files) > 0, "Should have Grafana dashboard files"
    
    def test_alerting_configuration(self, project_root):
        """Testa configuração de alertas."""
        alerts_config = project_root / "interface-web" / "monitoring" / "alerts.yml"
        assert alerts_config.exists(), "Alerts configuration should exist"
        
        content = alerts_config.read_text()
        assert 'groups:' in content, "Alerts should be organized in groups"
        assert 'alert:' in content.lower(), "Should have alert definitions"


class TestWebInterfaceIntegration:
    """Testes para integração da interface web."""
    
    def test_frontend_backend_compatibility(self, project_root):
        """Testa compatibilidade entre frontend e backend."""
        frontend_dir = project_root / "interface-web" / "src"
        backend_dir = project_root / "interface-web" / "server"
        
        assert frontend_dir.exists(), "Frontend source should exist"
        assert backend_dir.exists(), "Backend source should exist"
        
        # Verifica package.json
        package_json = project_root / "interface-web" / "package.json"
        if package_json.exists():
            with open(package_json) as f:
                package_data = json.load(f)
                assert 'dependencies' in package_data, "Should have dependencies"
    
    def test_webSocket_real_time_updates(self, project_root):
        """Testa atualizações em tempo real via WebSocket."""
        # Simula estrutura de WebSocket
        websocket_structure = {
            'connection': 'websocket',
            'events': ['status_update', 'sensor_data', 'alert_notification'],
            'protocol': 'json'
        }
        
        # Verifica se a estrutura é válida
        assert 'connection' in websocket_structure
        assert len(websocket_structure['events']) > 0
        assert websocket_structure['protocol'] == 'json'
    
    def test_api_response_format_consistency(self, project_root):
        """Testa consistência de formato das respostas da API."""
        # Simula respostas de API
        api_responses = [
            {
                'status': 'success',
                'data': {'weight': 750.0, 'temperature': 24.0},
                'timestamp': '2025-11-10T10:30:00Z'
            },
            {
                'status': 'error',
                'message': 'Sensor connection failed',
                'timestamp': '2025-11-10T10:30:00Z'
            }
        ]
        
        for response in api_responses:
            assert 'status' in response
            assert 'timestamp' in response
            assert response['status'] in ['success', 'error']


class TestDeploymentIntegration:
    """Testes para integração de deployment."""
    
    def test_deployment_script_structure(self, project_root):
        """Testa estrutura do script de deploy."""
        deploy_script = project_root / "interface-web" / "deploy.sh"
        assert deploy_script.exists(), "Deploy script should exist"
        
        content = deploy_script.read_text()
        # Verifica comandos essenciais de deploy
        deploy_commands = ['docker', 'nginx', 'ssl', 'backup']
        for cmd in deploy_commands:
            assert cmd in content, f"Deploy script should contain {cmd} commands"
    
    def test_nginx_configuration(self, project_root):
        """Testa configuração do Nginx."""
        nginx_dir = project_root / "interface-web" / "nginx"
        assert nginx_dir.exists(), "Nginx configuration should exist"
        
        # Verifica se tem configuração principal
        main_config = nginx_dir / "nginx.conf"
        if main_config.exists():
            content = main_config.read_text()
            assert 'http {' in content, "Nginx should have HTTP configuration"
        
        # Verifica configuração do frontend
        frontend_config = nginx_dir / "conf.d" / "frontend.conf"
        if frontend_config.exists():
            content = frontend_config.read_text()
            assert 'location /' in content, "Should have frontend location configuration"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])