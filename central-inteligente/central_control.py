#!/usr/bin/env python3
"""
Central de Controle Inteligente 3dPot
Interface principal que integra Arduino, ESP32 e Raspberry Pi
Sistema de monitoramento e automação de impressão 3D
"""

import json
import logging
import os
import time
from datetime import datetime
from threading import Thread, Event
from typing import Dict, List, Optional, Any
import requests
import serial
import sqlite3
from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_socketio import SocketIO, emit

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('central_control.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CentralControlSystem:
    """Sistema central de controle que integra todos os módulos"""
    
    def __init__(self):
        self.config = self._load_config()
        self.esp32_url = self.config.get('esp32', {}).get('url', 'http://192.168.1.100')
        self.rpi_qc_url = self.config.get('rpi_qc', {}).get('url', 'http://192.168.1.101')
        self.arduino_port = self.config.get('arduino', {}).get('port', '/dev/ttyUSB0')
        self.arduino_baudrate = self.config.get('arduino', {}).get('baudrate', 9600)
        
        # Estado do sistema
        self.system_state = {
            'active': False,
            'current_mode': 'idle',  # idle, monitoring, quality_check, production
            'weight': 0.0,
            'filament_low': False,
            'conveyor_speed': 0,
            'qc_status': 'waiting',
            'last_update': None
        }
        
        # Banco de dados
        self.db_path = 'central_control.db'
        self._init_database()
        
        # Comunicação com módulos
        self.arduino_serial = None
        self.esp32_session = requests.Session()
        self.esp32_session.timeout = 5
        
        # Controle de threads
        self.running = Event()
        self.threads = []
        
    def _load_config(self) -> Dict[str, Any]:
        """Carrega configuração do sistema"""
        try:
            with open('config.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning("Config file not found, using defaults")
            return {
                'esp32': {'url': 'http://192.168.1.100', 'timeout': 5},
                'rpi_qc': {'url': 'http://192.168.1.101', 'timeout': 5},
                'arduino': {'port': '/dev/ttyUSB0', 'baudrate': 9600},
                'database': {'path': 'central_control.db'},
                'sensors': {
                    'weight_low_threshold': 100.0,  # 100g mínimo
                    'conveyor_speed_default': 50
                }
            }
    
    def _init_database(self):
        """Inicializa banco de dados"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela de logs de operação
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS operation_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                module TEXT NOT NULL,
                action TEXT NOT NULL,
                status TEXT NOT NULL,
                details TEXT,
                weight_value REAL,
                conveyor_speed INTEGER,
                qc_result TEXT
            )
        ''')
        
        # Tabela de configurações
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                parameter TEXT UNIQUE NOT NULL,
                value TEXT NOT NULL,
                description TEXT
            )
        ''')
        
        # Tabela de alertas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                level TEXT NOT NULL,  # info, warning, error, critical
                module TEXT NOT NULL,
                message TEXT NOT NULL,
                resolved BOOLEAN DEFAULT FALSE
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Database initialized")
    
    def connect_arduino(self) -> bool:
        """Estabelece conexão com Arduino"""
        try:
            self.arduino_serial = serial.Serial(
                self.arduino_port,
                self.arduino_baudrate,
                timeout=1
            )
            time.sleep(2)  # Aguardar inicialização
            logger.info(f"Arduino connected on {self.arduino_port}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Arduino: {e}")
            return False
    
    def get_esp32_status(self) -> Dict[str, Any]:
        """Obtém status do ESP32 (monitor de filamento)"""
        try:
            response = self.esp32_session.get(f"{self.esp32_url}/api/status", timeout=3)
            if response.status_code == 200:
                data = response.json()
                logger.debug(f"ESP32 status: {data}")
                return data
            else:
                logger.warning(f"ESP32 API returned status {response.status_code}")
                return {'error': 'Connection failed'}
        except Exception as e:
            logger.error(f"Error getting ESP32 status: {e}")
            return {'error': str(e)}
    
    def get_rpi_qc_status(self) -> Dict[str, Any]:
        """Obtém status do Raspberry Pi (estação QC)"""
        try:
            response = requests.get(f"{self.rpi_qc_url}/api/status", timeout=3)
            if response.status_code == 200:
                data = response.json()
                logger.debug(f"RPi QC status: {data}")
                return data
            else:
                logger.warning(f"RPi QC API returned status {response.status_code}")
                return {'error': 'Connection failed'}
        except Exception as e:
            logger.error(f"Error getting RPi QC status: {e}")
            return {'error': str(e)}
    
    def send_arduino_command(self, command: str) -> bool:
        """Envia comando para Arduino"""
        if not self.arduino_serial or not self.arduino_serial.is_open:
            logger.error("Arduino not connected")
            return False
        
        try:
            self.arduino_serial.write(f"{command}\n".encode())
            self.arduino_serial.flush()
            logger.debug(f"Sent Arduino command: {command}")
            return True
        except Exception as e:
            logger.error(f"Error sending Arduino command: {e}")
            return False
    
    def start_production_mode(self) -> bool:
        """Inicia modo de produção automatizado"""
        if not self._check_all_systems():
            logger.error("Cannot start production: not all systems ready")
            return False
        
        self.system_state['active'] = True
        self.system_state['current_mode'] = 'production'
        self._log_operation('central', 'start_production', 'success')
        
        # Iniciar threads de monitoramento
        self._start_monitoring_threads()
        
        logger.info("Production mode started")
        return True
    
    def stop_production_mode(self):
        """Para modo de produção"""
        self.system_state['active'] = False
        self.system_state['current_mode'] = 'idle'
        
        # Parar threads
        self.running.clear()
        for thread in self.threads:
            if thread.is_alive():
                thread.join(timeout=1)
        
        self._log_operation('central', 'stop_production', 'success')
        logger.info("Production mode stopped")
    
    def start_quality_check(self) -> bool:
        """Inicia processo de controle de qualidade"""
        self.system_state['current_mode'] = 'quality_check'
        self.system_state['qc_status'] = 'in_progress'
        
        try:
            # Parar esteira
            self.send_arduino_command('STOP')
            
            # Solicitar QC ao RPi
            qc_response = requests.post(
                f"{self.rpi_qc_url}/api/start_inspection",
                json={'mode': 'automated'},
                timeout=10
            )
            
            if qc_response.status_code == 200:
                self._log_operation('central', 'start_qc', 'success')
                return True
            else:
                logger.error("QC request failed")
                return False
                
        except Exception as e:
            logger.error(f"Error starting QC: {e}")
            return False
    
    def _check_all_systems(self) -> bool:
        """Verifica se todos os sistemas estão prontos"""
        esp32_ok = self.get_esp32_status().get('status') == 'ready'
        rpi_ok = self.get_rpi_qc_status().get('status') == 'ready'
        arduino_ok = self.arduino_serial and self.arduino_serial.is_open
        
        if not (esp32_ok and rpi_ok and arduino_ok):
            logger.warning(f"Systems check: ESP32={esp32_ok}, RPi={rpi_ok}, Arduino={arduino_ok}")
        
        return esp32_ok and rpi_ok and arduino_ok
    
    def _start_monitoring_threads(self):
        """Inicia threads de monitoramento"""
        self.running.set()
        
        # Thread de monitoramento ESP32
        esp32_thread = Thread(target=self._monitor_esp32, daemon=True)
        esp32_thread.start()
        self.threads.append(esp32_thread)
        
        # Thread de monitoramento RPi QC
        rpi_thread = Thread(target=self._monitor_rpi_qc, daemon=True)
        rpi_thread.start()
        self.threads.append(rpi_thread)
        
        # Thread de monitoramento geral
        general_thread = Thread(target=self._monitor_general, daemon=True)
        general_thread.start()
        self.threads.append(general_thread)
    
    def _monitor_esp32(self):
        """Monitoramento contínuo do ESP32"""
        while self.running.is_set():
            try:
                status = self.get_esp32_status()
                if 'weight' in status:
                    self.system_state['weight'] = status['weight']
                    
                    # Verificar filamento baixo
                    if status['weight'] < self.config['sensors']['weight_low_threshold']:
                        self.system_state['filament_low'] = True
                        self._create_alert('warning', 'ESP32', 
                                         f"Filament low: {status['weight']:.1f}g")
                    else:
                        self.system_state['filament_low'] = False
                
                self.system_state['last_update'] = datetime.now().isoformat()
                
            except Exception as e:
                logger.error(f"ESP32 monitoring error: {e}")
            
            time.sleep(5)  # Atualizar a cada 5 segundos
    
    def _monitor_rpi_qc(self):
        """Monitoramento contínuo do RPi QC"""
        while self.running.is_set():
            try:
                status = self.get_rpi_qc_status()
                if 'qc_status' in status:
                    self.system_state['qc_status'] = status['qc_status']
                
            except Exception as e:
                logger.error(f"RPi QC monitoring error: {e}")
            
            time.sleep(3)  # Atualizar a cada 3 segundos
    
    def _monitor_general(self):
        """Monitoramento geral do sistema"""
        while self.running.is_set():
            try:
                # Verificar conectividade geral
                if not self._check_all_systems():
                    self._create_alert('error', 'central', 'System connectivity issue')
                
                # Log de operação periódica
                self._log_operation('central', 'monitor', 'success', 
                                  weight_value=self.system_state['weight'],
                                  conveyor_speed=self.system_state['conveyor_speed'])
                
            except Exception as e:
                logger.error(f"General monitoring error: {e}")
            
            time.sleep(10)  # A cada 10 segundos
    
    def _log_operation(self, module: str, action: str, status: str, 
                      details: str = None, weight_value: float = None,
                      conveyor_speed: int = None, qc_result: str = None):
        """Registra operação no banco de dados"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO operation_logs 
            (module, action, status, details, weight_value, conveyor_speed, qc_result)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (module, action, status, details, weight_value, conveyor_speed, qc_result))
        
        conn.commit()
        conn.close()
    
    def _create_alert(self, level: str, module: str, message: str):
        """Cria alerta no sistema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO alerts (level, module, message)
            VALUES (?, ?, ?)
        ''', (level, module, message))
        
        conn.commit()
        conn.close()
        
        logger.warning(f"ALERT [{level.upper()}] {module}: {message}")
    
    def get_operation_logs(self, limit: int = 100) -> List[Dict]:
        """Obtém logs de operação"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM operation_logs 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))
        
        logs = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return logs
    
    def get_alerts(self, resolved: bool = False, limit: int = 50) -> List[Dict]:
        """Obtém alertas do sistema"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM alerts 
            WHERE resolved = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (resolved, limit))
        
        alerts = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return alerts

# Inicializar Flask e SocketIO
app = Flask(__name__)
app.config['SECRET_KEY'] = '3dpot-central-control'
socketio = SocketIO(app, cors_allowed_origins="*")

# Inicializar sistema de controle
control_system = CentralControlSystem()

@app.route('/')
def dashboard():
    """Dashboard principal"""
    return render_template('dashboard.html')

@app.route('/api/status')
def get_system_status():
    """API para status do sistema"""
    return jsonify(control_system.system_state)

@app.route('/api/start_production', methods=['POST'])
def start_production():
    """Inicia modo de produção"""
    success = control_system.start_production_mode()
    if success:
        socketio.emit('status_update', {'mode': 'production', 'active': True})
        return jsonify({'success': True, 'message': 'Production started'})
    else:
        return jsonify({'success': False, 'message': 'Failed to start production'}), 500

@app.route('/api/stop_production', methods=['POST'])
def stop_production():
    """Para modo de produção"""
    control_system.stop_production_mode()
    socketio.emit('status_update', {'mode': 'idle', 'active': False})
    return jsonify({'success': True, 'message': 'Production stopped'})

@app.route('/api/start_qc', methods=['POST'])
def start_qc():
    """Inicia controle de qualidade"""
    success = control_system.start_quality_check()
    if success:
        return jsonify({'success': True, 'message': 'QC started'})
    else:
        return jsonify({'success': False, 'message': 'Failed to start QC'}), 500

@app.route('/api/esp32/status')
def get_esp32_status():
    """Status específico do ESP32"""
    status = control_system.get_esp32_status()
    return jsonify(status)

@app.route('/api/rpiqc/status')
def get_rpiqc_status():
    """Status específico do RPi QC"""
    status = control_system.get_rpi_qc_status()
    return jsonify(status)

@app.route('/api/logs')
def get_logs():
    """Logs de operação"""
    limit = request.args.get('limit', 100, type=int)
    logs = control_system.get_operation_logs(limit)
    return jsonify(logs)

@app.route('/api/alerts')
def get_alerts():
    """Alertas do sistema"""
    resolved = request.args.get('resolved', 'false').lower() == 'true'
    limit = request.args.get('limit', 50, type=int)
    alerts = control_system.get_alerts(resolved, limit)
    return jsonify(alerts)

@app.route('/api/conveyor/speed', methods=['GET', 'POST'])
def conveyor_control():
    """Controle da velocidade da esteira"""
    if request.method == 'GET':
        return jsonify({
            'current_speed': control_system.system_state['conveyor_speed']
        })
    
    data = request.get_json()
    speed = data.get('speed', 50)  # default 50
    
    success = control_system.send_arduino_command(f'SPEED:{speed}')
    if success:
        control_system.system_state['conveyor_speed'] = speed
        return jsonify({'success': True, 'speed': speed})
    else:
        return jsonify({'success': False, 'message': 'Failed to set speed'}), 500

@socketio.on('connect')
def handle_connect():
    """Cliente conectado"""
    logger.info(f"Client connected: {request.sid}")
    # Enviar status atual
    emit('status_update', control_system.system_state)

@socketio.on('disconnect')
def handle_disconnect():
    """Cliente desconectado"""
    logger.info(f"Client disconnected: {request.sid}")

def main():
    """Função principal"""
    # Conectar Arduino
    if not control_system.connect_arduino():
        logger.warning("Arduino not connected - system will work in limited mode")
    
    # Configurar SocketIO events
    def update_status_periodically():
        while True:
            socketio.emit('status_update', control_system.system_state)
            time.sleep(2)
    
    # Iniciar thread de atualizações
    status_thread = Thread(target=update_status_periodically, daemon=True)
    status_thread.start()
    
    logger.info("Starting 3dPot Central Control System")
    logger.info(f"ESP32 URL: {control_system.esp32_url}")
    logger.info(f"RPi QC URL: {control_system.rpi_qc_url}")
    logger.info(f"Arduino Port: {control_system.arduino_port}")
    
    # Iniciar servidor Flask-SocketIO
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)

if __name__ == '__main__':
    main()