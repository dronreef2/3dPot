#!/bin/bash

# Script de inicialização do banco de dados 3dPot
# Cria tabelas, índices e dados iniciais

set -e

DB_PATH="/data/3dpot.db"

echo "Inicializando banco de dados 3dPot..."

# Função para executar SQL
execute_sql() {
    sqlite3 $DB_PATH "$1"
}

# Criar banco de dados se não existir
if [ ! -f "$DB_PATH" ]; then
    touch $DB_PATH
    echo "Banco de dados criado: $DB_PATH"
fi

# Tabela de usuários
execute_sql "
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('admin', 'operator', 'viewer')),
    is_active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
"

# Tabela de dispositivos
execute_sql "
CREATE TABLE IF NOT EXISTS devices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('esp32', 'arduino', 'raspberry_pi', 'sensor')),
    device_id TEXT UNIQUE NOT NULL,
    status TEXT NOT NULL DEFAULT 'offline' CHECK (status IN ('online', 'offline', 'error')),
    location TEXT,
    last_seen DATETIME,
    config TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
"

# Tabela de dados de sensores
execute_sql "
CREATE TABLE IF NOT EXISTS sensor_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id TEXT NOT NULL,
    sensor_type TEXT NOT NULL,
    value REAL NOT NULL,
    unit TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES devices (device_id)
);
"

# Tabela de dados de filamento
execute_sql "
CREATE TABLE IF NOT EXISTS filament_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id TEXT NOT NULL,
    weight REAL,
    temperature REAL,
    humidity REAL,
    battery_level REAL,
    status TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES devices (device_id)
);
"

# Tabela de dados da esteira
execute_sql "
CREATE TABLE IF NOT EXISTS conveyor_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id TEXT NOT NULL,
    speed REAL,
    direction TEXT,
    position REAL,
    status TEXT,
    error_code TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES devices (device_id)
);
"

# Tabela de dados da estação QC
execute_sql "
CREATE TABLE IF NOT EXISTS qc_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id TEXT NOT NULL,
    quality_grade TEXT CHECK (quality_grade IN ('A', 'B', 'C', 'D', 'F')),
    defects_detected TEXT,
    confidence REAL,
    image_path TEXT,
    processing_time REAL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES devices (device_id)
);
"

# Tabela de alertas
execute_sql "
CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id TEXT,
    type TEXT NOT NULL,
    severity TEXT NOT NULL CHECK (severity IN ('info', 'warning', 'error', 'critical')),
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES devices (device_id)
);
"

# Tabela de configurações do sistema
execute_sql "
CREATE TABLE IF NOT EXISTS system_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT UNIQUE NOT NULL,
    value TEXT NOT NULL,
    description TEXT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
"

# Tabela de logs do sistema
execute_sql "
CREATE TABLE IF NOT EXISTS system_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    level TEXT NOT NULL CHECK (level IN ('debug', 'info', 'warning', 'error')),
    message TEXT NOT NULL,
    module TEXT,
    user_id INTEGER,
    ip_address TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);
"

# Criar índices para performance
execute_sql "CREATE INDEX IF NOT EXISTS idx_sensor_data_device_timestamp ON sensor_data(device_id, timestamp);"
execute_sql "CREATE INDEX IF NOT EXISTS idx_filament_data_device_timestamp ON filament_data(device_id, timestamp);"
execute_sql "CREATE INDEX IF NOT EXISTS idx_conveyor_data_device_timestamp ON conveyor_data(device_id, timestamp);"
execute_sql "CREATE INDEX IF NOT EXISTS idx_qc_data_device_timestamp ON qc_data(device_id, timestamp);"
execute_sql "CREATE INDEX IF NOT EXISTS idx_alerts_device_created ON alerts(device_id, created_at);"
execute_sql "CREATE INDEX IF NOT EXISTS idx_logs_level_created ON system_logs(level, created_at);"

# Inserir usuários padrão
execute_sql "
INSERT OR IGNORE INTO users (username, email, password_hash, role) VALUES 
('admin', 'admin@3dpot.com', '\$2b\$10\$rOzLy2fKHKrYfHKfYL5Z3OKlFAJfJVqYjZq5F2gF1L2F3F4F5F6F7', 'admin'),
('operator', 'operator@3dpot.com', '\$2b\$10\$rOzLy2fKHKrYfHKfYL5Z3OKlFAJfJVqYjZq5F2gF1L2F3F4F5F6F8', 'operator'),
('viewer', 'viewer@3dpot.com', '\$2b\$10\$rOzLy2fKHKrYfHKfYL5Z3OKlFAJfJVqYjZq5F2gF1L2F3F4F5F6F9', 'viewer');
"

# Inserir dispositivos padrão
execute_sql "
INSERT OR IGNORE INTO devices (name, type, device_id, status, location) VALUES 
('Monitor de Filamento ESP32', 'esp32', 'esp32_001', 'offline', 'Impressora 3D #1'),
('Esteira Transportadora Arduino', 'arduino', 'arduino_001', 'offline', 'Linha de Produção'),
('Estação QC Raspberry Pi', 'raspberry_pi', 'rpi_001', 'offline', 'Ponto de Controle de Qualidade'),
('Sensor de Temperatura DHT22', 'sensor', 'sensor_temp_001', 'offline', 'Monitoramento Ambiental');
"

# Inserir configurações padrão do sistema
execute_sql "
INSERT OR IGNORE INTO system_config (key, value, description) VALUES 
('system_name', '3dPot Control Center', 'Nome do sistema'),
('api_version', '1.0.0', 'Versão da API'),
('max_filament_weight', '1000', 'Peso máximo do filamento em gramos'),
('min_battery_level', '20', 'Nível mínimo de bateria em porcentagem'),
('qc_confidence_threshold', '80', 'Threshold de confiança para classificação QC'),
('alert_email_enabled', 'false', 'Habilitar envio de alertas por email'),
('data_retention_days', '90', 'Dias para manter dados históricos'),
('backup_enabled', 'true', 'Habilitar backups automáticos'),
('maintenance_mode', 'false', 'Modo de manutenção do sistema');
"

# Inserir dados de exemplo (para demonstração)
execute_sql "
INSERT INTO sensor_data (device_id, sensor_type, value, unit) VALUES 
('sensor_temp_001', 'temperature', '23.5', '°C'),
('sensor_temp_001', 'humidity', '45.2', '%'),
('esp32_001', 'weight', '750.5', 'g'),
('esp32_001', 'battery', '85.0', '%');
"

execute_sql "
INSERT INTO filament_data (device_id, weight, temperature, humidity, battery_level, status) VALUES 
('esp32_001', 750.5, 23.5, 45.2, 85.0, 'ok');
"

execute_sql "
INSERT INTO conveyor_data (device_id, speed, direction, position, status) VALUES 
('arduino_001', 0.5, 'forward', 125.3, 'idle');
"

execute_sql "
INSERT INTO qc_data (device_id, quality_grade, defects_detected, confidence, processing_time) VALUES 
('rpi_001', 'A', 'none', 95.2, 1.25);
"

# Inserir alguns alertas de exemplo
execute_sql "
INSERT INTO alerts (device_id, type, severity, message) VALUES 
('esp32_001', 'low_battery', 'warning', 'Nível de bateria baixo (15%)'),
('arduino_001', 'disconnect', 'error', 'Dispositivo desconectado'),
('rpi_001', 'high_defect_rate', 'warning', 'Taxa de defeitos acima do normal');
"

# Criar views úteis
execute_sql "
CREATE VIEW IF NOT EXISTS device_status_summary AS
SELECT 
    d.device_id,
    d.name,
    d.type,
    d.status,
    d.location,
    d.last_seen,
    CASE 
        WHEN d.type = 'esp32' THEN (SELECT weight FROM filament_data WHERE device_id = d.device_id ORDER BY timestamp DESC LIMIT 1)
        WHEN d.type = 'arduino' THEN (SELECT speed FROM conveyor_data WHERE device_id = d.device_id ORDER BY timestamp DESC LIMIT 1)
        WHEN d.type = 'raspberry_pi' THEN (SELECT quality_grade FROM qc_data WHERE device_id = d.device_id ORDER BY timestamp DESC LIMIT 1)
        ELSE NULL
    END as latest_value
FROM devices d;
"

execute_sql "
CREATE VIEW IF NOT EXISTS recent_alerts AS
SELECT 
    a.id,
    d.name as device_name,
    a.type,
    a.severity,
    a.message,
    a.created_at
FROM alerts a
LEFT JOIN devices d ON a.device_id = d.device_id
WHERE a.is_read = 0
ORDER BY a.created_at DESC
LIMIT 20;
"

# Definir permissões corretas
chmod 644 $DB_PATH
chown 1001:1001 $DB_PATH

echo "Banco de dados inicializado com sucesso!"
echo ""
echo "Usuários criados:"
echo "- admin / admin123 (admin)"
echo "- operator / operator123 (operator)"
echo "- viewer / viewer123 (viewer)"
echo ""
echo "Dispositivos configurados:"
echo "- Monitor de Filamento ESP32 (esp32_001)"
echo "- Esteira Transportadora Arduino (arduino_001)"
echo "- Estação QC Raspberry Pi (rpi_001)"
echo "- Sensor de Temperatura (sensor_temp_001)"
echo ""
echo "O banco de dados está pronto para uso!"