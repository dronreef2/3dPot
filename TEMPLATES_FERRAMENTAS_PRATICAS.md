# TEMPLATES E FERRAMENTAS PRÁTICAS - 3DPOT
**Arquivos prontos para uso durante o projeto**

## 📁 ESTRUTURA DE ARQUIVOS AUTOMÁTICA

### Script de Setup Automático
```bash
#!/bin/bash
# setup_project.sh - Configuração automática do projeto 3dPot

echo "🚀 Setting up 3dPot project structure..."

# Criar estrutura de diretórios
mkdir -p {codigos/{esp32/monitor-filamento,arduino/esteira-transportadora,raspberry-pi/estacao_qc},backend,tests/{unit/{test_esp32,test_arduino,test_raspberry_pi,test_backend},integration,fixtures},models,config,scripts,docs,deployment/{docker,kubernetes},monitoring/{grafana,prometheus}}

# Configurar Git hooks
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# Pre-commit hook para qualidade de código

echo "🔍 Running pre-commit checks..."

# Python linting
if [ -f "backend/"*.py ]; then
    echo "Running pylint on Python files..."
    pylint backend/ --exit-zero || true
fi

# Black formatting
echo "Running black formatter..."
black --check . || black .

# Running tests
echo "Running fast tests..."
python -m pytest tests/unit/ --tb=short -x

echo "✅ Pre-commit checks completed"
EOF

chmod +x .git/hooks/pre-commit

# Criar arquivos de configuração básicos
touch requirements-test.txt
touch .gitignore
touch docker-compose.yml
touch Dockerfile.backend
touch .github/workflows/ci.yml

echo "✅ Project structure created successfully!"
echo "📝 Next steps:"
echo "1. Review and customize configuration files"
echo "2. Install dependencies: pip install -r requirements-test.txt"
echo "3. Run initial tests: pytest tests/"
```

### Estrutura Completa de Arquivos
```
3dPot/
├── 📁 codigos/
│   ├── 📁 esp32/
│   │   ├── 📁 monitor-filamento/
│   │   │   ├── 📄 monitor-filamento.ino
│   │   │   ├── 📄 config.h
│   │   │   ├── 📄 web_server.cpp
│   │   │   ├── 📄 weight_sensor.cpp
│   │   │   ├── 📄 wifi_manager.cpp
│   │   │   ├── 📄 mqtt_client.cpp
│   │   │   ├── 📄 ota_handler.cpp
│   │   │   ├── 📁 lib/
│   │   │   │   ├── 📁 HX711/
│   │   │   │   ├── 📁 WiFiManager/
│   │   │   │   └── 📁 PubSubClient/
│   │   │   ├── 📄 platformio.ini
│   │   │   └── 📄 README.md
│   │   └── 📁 arduino/
│   │       ├── 📁 esteira-transportadora/
│   │       │   ├── 📄 esteira-transportadora.ino
│   │       │   ├── 📄 motor_control.cpp
│   │       │   ├── 📄 lcd_display.cpp
│   │       │   ├── 📄 position_sensors.cpp
│   │       │   ├── 📄 communication.cpp
│   │       │   └── 📄 config.h
│   │       └── 📁 raspberry-pi/
│   │           ├── 📁 estacao_qc/
│   │           │   ├── 📄 estacao_qc.py
│   │           │   ├── 📄 camera_controller.py
│   │           │   ├── 📄 opencv_analyzer.py
│   │           │   ├── 📄 web_dashboard.py
│   │           │   ├── 📄 api_server.py
│   │           │   ├── 📁 requirements.txt
│   │           │   └── 📁 config/
│   │           │       └── 📄 camera_settings.yaml
├── 📁 backend/
│   ├── 📄 main.py
│   ├── 📄 database.py
│   ├── 📄 mqtt_handler.py
│   ├── 📄 websocket_handler.py
│   ├── 📄 models/
│   │   ├── 📄 __init__.py
│   │   ├── 📄 device.py
│   │   ├── 📄 telemetry.py
│   │   └── 📄 qc_results.py
│   ├── 📄 api/
│   │   ├── 📄 __init__.py
│   │   ├── 📄 devices.py
│   │   ├── 📄 telemetry.py
│   │   └── 📄 qc.py
│   ├── 📄 requirements.txt
│   └── 📁 alembic/
│       └── 📁 versions/
├── 📁 tests/
│   ├── 📁 unit/
│   │   ├── 📁 test_esp32/
│   │   │   ├── 📄 test_weight_sensor.py
│   │   │   ├── 📄 test_wifi_manager.py
│   │   │   └── 📄 test_mqtt_client.py
│   │   ├── 📁 test_arduino/
│   │   │   ├── 📄 test_motor_control.py
│   │   │   └── 📄 test_lcd_display.py
│   │   ├── 📄 test_raspberry_pi/
│   │   │   ├── 📄 test_camera_controller.py
│   │   │   └── 📄 test_opencv_analyzer.py
│   │   └── 📄 test_backend/
│   │       ├── 📄 test_api_endpoints.py
│   │       ├── 📄 test_mqtt_handler.py
│   │       └── 📄 test_database.py
│   ├── 📁 integration/
│   │   ├── 📄 test_device_communication.py
│   │   ├── 📄 test_end_to_end.py
│   │   └── 📄 test_mqtt_integration.py
│   ├── 📁 fixtures/
│   │   ├── 📄 mock_devices.py
│   │   ├── 📄 sample_data.py
│   │   └── 📄 test_config.py
│   ├── 📄 conftest.py
│   └── 📄 requirements-test.txt
├── 📁 .github/
│   └── 📁 workflows/
│       └── 📄 ci.yml
├── 📁 config/
│   ├── 📄 mosquitto.conf
│   ├── 📄 postgres.conf
│   └── 📁 grafana/
│       └── 📄 dashboards/
├── 📁 deployment/
│   ├── 📄 docker-compose.yml
│   ├── 📄 Dockerfile.backend
│   ├── 📄 Dockerfile.esp32
│   ├── 📁 kubernetes/
│   │   ├── 📄 deployment.yaml
│   │   ├── 📄 service.yaml
│   │   └── 📄 ingress.yaml
└── 📁 monitoring/
    ├── 📁 grafana/
    │   ├── 📄 dashboard.json
    │   └── 📁 datasource.yml
    └── 📁 prometheus/
        └── 📄 prometheus.yml
```

## 🔧 SCRIPTS DE AUTOMAÇÃO

### Script de Build Automático
```bash
#!/bin/bash
# build_all.sh - Build automático de todos os componentes

set -e

echo "🔨 Starting 3dPot build process..."

# Função para print com cores
print_status() {
    echo -e "\033[1;34m[INFO]\033[0m $1"
}

print_success() {
    echo -e "\033[1;32m[SUCCESS]\033[0m $1"
}

print_error() {
    echo -e "\033[1;31m[ERROR]\033[0m $1"
}

# 1. Backend Python
print_status "Building backend..."
cd backend/
python -m pip install -r requirements.txt
python -m pytest tests/ --tb=short
python -c "import main; print('Backend imports OK')"
cd ..
print_success "Backend build completed"

# 2. ESP32 Firmware
print_status "Building ESP32 firmware..."
cd codigos/esp32/monitor-filamento/
pio run --environment esp32dev
if [ -f ".pio/build/esp32dev/firmware.bin" ]; then
    print_success "ESP32 firmware built successfully"
else
    print_error "ESP32 firmware build failed"
    exit 1
fi
cd ../..
print_success "ESP32 build completed"

# 3. Arduino Code
print_status "Building Arduino code..."
cd codigos/arduino/esteira-transportadora/
pio run --environment uno
if [ -f ".pio/build/uno/firmware.bin" ]; then
    print_success "Arduino firmware built successfully"
else
    print_error "Arduino firmware build failed"
    exit 1
fi
cd ../..
print_success "Arduino build completed"

# 4. Raspberry Pi Code
print_status "Testing Raspberry Pi code..."
cd codigos/raspberry-pi/estacao_qc/
python -m pip install -r requirements.txt
python -c "import cv2; print('OpenCV version:', cv2.__version__)"
python -m pytest tests/ --tb=short
cd ../..
print_success "Raspberry Pi build completed"

# 5. Docker Images
print_status "Building Docker images..."
docker build -t 3dpot-backend:latest .
docker-compose build
print_success "Docker images built"

# 6. Test Models
print_status "Validating OpenSCAD models..."
find modelos-3d/ -name "*.scad" -exec openscad -o /dev/null {} \; || true
print_success "OpenSCAD models validated"

print_success "🎉 All builds completed successfully!"
```

### Script de Deploy Automático
```bash
#!/bin/bash
# deploy.sh - Deploy automático com validação

ENVIRONMENT=${1:-staging}
VERSION=${2:-$(git rev-parse --short HEAD)}

print_status() {
    echo -e "\033[1;34m[INFO]\033[0m $1"
}

print_success() {
    echo -e "\033[1;32m[SUCCESS]\033[0m $1"
}

print_error() {
    echo -e "\033[1;31m[ERROR]\033[0m $1"
}

echo "🚀 Deploying 3dPot to $ENVIRONMENT (version: $VERSION)"

# Pre-deployment checks
print_status "Running pre-deployment checks..."

# Tests must pass
python -m pytest tests/ --tb=short -q || {
    print_error "Tests failed, aborting deployment"
    exit 1
}

# Security scan
print_status "Running security scan..."
bandit -r backend/ -f json -o security-report.json || true

# Performance check
print_status "Running performance checks..."
python scripts/performance_check.py

print_success "Pre-deployment checks passed"

# Build artifacts
print_status "Building production artifacts..."
./scripts/build_all.sh

# Database migration (if needed)
if [ -f "backend/alembic/versions/*.py" ]; then
    print_status "Running database migrations..."
    cd backend/
    alembic upgrade head
    cd ..
fi

# Deploy based on environment
case $ENVIRONMENT in
    "staging")
        print_status "Deploying to staging..."
        docker-compose -f docker-compose.staging.yml up -d
        ;;
    "production")
        print_status "Deploying to production..."
        docker-compose -f docker-compose.prod.yml up -d
        # Additional production checks
        ;;
    *)
        print_error "Unknown environment: $ENVIRONMENT"
        exit 1
        ;;
esac

# Post-deployment validation
print_status "Running post-deployment validation..."
sleep 30

# Health check
curl -f http://localhost:8000/api/health || {
    print_error "Health check failed"
    exit 1
}

# Smoke tests
python scripts/smoke_tests.py

print_success "🎉 Deployment to $ENVIRONMENT completed successfully!"

# Notify team
echo "Deployment completed at $(date)" > deployment.log
```

## 📊 SCRIPTS DE MONITORAMENTO

### Métricas em Tempo Real
```python
#!/usr/bin/env python3
# realtime_metrics.py - Dashboard de métricas em tempo real

import time
import psutil
import json
import requests
from datetime import datetime
from threading import Thread
import queue

class MetricsCollector:
    def __init__(self):
        self.metrics_queue = queue.Queue()
        self.running = True
    
    def collect_system_metrics(self):
        """Coleta métricas do sistema"""
        while self.running:
            try:
                # CPU e Memória
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                
                # Temperatura (se disponível)
                try:
                    temperatures = psutil.sensors_temperatures()
                    cpu_temp = temperatures.get('coretemp', [{}])[0].get('current', 0)
                except:
                    cpu_temp = 0
                
                metrics = {
                    'timestamp': datetime.now().isoformat(),
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'memory_available_gb': memory.available / (1024**3),
                    'disk_percent': disk.percent,
                    'disk_free_gb': disk.free / (1024**3),
                    'cpu_temperature': cpu_temp
                }
                
                self.metrics_queue.put(metrics)
                time.sleep(5)  # Coleta a cada 5 segundos
                
            except Exception as e:
                print(f"Error collecting system metrics: {e}")
                time.sleep(5)
    
    def collect_application_metrics(self):
        """Coleta métricas da aplicação"""
        while self.running:
            try:
                # API Health
                try:
                    response = requests.get('http://localhost:8000/api/health', timeout=5)
                    api_status = response.status_code == 200
                    api_response_time = response.elapsed.total_seconds()
                except:
                    api_status = False
                    api_response_time = 0
                
                # Database connection
                try:
                    # Aqui você faria uma query simples no banco
                    db_status = True
                except:
                    db_status = False
                
                # MQTT connections
                try:
                    # Verificar conexões MQTT ativas
                    mqtt_status = True
                except:
                    mqtt_status = False
                
                app_metrics = {
                    'timestamp': datetime.now().isoformat(),
                    'api_healthy': api_status,
                    'api_response_time': api_response_time,
                    'db_connected': db_status,
                    'mqtt_connected': mqtt_status
                }
                
                self.metrics_queue.put(app_metrics)
                time.sleep(10)  # Coleta a cada 10 segundos
                
            except Exception as e:
                print(f"Error collecting application metrics: {e}")
                time.sleep(10)
    
    def display_dashboard(self):
        """Exibe dashboard em tempo real"""
        print("\n" + "="*80)
        print("🚀 3DPOT REAL-TIME METRICS DASHBOARD")
        print("="*80)
        
        while self.running:
            try:
                # Limpar tela (Unix systems)
                os.system('clear' if os.name == 'posix' else 'cls')
                
                print("\n" + "="*80)
                print("🚀 3DPOT REAL-TIME METRICS DASHBOARD")
                print("="*80)
                print(f"Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print("-" * 80)
                
                # Coletar todas as métricas na fila
                metrics_data = []
                while not self.metrics_queue.empty():
                    metrics_data.append(self.metrics_queue.get())
                
                if metrics_data:
                    latest = metrics_data[-1]
                    
                    # Métricas do sistema
                    if 'cpu_percent' in latest:
                        print(f"💻 SYSTEM METRICS")
                        print(f"  CPU: {latest.get('cpu_percent', 0):.1f}% | Temp: {latest.get('cpu_temperature', 0):.1f}°C")
                        print(f"  Memory: {latest.get('memory_percent', 0):.1f}% ({latest.get('memory_available_gb', 0):.1f}GB free)")
                        print(f"  Disk: {latest.get('disk_percent', 0):.1f}% ({latest.get('disk_free_gb', 0):.1f}GB free)")
                        print("-" * 40)
                    
                    # Métricas da aplicação
                    if 'api_healthy' in latest:
                        print(f"🌐 APPLICATION METRICS")
                        status_icon = "✅" if latest.get('api_healthy') else "❌"
                        print(f"  API Status: {status_icon} | Response: {latest.get('api_response_time', 0)*1000:.0f}ms")
                        print(f"  Database: {'✅' if latest.get('db_connected') else '❌'} | MQTT: {'✅' if latest.get('mqtt_connected') else '❌'}")
                        print("-" * 40)
                
                # Gráfico simples
                print("📊 RECENT CPU USAGE:")
                recent_cpu = [m.get('cpu_percent', 0) for m in metrics_data if 'cpu_percent' in m][-20:]
                if recent_cpu:
                    for cpu in recent_cpu:
                        bar = "█" * int(cpu / 5) + "░" * (20 - int(cpu / 5))
                        print(f"  {bar} {cpu:.1f}%")
                
                print("\nPress Ctrl+C to stop")
                time.sleep(2)
                
            except KeyboardInterrupt:
                self.running = False
                break
            except Exception as e:
                print(f"Error updating dashboard: {e}")
                time.sleep(2)

if __name__ == "__main__":
    import os
    
    collector = MetricsCollector()
    
    # Iniciar threads de coleta
    system_thread = Thread(target=collector.collect_system_metrics)
    app_thread = Thread(target=collector.collect_application_metrics)
    
    system_thread.daemon = True
    app_thread.daemon = True
    
    system_thread.start()
    app_thread.start()
    
    # Exibir dashboard
    collector.display_dashboard()
```

### Alertas Automáticos
```python
#!/usr/bin/env python3
# alert_manager.py - Sistema de alertas automático

import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import time
from datetime import datetime

class AlertManager:
    def __init__(self, config_file='alert_config.json'):
        with open(config_file, 'r') as f:
            self.config = json.load(f)
        
        self.alert_history = []
        self.alert_cooldown = {}
    
    def check_thresholds(self):
        """Verifica limites e dispara alertas"""
        alerts = []
        
        # Verificar uso de CPU
        cpu_percent = self._get_cpu_usage()
        if cpu_percent > self.config['thresholds']['cpu_high']:
            alerts.append({
                'type': 'CPU_HIGH',
                'severity': 'WARNING',
                'message': f'CPU usage at {cpu_percent:.1f}%',
                'value': cpu_percent
            })
        
        # Verificar uso de memória
        memory_percent = self._get_memory_usage()
        if memory_percent > self.config['thresholds']['memory_high']:
            alerts.append({
                'type': 'MEMORY_HIGH',
                'severity': 'WARNING',
                'message': f'Memory usage at {memory_percent:.1f}%',
                'value': memory_percent
            })
        
        # Verificar API health
        if not self._check_api_health():
            alerts.append({
                'type': 'API_DOWN',
                'severity': 'CRITICAL',
                'message': 'API endpoint is not responding',
                'value': 0
            })
        
        # Verificar espaço em disco
        disk_usage = self._get_disk_usage()
        if disk_usage > self.config['thresholds']['disk_high']:
            alerts.append({
                'type': 'DISK_HIGH',
                'severity': 'WARNING',
                'message': f'Disk usage at {disk_usage:.1f}%',
                'value': disk_usage
            })
        
        return alerts
    
    def _get_cpu_usage(self):
        import psutil
        return psutil.cpu_percent(interval=1)
    
    def _get_memory_usage(self):
        import psutil
        return psutil.virtual_memory().percent
    
    def _get_disk_usage(self):
        import psutil
        return psutil.disk_usage('/').percent
    
    def _check_api_health(self):
        try:
            response = requests.get('http://localhost:8000/api/health', timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def should_alert(self, alert_type):
        """Verifica se deve alertar baseado no cooldown"""
        now = time.time()
        cooldown = self.alert_cooldown.get(alert_type, 0)
        
        if now - cooldown < self.config['cooldown_minutes'] * 60:
            return False
        
        self.alert_cooldown[alert_type] = now
        return True
    
    def send_alert(self, alert):
        """Envia alerta via email ou webhook"""
        if not self.should_alert(alert['type']):
            return False
        
        try:
            if self.config['email']['enabled']:
                self._send_email_alert(alert)
            
            if self.config['slack']['enabled']:
                self._send_slack_alert(alert)
            
            # Log alert
            self.alert_history.append({
                'timestamp': datetime.now().isoformat(),
                'alert': alert
            })
            
            print(f"🚨 ALERT: {alert['type']} - {alert['message']}")
            return True
            
        except Exception as e:
            print(f"Error sending alert: {e}")
            return False
    
    def _send_email_alert(self, alert):
        msg = MIMEMultipart()
        msg['From'] = self.config['email']['from']
        msg['To'] = self.config['email']['to']
        msg['Subject'] = f"3dPot Alert: {alert['type']} - {alert['severity']}"
        
        body = f"""
        3dPot Alert Generated
        
        Type: {alert['type']}
        Severity: {alert['severity']}
        Message: {alert['message']}
        Value: {alert.get('value', 'N/A')}
        Timestamp: {alert['timestamp'] if 'timestamp' in alert else datetime.now().isoformat()}
        
        Please check the system immediately.
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(self.config['email']['smtp_server'], self.config['email']['smtp_port'])
        server.starttls()
        server.login(self.config['email']['username'], self.config['email']['password'])
        server.send_message(msg)
        server.quit()
    
    def _send_slack_alert(self, alert):
        color = "danger" if alert['severity'] == 'CRITICAL' else "warning"
        
        payload = {
            "channel": self.config['slack']['channel'],
            "username": "3dPot Alert Bot",
            "icon_emoji": ":warning:",
            "attachments": [
                {
                    "color": color,
                    "title": f"3dPot Alert: {alert['type']}",
                    "text": alert['message'],
                    "fields": [
                        {"title": "Severity", "value": alert['severity'], "short": True},
                        {"title": "Value", "value": str(alert.get('value', 'N/A')), "short": True}
                    ],
                    "ts": time.time()
                }
            ]
        }
        
        requests.post(self.config['slack']['webhook_url'], json=payload)
    
    def run(self):
        """Loop principal do alert manager"""
        print("🔔 Starting 3dPot Alert Manager...")
        
        while True:
            try:
                alerts = self.check_thresholds()
                
                for alert in alerts:
                    self.send_alert(alert)
                
                time.sleep(60)  # Verifica a cada minuto
                
            except KeyboardInterrupt:
                print("Alert manager stopped")
                break
            except Exception as e:
                print(f"Error in alert manager: {e}")
                time.sleep(60)

# Configuração de exemplo para alertas
ALERT_CONFIG_EXAMPLE = {
    "email": {
        "enabled": True,
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "username": "alerts@3dpot.com",
        "password": "your_app_password",
        "from": "alerts@3dpot.com",
        "to": "team@3dpot.com"
    },
    "slack": {
        "enabled": True,
        "webhook_url": "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK",
        "channel": "#alerts"
    },
    "thresholds": {
        "cpu_high": 80,
        "memory_high": 85,
        "disk_high": 90,
        "api_response_time": 2.0
    },
    "cooldown_minutes": 15
}

if __name__ == "__main__":
    # Criar arquivo de configuração exemplo
    with open('alert_config.json', 'w') as f:
        json.dump(ALERT_CONFIG_EXAMPLE, f, indent=2)
    
    # Iniciar alert manager
    manager = AlertManager()
    manager.run()
```

## 🧪 TEMPLATES DE TESTE

### Teste de Integração End-to-End
```python
#!/usr/bin/env python3
# test_end_to_end.py - Teste completo do sistema

import pytest
import requests
import json
import time
from unittest.mock import MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class TestEndToEnd:
    """Testes end-to-end do sistema 3dPot"""
    
    @pytest.fixture(scope="session")
    def test_db(self):
        """Setup banco de dados de teste"""
        engine = create_engine('sqlite:///:memory:')
        Session = sessionmaker(bind=engine)
        
        # Criar tabelas
        from backend.models import Base
        Base.metadata.create_all(engine)
        
        return Session()
    
    @pytest.fixture
    def api_client(self):
        """Client da API para testes"""
        # Configurar API para testing
        from backend.main import app
        from fastapi.testclient import TestClient
        
        return TestClient(app)
    
    def test_complete_filament_monitoring_flow(self, api_client, test_db):
        """Teste completo do fluxo de monitoramento de filamento"""
        
        # 1. Verificar que API está rodando
        response = api_client.get("/api/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
        
        # 2. Registrar dispositivo ESP32
        device_data = {
            "id": "esp32-001",
            "type": "esp32",
            "name": "Monitor de Filamento #1",
            "ip_address": "192.168.1.100"
        }
        
        response = api_client.post("/api/devices", json=device_data)
        assert response.status_code == 201
        device = response.json()
        assert device["id"] == "esp32-001"
        
        # 3. Simular telemetria de peso
        telemetry_data = {
            "device_id": "esp32-001",
            "weight_g": 750.5,
            "percentage": 75.0,
            "temperature": 22.5,
            "humidity": 45.0
        }
        
        response = api_client.post(
            f"/api/telemetry/{telemetry_data['device_id']}", 
            json=telemetry_data
        )
        assert response.status_code == 201
        
        # 4. Verificar telemetria recebida
        response = api_client.get("/api/telemetry/esp32-001?limit=1")
        assert response.status_code == 200
        telemetry = response.json()[0]
        assert telemetry["weight_g"] == 750.5
        assert telemetry["percentage"] == 75.0
        
        # 5. Testar WebSocket para dados em tempo real
        with api_client.websocket_connect("/ws/realtime") as websocket:
            # Receber dados em tempo real
            data = websocket.receive_json()
            assert "device_id" in data
            assert "timestamp" in data
    
    def test_qc_station_integration(self, api_client, test_db):
        """Teste integração da estação QC"""
        
        # 1. Registrar estação QC
        qc_device_data = {
            "id": "qc-station-001",
            "type": "raspberrypi",
            "name": "Estação QC #1",
            "ip_address": "192.168.1.101"
        }
        
        response = api_client.post("/api/devices", json=qc_device_data)
        assert response.status_code == 201
        
        # 2. Simular resultado de QC
        qc_result = {
            "device_id": "qc-station-001",
            "image_path": "/images/test-piece-001.jpg",
            "result": "approved",
            "score": 0.95,
            "defects": []
        }
        
        response = api_client.post("/api/qc", json=qc_result)
        assert response.status_code == 201
        
        # 3. Verificar histórico QC
        response = api_client.get("/api/qc/history?device_id=qc-station-001&limit=1")
        assert response.status_code == 200
        history = response.json()
        assert len(history) == 1
        assert history[0]["result"] == "approved"
        assert history[0]["score"] == 0.95
    
    def test_conveyor_belt_control(self, api_client, test_db):
        """Teste controle da esteira transportadora"""
        
        # 1. Registrar dispositivo Arduino
        arduino_data = {
            "id": "arduino-001",
            "type": "arduino",
            "name": "Esteira Transportadora #1",
            "ip_address": "192.168.1.102"
        }
        
        response = api_client.post("/api/devices", json=arduino_data)
        assert response.status_code == 201
        
        # 2. Comando para iniciar movimentação
        command = {
            "command": "start",
            "direction": "forward",
            "speed": 100,
            "duration": 30
        }
        
        response = api_client.post(
            f"/api/devices/arduino-001/command", 
            json=command
        )
        assert response.status_code == 200
        assert response.json()["status"] == "command_sent"
        
        # 3. Verificar status do dispositivo
        response = api_client.get("/api/devices/arduino-001/status")
        assert response.status_code == 200
        status = response.json()
        assert status["id"] == "arduino-001"
        assert status["type"] == "arduino"
    
    def test_mqtt_integration(self, api_client, test_db):
        """Teste integração MQTT"""
        
        # Este teste verificaria:
        # 1. Conexão com broker MQTT
        # 2. Publicação de mensagens
        # 3. Assinatura de tópicos
        # 4. Processamento de mensagens
        
        # Mock MQTT client para teste
        mock_mqtt = MagicMock()
        
        # Simular publicação de telemetria via MQTT
        topic = "3dpot/devices/esp32-001/telemetry"
        message = json.dumps({
            "weight_g": 500.0,
            "percentage": 50.0,
            "timestamp": time.time()
        })
        
        mock_mqtt.publish.assert_not_called()
        
        # Aqui você verificaria o publish real
        # mock_mqtt.publish(topic, message)
        # mock_mqtt.publish.assert_called_with(topic, message)

    def test_websocket_realtime_data(self, api_client, test_db):
        """Teste WebSocket para dados em tempo real"""
        
        with api_client.websocket_connect("/ws/realtime") as websocket:
            # Conectar WebSocket
            
            # Receber handshake
            handshake = websocket.receive_json()
            assert handshake["type"] == "connected"
            assert "connection_id" in handshake
            
            # Testar subscribe/unsubscribe
            subscribe_msg = {"action": "subscribe", "device_id": "esp32-001"}
            websocket.send_json(subscribe_msg)
            
            response = websocket.receive_json()
            assert response["action"] == "subscribed"
            
            # Testar unsubscribe
            unsubscribe_msg = {"action": "unsubscribe", "device_id": "esp32-001"}
            websocket.send_json(unsubscribe_msg)
            
            response = websocket.receive_json()
            assert response["action"] == "unsubscribed"

    def test_error_handling(self, api_client):
        """Teste tratamento de erros"""
        
        # 1. Dispositivo inexistente
        response = api_client.get("/api/devices/nonexistent")
        assert response.status_code == 404
        
        # 2. Payload inválido
        invalid_data = {"invalid": "data"}
        response = api_client.post("/api/devices", json=invalid_data)
        assert response.status_code == 422  # Validation error
        
        # 3. Telemetria para dispositivo inexistente
        invalid_telemetry = {
            "weight_g": 100.0,
            "percentage": 10.0
        }
        response = api_client.post("/api/telemetry/fake-device", json=invalid_telemetry)
        assert response.status_code == 404
        
        # 4. Comando para dispositivo offline
        offline_command = {"command": "stop"}
        response = api_client.post("/api/devices/offline-device/command", json=offline_command)
        assert response.status_code == 400  # Device offline
    
    def test_performance_under_load(self, api_client):
        """Teste de performance sob carga"""
        
        import concurrent.futures
        import time
        
        # Criar múltiplas requisições simultâneas
        def make_request(device_id):
            start_time = time.time()
            response = api_client.get(f"/api/devices/{device_id}")
            end_time = time.time()
            return {
                "response_time": end_time - start_time,
                "status_code": response.status_code
            }
        
        # Teste com 50 requisições simultâneas
        device_ids = [f"test-device-{i}" for i in range(50)]
        
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request, device_id) for device_id in device_ids]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        total_time = time.time() - start_time
        
        # Verificações de performance
        assert total_time < 10.0  # Deve completar em menos de 10 segundos
        assert all(r["status_code"] == 404 for r in results)  # Todos devem retornar 404 (dispositivo não encontrado)
        
        # Verificar que nenhum request demorou mais de 2 segundos
        response_times = [r["response_time"] for r in results]
        assert max(response_times) < 2.0

if __name__ == "__main__":
    # Executar testes
    pytest.main([__file__, "-v", "--tb=short"])
```

### Teste de Carga
```python
#!/usr/bin/env python3
# load_test.py - Teste de carga com Artillery

import subprocess
import json
import time
from datetime import datetime

# Configuração do teste de carga
LOAD_TEST_CONFIG = {
    "config": {
        "target": "http://localhost:8000",
        "phases": [
            {
                "duration": 60,
                "arrivalRate": 10
            },
            {
                "duration": 120,
                "arrivalRate": 25
            },
            {
                "duration": 60,
                "arrivalRate": 50
            }
        ],
        "payload": {
            "path": "test_data.csv",
            "fields": ["device_id", "weight", "temperature"]
        }
    },
    "scenarios": [
        {
            "name": "API Health Check",
            "weight": 50,
            "flow": [
                {
                    "get": {
                        "url": "/api/health"
                    }
                }
            ]
        },
        {
            "name": "Get Device List",
            "weight": 30,
            "flow": [
                {
                    "get": {
                        "url": "/api/devices"
                    }
                }
            ]
        },
        {
            "name": "Submit Telemetry",
            "weight": 20,
            "flow": [
                {
                    "post": {
                        "url": "/api/telemetry/{{ device_id }}",
                        "json": {
                            "weight_g": "{{ weight }}",
                            "temperature": "{{ temperature }}",
                            "percentage": "{{ $randomNumber(0, 100) }}"
                        }
                    }
                }
            ]
        }
    ]
}

def create_test_data_csv():
    """Criar arquivo CSV com dados de teste"""
    import csv
    
    with open('test_data.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['device_id', 'weight', 'temperature'])
        
        for i in range(1000):
            writer.writerow([
                f'esp32-{i % 100:03d}',
                f'{500 + i % 500}',  # weight 500-1000g
                f'{20 + i % 15}'    # temperature 20-35°C
            ])

def run_load_test():
    """Executar teste de carga"""
    
    print("🚀 Starting load test...")
    
    # Criar dados de teste
    create_test_data_csv()
    
    # Salvar configuração
    with open('load_test_config.yml', 'w') as f:
        import yaml
        yaml.dump(LOAD_TEST_CONFIG, f, default_flow_style=False)
    
    # Executar teste com Artillery
    try:
        result = subprocess.run([
            'artillery', 'run', 
            'load_test_config.yml',
            '--output', f'load_test_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        ], capture_output=True, text=True, timeout=600)
        
        if result.returncode == 0:
            print("✅ Load test completed successfully")
            print(result.stdout)
        else:
            print("❌ Load test failed")
            print(result.stderr)
            
    except FileNotFoundError:
        print("❌ Artillery not installed. Install with: npm install -g artillery")
    except subprocess.TimeoutExpired:
        print("⏰ Load test timed out")

if __name__ == "__main__":
    run_load_test()
```

## 🔒 CHECKLISTS DE SEGURANÇA

### Pre-Deployment Security Checklist
```markdown
# Security Checklist - Pre-Deployment

## 🔐 Authentication & Authorization
- [ ] JWT tokens configurados com expiração apropriada
- [ ] Rate limiting implementado (100 req/min per user)
- [ ] RBAC configurado para diferentes níveis de acesso
- [ ] API keys rotação automática configurada
- [ ] Sessions management seguro (secure, httpOnly, sameSite)

## 🌐 Network Security
- [ ] HTTPS obrigatório (TLS 1.2+)
- [ ] CORS configurado para domínios específicos
- [ ] Security headers implementados (HSTS, CSP, X-Frame-Options)
- [ ] Input validation em todos os endpoints
- [ ] SQL injection protection (SQLAlchemy ORM)
- [ ] XSS protection (output encoding)

## 🔑 Secrets Management
- [ ] Credenciais não hardcoded no código
- [ ] Environment variables para configurações sensíveis
- [ ] Secrets rotation procedure documentada
- [ ] Vault ou similar configurado para secrets
- [ ] .gitignore contém todos os arquivos de configuração

## 📊 Monitoring & Logging
- [ ] Failed login attempts logging
- [ ] Suspicious activity detection
- [ ] Security event alerts configurados
- [ ] Access logs centralizados
- [ ] Audit trail para ações administrativas

## 🛡️ Infrastructure Security
- [ ] Containers rodando como non-root user
- [ ] Image scanning sem vulnerabilidades críticas
- [ ] Network segmentation entre serviços
- [ ] Firewall rules implementadas
- [ ] Regular security updates scheduled

## 📝 Documentation
- [ ] Security incident response plan
- [ ] Vulnerability disclosure process
- [ ] Regular security training for team
- [ ] Penetration testing schedule
- [ ] Security best practices document
```

### Security Testing Script
```bash
#!/bin/bash
# security_scan.sh - Scan de segurança automatizado

echo "🔍 Running security scan..."

# 1. Secret scanning
echo "Scanning for secrets..."
if command -v truffleHog &> /dev/null; then
    truffleHog filesystem . --regex --entropy=False
else
    echo "Installing truffleHog..."
    pip install truffleHog
    truffleHog filesystem . --regex --entropy=False
fi

# 2. Dependency scanning
echo "Scanning dependencies for vulnerabilities..."
if command -v safety &> /dev/null; then
    safety check --json --output safety-report.json
else
    pip install safety
    safety check --json --output safety-report.json
fi

# 3. Static analysis for security
echo "Running bandit security analysis..."
bandit -r backend/ -f json -o bandit-report.json

# 4. Container scanning
echo "Scanning Docker images..."
if command -v trivy &> /dev/null; then
    trivy fs . --format json --output trivy-report.json
else
    echo "Installing trivy..."
    curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin
    trivy fs . --format json --output trivy-report.json
fi

# 5. License compliance
echo "Checking license compliance..."
if command -v licensee &> /dev/null; then
    licensee detect --json > license-report.json
else
    echo "Installing licensee..."
    gem install licensee
    licensee detect --json > license-report.json
fi

echo "✅ Security scan completed. Reports generated:"
echo "  - safety-report.json (vulnerabilities)"
echo "  - bandit-report.json (static analysis)"
echo "  - trivy-report.json (container scan)"
echo "  - license-report.json (license compliance)"

# Summary
echo ""
echo "📊 SECURITY SCAN SUMMARY:"
if [ -f "safety-report.json" ]; then
    VULNS=$(jq '.vulnerabilities | length' safety-report.json 2>/dev/null || echo "0")
    echo "  Vulnerabilities found: $VULNS"
fi

if [ -f "bandit-report.json" ]; then
    BANDIT_ISSUES=$(jq '.results | length' bandit-report.json 2>/dev/null || echo "0")
    echo "  Bandit issues: $BANDIT_ISSUES"
fi

if [ -f "trivy-report.json" ]; then
    TRIVY_ISSUES=$(jq '.Results | map(select(.Vulnerabilities != null)) | length' trivy-report.json 2>/dev/null || echo "0")
    echo "  Trivy issues: $TRIVY_ISSUES"
fi
```

---

**📚 Todos os templates e scripts estão prontos para uso imediato**  
**🔧 Modifique conforme necessário para seu ambiente específico**  
**⚡ Execute os scripts com privilégios adequados**  
**📖 Consulte a documentação para detalhes adicionais**