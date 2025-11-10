#!/bin/bash
# 3dPot Hardware Integration Test Suite
# Testa a integração com hardware real e simula dispositivos

echo "🧪 3dPot Hardware Integration Test Suite"
echo "========================================"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para print colorido
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Verificar dependências
check_dependencies() {
    echo -e "\n${BLUE}Verificando dependências...${NC}"
    
    # Verificar Node.js
    if command -v node &> /dev/null; then
        print_status "Node.js $(node --version) instalado"
    else
        print_error "Node.js não encontrado"
        exit 1
    fi
    
    # Verificar npm
    if command -v npm &> /dev/null; then
        print_status "npm $(npm --version) instalado"
    else
        print_error "npm não encontrado"
        exit 1
    fi
    
    # Verificar Python (para Raspberry Pi simulation)
    if command -v python3 &> /dev/null; then
        print_status "Python3 $(python3 --version) instalado"
    else
        print_warning "Python3 não encontrado (necessário para simulação Raspberry Pi)"
    fi
}

# Instalar dependências
install_dependencies() {
    echo -e "\n${BLUE}Instalando dependências...${NC}"
    
    # Backend
    if [ -d "server" ]; then
        print_info "Instalando dependências do backend..."
        cd server
        npm install
        cd ..
        print_status "Dependências do backend instaladas"
    else
        print_error "Diretório server não encontrado"
        return 1
    fi
    
    # Frontend
    if [ -d "../interface-web" ]; then
        print_info "Instalando dependências do frontend..."
        cd ../interface-web
        npm install
        cd server
        print_status "Dependências do frontend instaladas"
    else
        print_warning "Diretório frontend não encontrado"
    fi
}

# Configurar ambiente de teste
setup_test_environment() {
    echo -e "\n${BLUE}Configurando ambiente de teste...${NC}"
    
    # Criar diretório de logs
    mkdir -p logs
    
    # Configurar arquivo .env para testes
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            print_status "Arquivo .env criado a partir do exemplo"
            
            # Configurações específicas para testes
            sed -i 's/ESP32_ENABLED=true/ESP32_ENABLED=false/' .env
            sed -i 's/ARDUINO_ENABLED=true/ARDUINO_ENABLED=false/' .env
            sed -i 's/RASPBERRY_PI_ENABLED=true/RASPBERRY_PI_ENABLED=false/' .env
            print_info "Dispositivos desabilitados para modo simulação"
        else
            print_warning "Arquivo .env.example não encontrado"
        fi
    else
        print_status "Arquivo .env já existe"
    fi
}

# Teste de conectividade da API
test_api_connectivity() {
    echo -e "\n${BLUE}Testando conectividade da API...${NC}"
    
    # Iniciar servidor em background
    print_info "Iniciando servidor backend..."
    npm run dev &
    SERVER_PID=$!
    
    # Aguardar servidor inicializar
    sleep 5
    
    # Testar health check
    if curl -s http://localhost:5000/api/health > /dev/null; then
        print_status "API respondendo em http://localhost:5000"
    else
        print_error "API não está respondendo"
        kill $SERVER_PID 2>/dev/null
        return 1
    fi
    
    # Testar WebSocket
    if command -v node &> /dev/null; then
        print_info "Testando WebSocket..."
        # Simular conexão WebSocket
        timeout 5s node -e "
            const io = require('socket.io-client');
            const socket = io('http://localhost:5000');
            socket.on('connect', () => {
                console.log('WebSocket conectado');
                process.exit(0);
            });
            socket.on('connect_error', (error) => {
                console.log('Erro WebSocket:', error.message);
                process.exit(1);
            });
            setTimeout(() => {
                console.log('Timeout WebSocket');
                process.exit(1);
            }, 3000);
        " && print_status "WebSocket funcionando" || print_error "WebSocket com problemas"
    fi
    
    # Parar servidor
    kill $SERVER_PID 2>/dev/null
    print_info "Servidor parado"
}

# Simulador de dispositivos ESP32
simulate_esp32() {
    echo -e "\n${BLUE}Simulador ESP32 Monitor de Filamento${NC}"
    
    # Criar simulador simples
    cat > esp32_simulator.js << 'EOF'
const mqtt = require('mqtt');

const client = mqtt.connect('mqtt://localhost:1883', {
    clientId: '3dpot_esp32_simulator'
});

client.on('connect', () => {
    console.log('ESP32 Simulator conectado ao MQTT');
    
    // Publicar status inicial
    client.publish('3dpot/filament/status', JSON.stringify({
        weight: 800,
        temperature: 22.5,
        batteryLevel: 85,
        isSleeping: false
    }));
    
    // Simular atualizações a cada 10 segundos
    setInterval(() => {
        const data = {
            weight: Math.random() * 200 + 700,
            temperature: Math.random() * 10 + 20,
            humidity: Math.random() * 20 + 40,
            batteryLevel: Math.random() * 20 + 75,
            isSleeping: Math.random() > 0.9,
            uptime: Date.now(),
            wifiSignal: -45 + Math.random() * 20,
            memoryUsage: Math.random() * 30 + 10
        };
        
        client.publish('3dpot/filament/data', JSON.stringify(data));
        console.log('Dados ESP32 publicados:', data.weight.toFixed(1), 'g');
    }, 10000);
});

client.on('message', (topic, message) => {
    console.log('Comando recebido:', topic, message.toString());
    
    if (topic === '3dpot/filament/command') {
        const command = JSON.parse(message.toString());
        client.publish('3dpot/filament/response', JSON.stringify({
            commandId: command.id,
            success: true,
            result: 'Comando executado',
            timestamp: new Date().toISOString()
        }));
    }
});

client.on('error', (error) => {
    console.error('Erro MQTT:', error.message);
});
EOF
    
    print_info "Simulador ESP32 criado (esp32_simulator.js)"
    print_info "Execute: node esp32_simulator.js"
}

# Simulador de dispositivo Arduino
simulate_arduino() {
    echo -e "\n${BLUE}Simulador Arduino Esteira Transportadora${NC}"
    
    # Criar simulador simples via HTTP
    cat > arduino_simulator.py << 'EOF'
import json
import time
import random
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

class ArduinoSimulator(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/status':
            status = {
                'state': random.choice(['IDLE', 'RUNNING', 'PAUSED']),
                'speed': random.randint(0, 200),
                'mode': random.choice(['manual', 'automatic']),
                'totalPieces': random.randint(0, 1000),
                'totalRuntime': random.randint(0, 3600),
                'errorCount': random.randint(0, 5)
            }
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(status).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        if self.path == '/control':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            command = json.loads(post_data.decode())
            
            print(f"Comando Arduino recebido: {command}")
            
            response = {
                'success': True,
                'message': 'Comando executado',
                'timestamp': time.time()
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        print(f"[Arduino] {format % args}")

if __name__ == '__main__':
    server = HTTPServer(('localhost', 8080), ArduinoSimulator)
    print("Simulador Arduino executando em http://localhost:8080")
    server.serve_forever()
EOF
    
    print_info "Simulador Arduino criado (arduino_simulator.py)"
    print_info "Execute: python3 arduino_simulator.py"
}

# Simulador Raspberry Pi QC
simulate_raspberry_pi() {
    echo -e "\n${BLUE}Simulador Raspberry Pi Estação QC${NC}"
    
    # Criar simulador Flask
    cat > qc_simulator.py << 'EOF'
import json
import time
import random
from flask import Flask, jsonify
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'qc-simulator-secret'
socketio = SocketIO(app, cors_allowed_origins="*")

# Simulação de dados
pieces_analyzed = 0
avg_processing_time = 2.5

@app.route('/api/status')
def get_status():
    return jsonify({
        'camera_status': True,
        'led_status': 'on',
        'database_status': True,
        'cpu_usage': random.uniform(20, 80),
        'memory_usage': random.uniform(30, 70),
        'disk_usage': random.uniform(40, 90),
        'pieces_analyzed': pieces_analyzed,
        'avg_processing_time': avg_processing_time,
        'last_analysis': time.time()
    })

@app.route('/api/statistics')
def get_statistics():
    return jsonify({
        'total_inspections': pieces_analyzed,
        'quality_distribution': {
            'A': random.randint(20, 50),
            'B': random.randint(15, 30),
            'C': random.randint(5, 15),
            'D': random.randint(0, 5),
            'F': random.randint(0, 3)
        },
        'avg_confidence': random.uniform(0.7, 0.95),
        'defect_rate': random.uniform(0.05, 0.25)
    })

@socketio.on('connect')
def handle_connect():
    print('Cliente QC conectado')
    emit('status', {'message': 'QC Simulator conectado'})

@socketio.on('command')
def handle_command(data):
    print(f"Comando QC recebido: {data}")
    emit('response', {
        'commandId': data.get('id'),
        'success': True,
        'result': 'Comando executado',
        'timestamp': time.time()
    })

# Simular inspeções
def simulate_inspections():
    global pieces_analyzed, avg_processing_time
    
    while True:
        time.sleep(15)  # Nova inspeção a cada 15 segundos
        
        result = {
            'piece_id': f'piece_{pieces_analyzed:04d}',
            'quality_class': random.choices(['A', 'B', 'C', 'D', 'F'], 
                                          weights=[30, 25, 20, 15, 10])[0],
            'confidence': random.uniform(0.6, 0.99),
            'defects_found': random.sample(['warping', 'layer_shift', 'stringing'], 
                                         random.randint(0, 2)),
            'area': random.uniform(1000, 5000),
            'aspect_ratio': random.uniform(0.8, 1.5),
            'contrast': random.uniform(30, 80),
            'processing_time': random.uniform(1.0, 5.0)
        }
        
        pieces_analyzed += 1
        avg_processing_time = (avg_processing_time + result['processing_time']) / 2
        
        socketio.emit('inspection_result', result)
        print(f"Inspeção simulada: {result['piece_id']} - Classe {result['quality_class']}")

if __name__ == '__main__':
    import threading
    
    # Iniciar thread de simulação
    simulation_thread = threading.Thread(target=simulate_inspections, daemon=True)
    simulation_thread.start()
    
    print("Simulador QC executando em http://localhost:5001")
    socketio.run(app, port=5001, debug=False)
EOF
    
    print_info "Simulador Raspberry Pi QC criado (qc_simulator.py)"
    print_info "Execute: pip install flask flask-socketio && python3 qc_simulator.py"
}

# Teste de integração completa
test_full_integration() {
    echo -e "\n${BLUE}Teste de Integração Completa${NC}"
    
    print_info "Iniciando servidores de simulação..."
    
    # Iniciar simulador QC
    python3 qc_simulator.py &
    QC_PID=$!
    
    sleep 3
    
    # Iniciar backend
    npm run dev &
    BACKEND_PID=$!
    
    sleep 5
    
    # Testar endpoints
    print_info "Testando endpoints..."
    
    # Health check
    if curl -s http://localhost:5000/api/health | grep -q "healthy"; then
        print_status "Backend health check OK"
    else
        print_error "Backend health check FALHOU"
    fi
    
    # Status de dispositivos
    if curl -s http://localhost:5000/api/devices | grep -q "esp32\|arduino\|raspberry"; then
        print_status "API de dispositivos respondendo"
    else
        print_error "API de dispositivos com problemas"
    fi
    
    # Auth health
    if curl -s http://localhost:5000/api/auth/health | grep -q "healthy"; then
        print_status "Serviço de autenticação OK"
    else
        print_error "Serviço de autenticação com problemas"
    fi
    
    print_info "Testes de integração concluídos"
    print_info "Para parar os servidores: kill $BACKEND_PID $QC_PID"
}

# Limpeza
cleanup() {
    echo -e "\n${BLUE}Limpando arquivos de teste...${NC}"
    
    # Remover simuladores
    rm -f esp32_simulator.js arduino_simulator.py qc_simulator.py
    
    # Limpar processos em background
    pkill -f "node.*dev" 2>/dev/null || true
    pkill -f "python.*qc_simulator" 2>/dev/null || true
    pkill -f "arduino_simulator" 2>/dev/null || true
    
    print_status "Limpeza concluída"
}

# Menu principal
show_menu() {
    echo -e "\n${BLUE}=== Menu de Testes ===${NC}"
    echo "1) Verificar dependências"
    echo "2) Instalar dependências"
    echo "3) Configurar ambiente de teste"
    echo "4) Testar conectividade da API"
    echo "5) Simulador ESP32"
    echo "6) Simulador Arduino"
    echo "7) Simulador Raspberry Pi QC"
    echo "8) Teste de integração completa"
    echo "9) Executar todos os testes"
    echo "0) Sair"
    echo -n "Escolha uma opção: "
}

# Loop principal
main() {
    while true; do
        show_menu
        read choice
        
        case $choice in
            1) check_dependencies ;;
            2) install_dependencies ;;
            3) setup_test_environment ;;
            4) test_api_connectivity ;;
            5) simulate_esp32 ;;
            6) simulate_arduino ;;
            7) simulate_raspberry_pi ;;
            8) test_full_integration ;;
            9) 
                check_dependencies
                install_dependencies
                setup_test_environment
                test_api_connectivity
                test_full_integration
                ;;
            0) 
                cleanup
                echo "Testes finalizados!"
                exit 0
                ;;
            *) 
                print_error "Opção inválida"
                ;;
        esac
        
        echo -e "\nPressione Enter para continuar..."
        read
    done
}

# Verificar se está no diretório correto
if [ ! -f "package.json" ] || [ ! -f "index.js" ]; then
    print_error "Execute este script no diretório server/"
    exit 1
fi

# Iniciar
main
